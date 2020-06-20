def enumchunks(items, chunk_size):
    buf = []
    index = 0
    for item in items:
        buf.append(item)
        if len(buf) >= chunk_size:
            yield index, buf
            index += 1
            buf = []

    if len(buf) > 0:
        yield index, buf
