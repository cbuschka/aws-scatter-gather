from jsonschema import validate

_REQUEST_TYPE_SCHEMA = {
    "type": "object",
    "required": ["itemNo", "price"],
    "properties": {
        "itemNo": {
            "type": "string"
        },
        "price": {
            "type": "number"
        }
    }
}

_INPUT_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "records": {
            "type": "array",
            "items": {"$ref": "#/definitions/request"}
        }
    },
    "required": ["records"],

    "definitions": {
        "request": _REQUEST_TYPE_SCHEMA
    }
}

_RESPONSE_TYPE_SCHEMA = {
    "type": "object",
    "required": ["success", "message"],
    "properties": {
        "success": {
            "type": "boolean"
        },
        "message": {
            "type": "string"
        }
    }
}

_PENDING_TASK_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "batchId": {
            "type": "string"
        },
        "index": {
            "type": "number"
        },
        "request": {"$ref": "#/definitions/request"}
    },
    "required": ["batchId", "index", "request"],

    "definitions": {
        "request": _REQUEST_TYPE_SCHEMA
    }
}

_PENDING_CHUNK_OF_TASKS_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "batchId": {
            "type": "string"
        },
        "index": {
            "type": "number"
        },
        "records": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "index": {"type": "number"},
                    "request": {"$ref": "#/definitions/request"},
                },
                "required": ["index", "request"],
            }
        }
    },
    "required": ["batchId", "index"],

    "definitions": {
        "request": _REQUEST_TYPE_SCHEMA
    }
}

_PROCESSED_TASK_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "batchId": {
            "type": "string"
        },
        "index": {
            "type": "number"
        },
        "request": {"$ref": "#/definitions/request"},
        "response": {"$ref": "#/definitions/response"},
    },
    "required": ["batchId", "index", "request", "response"],

    "definitions": {
        "request": _REQUEST_TYPE_SCHEMA,
        "response": _RESPONSE_TYPE_SCHEMA
    }
}

_PROCESSED_CHUNK_OF_TASKS_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "batchId": {
            "type": "string"
        },
        "index": {
            "type": "number"
        },
        "records": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "index": {"type": "number"},
                    "request": {"$ref": "#/definitions/request"},
                    "response": {"$ref": "#/definitions/response"},
                },
                "required": ["index", "request", "response"],
            }
        }
    },
    "required": ["batchId", "index", "records"],

    "definitions": {
        "request": _REQUEST_TYPE_SCHEMA,
        "response": _RESPONSE_TYPE_SCHEMA
    }
}


def validate_input(doc):
    validate(instance=doc, schema=_INPUT_SCHEMA)


def validate_pending_task(doc):
    validate(instance=doc, schema=_PENDING_TASK_SCHEMA)


def validate_processed_task(doc):
    validate(instance=doc, schema=_PENDING_TASK_SCHEMA)


def validate_pending_chunk_of_tasks(doc):
    validate(instance=doc, schema=_PENDING_CHUNK_OF_TASKS_SCHEMA)


def validate_processed_chunk_of_tasks(doc):
    validate(instance=doc, schema=_PROCESSED_CHUNK_OF_TASKS_SCHEMA)
