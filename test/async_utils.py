async def collect(async_iterable):
    return [item async for item in async_iterable]


async def first(async_iterable):
    async for item in async_iterable:
        return item
    raise AssertionError("Expected at least one item")
