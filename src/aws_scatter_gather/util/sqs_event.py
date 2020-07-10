import json


def get_bodies(event):
    return [json.loads(e["body"]) for e in event.get("Records", [])]


def get_single_body(event):
    bodies = get_bodies(event)
    if len(bodies) == 0:
        return None
    if len(bodies) > 1:
        raise ValueError("More than single records.")
    return bodies[0]
