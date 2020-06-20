import json
from enum import Enum


class _State(Enum):
    INITIAL = 0
    OBJECT_STARTED = 1
    OBJECT_PROPERTY_STARTED = 2
    OBJECT_PROPERTY_AFTER_NAME = 3
    OBJECT_PROPERTY_AFTER_VALUE = 4
    ARRAY_STARTED = 5
    ARRAY_AFTER_VALUE = 6
    DONE = 7


class JsonStream(object):
    def __init__(self, fp, encoder: json.JSONEncoder = None, indent=None, separators=None):
        self._state = []
        self._fp = fp
        self._indent = indent
        if separators is not None:
            self._item_separator, self._key_separator = separators
        elif indent is not None:
            self._item_separator = ','
        else:
            self._item_separator, self._key_separator = (', ', ': ')
        self._encoder = encoder or json.JSONEncoder(indent=self._indent,
                                                    separators=(self._item_separator, self._key_separator))
        self._push_state(_State.INITIAL)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        self.close()

    def start_array(self):
        if self._is_state(_State.INITIAL):
            self._fp.write("[")
            self._write_indent()
            self._set_state(_State.DONE)
            self._push_state(_State.ARRAY_STARTED)
        elif self._is_state(_State.OBJECT_PROPERTY_AFTER_NAME):
            self._fp.write("[")
            self._write_indent()
            self._set_state(_State.OBJECT_PROPERTY_AFTER_VALUE)
            self._push_state(_State.ARRAY_STARTED)
        else:
            self._fail("start array")

    def end_array(self):
        if self._is_state(_State.ARRAY_STARTED, _State.ARRAY_AFTER_VALUE):
            self._fp.write("]")
            self._pop_state()
        else:
            self._fail("end array")

    def start_object(self):
        if self._is_state(_State.INITIAL):
            self._fp.write("{")
            self._write_indent()
            self._set_state(_State.DONE)
            self._push_state(_State.OBJECT_STARTED)
        elif self._is_state(_State.OBJECT_PROPERTY_AFTER_NAME):
            self._fp.write("{")
            self._write_indent()
            self._set_state(_State.OBJECT_PROPERTY_AFTER_VALUE)
            self._push_state(_State.OBJECT_STARTED)
        elif self._is_state(_State.ARRAY_STARTED):
            self._fp.write("{")
            self._write_indent()
            self._set_state(_State.ARRAY_AFTER_VALUE)
            self._push_state(_State.OBJECT_STARTED)
        elif self._is_state(_State.ARRAY_AFTER_VALUE):
            self._fp.write("{}{{".format(self._item_separator))
            self._write_indent()
            self._set_state(_State.ARRAY_AFTER_VALUE)
            self._push_state(_State.OBJECT_STARTED)
        else:
            self._fail("start object")

    def start_property(self, name):
        if self._is_state(_State.OBJECT_PROPERTY_AFTER_VALUE):
            self._fp.write("{}\"{}\"{}".format(self._item_separator, name, self._key_separator))
            self._set_state(_State.OBJECT_PROPERTY_AFTER_NAME)
        elif self._is_state(_State.OBJECT_STARTED):
            self._fp.write("\"{}\"{}".format(name, self._key_separator))
            self._set_state(_State.OBJECT_PROPERTY_AFTER_NAME)
        else:
            self._fail("start property")

    def write_property(self, name, value):
        self.start_property(name)
        self.write_value(value)

    def write_value(self, value):
        if self._is_state(_State.INITIAL):
            self._fp.write(self._encoder.encode(value))
            self._set_state(_State.DONE)
        elif self._is_state(_State.OBJECT_PROPERTY_AFTER_NAME):
            self._fp.write(self._encoder.encode(value))
            self._set_state(_State.OBJECT_PROPERTY_AFTER_VALUE)
        elif self._is_state(_State.ARRAY_AFTER_VALUE):
            self._fp.write("{}{}".format(self._item_separator, self._encoder.encode(value)))
        elif self._is_state(_State.ARRAY_STARTED):
            self._fp.write(self._encoder.encode(value))
            self._set_state(_State.ARRAY_AFTER_VALUE)
        else:
            self._fail("value")

    def end_object(self):
        if self._is_state(_State.OBJECT_PROPERTY_AFTER_VALUE, _State.OBJECT_STARTED):
            self._fp.write("}")
            self._pop_state()
        else:
            self._fail("end object")

    def flush(self):
        self._fp.flush()

    def close(self):
        self._fp.flush()
        self._fp.close()

    def _push_state(self, state):
        self._state.append(state)

    def _pop_state(self):
        return self._state.pop()

    def _is_state(self, *states):
        return self._state[-1] in states

    def _set_state(self, state):
        self._state[-1] = state

    def _peek_state(self):
        return self._state[-1]

    def _fail(self, op_name):
        raise ValueError("Invalid state for {}: {}".format(op_name, self._peek_state()))

    def _write_indent(self):
        if self._indent is None:
            return
        else:
            self._fp.write("\n")
