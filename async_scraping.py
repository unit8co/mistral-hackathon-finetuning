import asyncio
from asyncio import Semaphore
import aiohttp

import logging
from aiohttp import ClientSession

from typing import Optional

MAX_CONCURRENT_REQUESTS = 10

logger = logging.getLogger(__name__)


async def fetch(session: ClientSession, url: str) -> Optional[str]:
    try:
        async with session.get(url) as response:
            if response.status != 200:
                logger.error(f"Error when query url {url}, {response}")
            return await response.text()

    except Exception as e:
        # Handle any exceptions that might occur
        logger.error(f"Expect when fetching url {url} {e}")
        return None


async def rate_limited_fetch(
    rate_limit_semaphore: Semaphore, session: ClientSession, url: str
):
    """ """
    # Limits the number of simultaneous requests
    async with rate_limit_semaphore:
        return await fetch(session, url)


async def fetch_urls(urls):
    # Maximum number of concurrent requests
    semaphore = Semaphore(MAX_CONCURRENT_REQUESTS)

    async with aiohttp.ClientSession() as session:
        # Prepare the list of tasks
        tasks = [rate_limited_fetch(semaphore, session, url) for url in urls]

        # Gather results
        results = await asyncio.gather(*tasks)

        for content in results:
            print(f'Content: {content[:100]}\n{"-"*60}\n')


if __name__ == "__main__":

    # List of URLs to scrape
    urls = [
        "https://example.com",
        "https://example.org",
        "https://example.net",
        # Add more URLs here
    ]

    # Run the main function
    asyncio.run(fetch_urls(urls))
