import aiohttp
import asyncio
from typing import List, Tuple

from aiohttp import ClientSession

from utils.logger import Logger, LoggerLevel
from events.observables.observable_list import ObservableList


class ResponsesLoader:
    _hooks = {'response': Logger.console_log}

    def __init__(self, responses_collection_name: str):
        self._responses = ObservableList(responses_collection_name)
        self._errors: List[str] = []
        self._urls = []

    async def fetch_url(self, session: ClientSession, url: str) -> Tuple[str, str]:
        async with session.get(url) as response:
            self._urls.remove(url)
            return await self._apply_hooks(url, response)

    async def fetch_multiple_urls(self) -> None:
        responses = []
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_url(session, url) for url in self._urls]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in results:
                if isinstance(result, Exception):
                    Logger.console_log(f'{result}', LoggerLevel.WARNING)
                    self._add_error(f"ERROR: {result}")
                else:
                    url, content = result
                    responses.append({url: content})
        self._responses.extend(responses)

    def collect_responses(self) -> ObservableList:
        asyncio.run(self.fetch_multiple_urls())
        return self._responses

    def add_urls(self, urls: List[str]):
        self._urls += urls

    def show_errors(self) -> None:
        for error in self._errors:
            print(error)

    @staticmethod
    async def _apply_hooks(url: str, response: aiohttp.ClientResponse) -> Tuple[str, str]:
        content = await response.text()

        response_hook = ResponsesLoader._hooks.get('response')
        if response_hook:
            response_hook(f"Received response from {url}", LoggerLevel.INFO, include_time=True)

        return url, content

    def _add_error(self, error: str) -> None:
        self._errors.append(error)
