# Links

## python
* https://docs.quantifiedcode.com/python-anti-patterns

## asyncio in python
* https://realpython.com/async-io-python
* https://stackoverflow.com/questions/50190480/limit-number-of-concurrent-requests-aiohttp

## aws lambda asyncio
* https://read.acloud.guru/save-time-and-money-with-aws-lambda-using-asynchronous-programming-3548ea65f751
* https://stackoverflow.com/questions/43600676/what-is-the-correct-way-to-write-asyncio-code-for-use-with-aws-lambda
* https://www.trek10.com/blog/aws-lambda-python-asyncio

## aws lambda destinations
* https://www.trek10.com/blog/lambda-destinations-what-we-learned-the-hard-way

## misc
* https://aws.amazon.com/blogs/aws/new-amazon-s3-batch-operations/
* how to choose cpu/memory - https://lumigo.io/aws-lambda-performance-optimization/
* setup time for lambda because of eni - https://aws.amazon.com/blogs/compute/announcing-improved-vpc-networking-for-aws-lambda-functions/
* https://engineering.opsgenie.com/aws-lambda-performance-series-part-1-performance-analysis-on-aws-lambda-calls-and-cold-start-98984cdf4fe0
* https://docs.aws.amazon.com/xray/latest/devguide/scorekeep-lambda.html
* https://github.com/hashicorp/terraform/issues/7854
* http://www.hydrogen18.com/blog/aws-s3-event-notifications-probably-once.html - s3 events have "probably once" semantics
* https://www.amazonaws.cn/en/lambda/faqs/ "Q: What happens if my function fails while processing an event?" -
"For Amazon S3 bucket notifications and custom events, AWS Lambda will attempt execution of your function three times in the event of an error condition in your code or if you exceed a service or resource limit. For ordered event sources that AWS Lambda polls on your behalf, such as Amazon DynamoDB Streams and Amazon Kinesis streams, Lambda will continue attempting execution in the event of a developer code error until the data expires. "
* http://docs.aws.amazon.com/lambda/latest/dg/lambda-introduction-function.html#resource-model - lambda resource model

## s3 performance
* https://aws.amazon.com/blogs/aws/amazon-s3-performance-tips-tricks-seattle-hiring-event/
* https://stackoverflow.com/questions/43035449/add-a-random-prefix-to-the-key-names-to-improve-s3-performance
* https://www.sumologic.com/insight/10-things-might-not-know-using-s3/
* https://www.infoq.com/news/2018/10/amazon-s3-performance-increase/
* https://www.lastweekinaws.com/blog/s3-is-faster-doesnt-do-it-justice/
* https://jayendrapatil.com/aws-s3-best-practices/
* https://www.trek10.com/blog/leveraging-ulids-to-create-order-in-unordered-datastores

## packaging boto3
* https://www.serverlessops.io/blog/aws-lambda-and-python-boto3-bundling

## enterprise support
* https://www.lastweekinaws.com/blog/how-to-properly-engage-with-aws-enterprise-support/
