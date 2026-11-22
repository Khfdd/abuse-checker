import logging
import typing
import uuid
import dataclasses
from clients.remnawave import Client

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class SessionLoaderResult:
    user_id: int
    username: str
    sessions: set[str]
    hwid_limit: int
    telegram_id: int | None


class SessionLoader:
    def __init__(
        self,
        remnawave_client: Client,
        min_session_count: int,
        device_limit_multiplier: int,
        include_node_tags: list[str] | None = None,
        exclude_node_tags: list[str] | None = None,
    ) -> None:
        self._remnawave_client = remnawave_client
        self._include_node_tags = include_node_tags
        self._exclude_node_tags = exclude_node_tags
        self._min_session_count = min_session_count
        self._device_limit_multiplier = device_limit_multiplier

    async def load(self):
        nodes_raw = await self._remnawave_client.nodes.get_all()
        nodes: list[dict[str, typing.Any]] = nodes_raw.get("response")
        if not nodes:
            raise RuntimeError("Cat't get all nodes. Invalid API response.")

        client_sessions_map: dict[int, SessionLoaderResult] = {}
        for node in nodes:
            name: str = node["name"]
            node_uuid: str = node["uuid"]
            tags: list[str] | None = node.get("tags")
            if self._include_node_tags and (
                tags is None or all(
                    include_node_tag not in tags
                    for include_node_tag in self._include_node_tags
                )
            ):
                continue
            if tags and self._exclude_node_tags and any(
                exclude_node_tag in tags
                for exclude_node_tag in self._exclude_node_tags
            ):
                continue

            logger.info("Processing node: %s (Tags: %s)", name, tags)

            sessions: list[dict[str, typing.Any]] = await self._remnawave_client.connections.by_node(
                node_uuid=uuid.UUID(node_uuid)
            )
            logger.debug("  Founded %s sessions.", len(sessions))
            for session in sessions:
                user_id = session["userId"]
                ips: list[dict[str, typing.Any]] = session["ips"]
                if user_id not in client_sessions_map:
                    client_sessions_map[user_id] = SessionLoaderResult(
                        user_id=user_id,
                        sessions=set(),
                        hwid_limit=0,
                        telegram_id=None,
                        username=""
                    )
                client_sessions_map[user_id].sessions.update(
                    ip["ip"] for ip in ips)

        client_sessions_map = {
            key: data for key, data in client_sessions_map.items() if len(data.sessions) >= self._min_session_count
        }

        for key in list(client_sessions_map):
            user_info = await self._remnawave_client.users.get_by_id(key)
            hwid_limit: int | None = user_info["response"]["hwidDeviceLimit"]
            if not hwid_limit:
                logger.warning("For user %s hwid limit is None.", key)
                del client_sessions_map[key]
                continue
            client_sessions_map[key].hwid_limit = hwid_limit
            client_sessions_map[key].telegram_id = user_info["response"]["telegramId"]
            client_sessions_map[key].username = user_info["response"]["username"]

            if hwid_limit * self._device_limit_multiplier >= len(client_sessions_map[key].sessions):
                logger.info(
                    "User %s is normal. Count of session <= hwid * multiplier: %s < %s * %s",
                    key,
                    len(client_sessions_map[key].sessions),
                    hwid_limit,
                    self._device_limit_multiplier
                )
                del client_sessions_map[key]

        return client_sessions_map
