import io


class BytesBufferIO(io.BytesIO):
    def __init__(self, *args, **kwargs):
        self._value = None
        super().__init__(*args, **kwargs)

    def getvalue(self):
        if self._value is not None:
            return self._value
        return super().getvalue()

    def close(self):
        self._value = super().getvalue()
        super().close()
