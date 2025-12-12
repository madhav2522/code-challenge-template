"""Small utility helpers."""

def chunked(iterable, n):
    """Yield chunks of size n from iterable."""
    chunk = []
    for x in iterable:
        chunk.append(x)
        if len(chunk) == n:
            yield chunk
            chunk = []
    if chunk:
        yield chunk

