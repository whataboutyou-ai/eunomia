import asyncio
from typing import Awaitable, Callable, List, TypeVar

T = TypeVar("T")
R = TypeVar("R")


class BatchProcessor:
    """
    Utility class for processing items with controlled concurrency to manage resource usage.
    """

    def __init__(self, batch_size: int = 10):
        self._batch_size = batch_size
        self._semaphore = asyncio.Semaphore(batch_size)

    async def run(
        self, items: List[T], processor: Callable[[T], Awaitable[R]]
    ) -> List[R]:
        """
        Process a list of items with controlled concurrency.

        Uses semaphore to limit concurrent operations while maintaining input order.

        Parameters
        ----------
        items : List[T]
            The items to process
        processor : Callable[[T], Awaitable[R]]
            Async function to process each item

        Returns
        -------
        List[R]
            Results in the same order as input items
        """

        async def bounded_processor(item: T) -> R:
            async with self._semaphore:
                return await processor(item)

        return await asyncio.gather(*[bounded_processor(item) for item in items])
