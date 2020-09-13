import asyncio
import gzip
import io
from math import ceil

from bytesbufio import BytesBufferIO

from aws_scatter_gather.measurement.measurement_recorder import record_batch_finished, record_gather_started
from aws_scatter_gather.s3_sqs_lambda_async_chunked.resources import work_bucket, output_bucket
from aws_scatter_gather.util import aioaws
from aws_scatter_gather.util import json
from aws_scatter_gather.util import logger
from aws_scatter_gather.util.aioaws import enable_xray
from aws_scatter_gather.util.async_util import async_to_sync
from aws_scatter_gather.util.enumchunks import enumchunks
from aws_scatter_gather.util.jsonstream import JsonStream
from aws_scatter_gather.util.trace import trace

enable_xray()

logger.configure(name=__name__)


@async_to_sync
async def handle_event(event, lambda_context):
    logger.info("Event: {}".format(json.dumps(event, indent=2)))

    async with aioaws.resource("s3") as s3_resource, aioaws.client("s3") as s3_client:
        records = [json.loads(record["body"]) for record in event["Records"]]
        await asyncio.gather(*[__gather(record, s3_resource, s3_client) for record in records])


async def __gather(record, s3_resource, s3_client):
    batch_id = record["batchId"]
    record_gather_started(batch_id)
    async with trace("Gathering results for batch batch_id={}", batch_id):
        status = await work_bucket.read_batch_status(batch_id, s3_resource)
        chunk_count = ceil(status["taskCount"] / status["chunkSize"])

        bufstream = BytesBufferIO()
        jsonstream = JsonStream(
            fp=io.TextIOWrapper(gzip.GzipFile(fileobj=bufstream, mode='wb'), write_through=True, encoding='utf-8'))
        jsonstream.start_object()
        for key, value in status.items():
            jsonstream.write_property(key, value)
        jsonstream.start_property("records")
        jsonstream.start_array()
        for _, chunks in enumchunks(range(chunk_count), 10):
            chunk_results = await asyncio.gather(
                *[work_bucket.read_chunk_result(batch_id, index, s3_resource) for index in chunks])
            for chunk_result in chunk_results:
                for record in chunk_result["records"]:
                    jsonstream.write_value(record)
        jsonstream.end_array()
        jsonstream.end_object()
        jsonstream.close()
        json_bytes = bufstream.getvalue()
        await output_bucket.upload_batch_output(batch_id, gzip.GzipFile(fileobj=io.BytesIO(json_bytes), mode='rb'),
                                                s3_client)

        # await work_bucket.delete_batch_status(batch_id)
        record_batch_finished(batch_id)
