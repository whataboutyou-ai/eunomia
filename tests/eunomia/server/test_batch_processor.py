import asyncio

import pytest

from eunomia.utils.batch_processor import BatchProcessor


@pytest.mark.asyncio
async def test_batch_processor_processes_items():
    processor = BatchProcessor(batch_size=3)

    async def mock_processor(item):
        return item * 2

    items = [1, 2, 3, 4, 5, 6, 7]
    results = await processor.run(items, mock_processor)

    assert results == [2, 4, 6, 8, 10, 12, 14]


@pytest.mark.asyncio
async def test_batch_processor_empty_list():
    processor = BatchProcessor(batch_size=3)

    async def mock_processor(item):
        return item * 2

    results = await processor.run([], mock_processor)
    assert results == []


@pytest.mark.asyncio
async def test_batch_processor_maintains_order():
    processor = BatchProcessor(batch_size=2)

    async def mock_processor(item):
        await asyncio.sleep(0.01 if item % 2 == 0 else 0.02)
        return item * 10

    items = [1, 2, 3, 4, 5]
    results = await processor.run(items, mock_processor)

    assert results == [10, 20, 30, 40, 50]


@pytest.mark.asyncio
async def test_batch_processor_concurrency_limit():
    processor = BatchProcessor(batch_size=2)
    concurrent_count = 0
    max_concurrent = 0

    async def mock_processor(item):
        nonlocal concurrent_count, max_concurrent
        concurrent_count += 1
        max_concurrent = max(max_concurrent, concurrent_count)
        await asyncio.sleep(0.1)
        concurrent_count -= 1
        return item

    items = [1, 2, 3, 4, 5]
    await processor.run(items, mock_processor)

    assert max_concurrent <= 2
