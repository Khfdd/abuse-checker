import aiohttp
import yarl
import typing
import logging

logger = logging.getLogger(__name__)


class Base:
    def __init__(
        self,
        base_url: yarl.URL,
        token: str,
        session: aiohttp.ClientSession
    ) -> None:
        self._base_url = base_url
        self._token = token
        self._session = session
        self._headers = {
            "Authorization": f"Bearer {token}"
        }

    async def _check_response(
        self,
        response: aiohttp.ClientResponse
    ):
        if response.status not in range(200, 300):
            logger.warning("Check response with status: %s", response.status)
            logger.warning("Requested URL: %s", response.url)
            logger.warning("Requested Method: %s", response.method)
            logger.warning("Returned json: %s", await response.json())
            response.raise_for_status()

    async def post(
        self,
        url: yarl.URL,
        json: typing.Any = None
    ):
        async with self._session.post(
            url=url,
            json=json,
            headers=self._headers
        ) as response:
            await self._check_response(response=response)
            return await response.json()

    async def patch(
        self,
        url: yarl.URL,
        json: typing.Any = None
    ):
        async with self._session.patch(
            url=url,
            json=json,
            headers=self._headers
        ) as response:
            await self._check_response(response=response)
            return await response.json()

    async def get(
        self,
        url: yarl.URL
    ):
        async with self._session.get(
            url=url,
            headers=self._headers
        ) as response:
            await self._check_response(response=response)
            return await response.json()
