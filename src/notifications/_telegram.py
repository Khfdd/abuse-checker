import aiohttp
import typing


class Telegram:
    def __init__(
        self,
        bot_token: str,
        chat_id: int,
        topic_id: int,
        session: aiohttp.ClientSession
    ):
        self._bot_token = bot_token
        self._chat_id = chat_id
        self._topic_id = topic_id
        self._session = session

    async def send(
        self,
        msg: str
    ) -> dict[str, typing.Any]:
        url = f"https://api.telegram.org/bot{self._bot_token}/sendMessage"
        payload = {
            "chat_id": self._chat_id,
            "message_thread_id": self._topic_id,
            "text": msg,
            "parse_mode": "HTML"
        }

        async with self._session.post(url, json=payload) as response:
            response.raise_for_status()
            return await response.json()
