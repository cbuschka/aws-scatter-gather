def is_s3_test_event(event):
    return event.get("Event", None) == "s3:TestEvent"


def get_s3_objects(event):
    records = event.get("Records", [])
    return [(record["s3"]["bucket"]["name"], record["s3"]["object"]["key"],) for record in records]


def get_single_s3_object(event):
    s3_objects = get_s3_objects(event)
    if len(s3_objects) == 0:
        return None
    if len(s3_objects) > 1:
        raise ValueError("Muliple s3 objects present.")
    return s3_objects[0]
