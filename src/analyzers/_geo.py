from ._result import AnalyzeResult
from loaders._session import SessionLoaderResult
from clients import maxmind
import logging
logger = logging.getLogger(__name__)


class GeoAnalyzers:
    def __init__(
        self,
        maxmind_client: maxmind.Client,
        sessions: dict[int, SessionLoaderResult]
    ) -> None:
        self._sessions = sessions
        self._maxmind_client = maxmind_client

    async def check(self):
        result: list[AnalyzeResult] = []
        with self._maxmind_client as maxmind_reader:
            for user_id, data in self._sessions.items():
                cites = {
                    i.city.name for i in (
                        maxmind_reader.city(ip)
                        for ip in data.sessions
                    ) if i.city.name and i.country.iso_code == "RU"
                }
                logger.info("For user %s founded %s cites. Hwid_limit: %s",
                            user_id, ", ".join(cites), data.hwid_limit)
                if len(cites) > data.hwid_limit * 3:
                    result.append(
                        AnalyzeResult(
                            user_id=user_id,
                            username=data.username,
                            for_admin_message="\n".join([
                                f'<b><tg-emoji emoji-id="5276240711795107620">⚠️</tg-emoji></b><b> Пользователь </b><code>{data.user_id}</code><b> заблокирован за обход лимита устройств:</b>',
                                '',
                                '<tg-emoji emoji-id="5278753302023004775">ℹ️</tg-emoji> <b>Пользователь был обнаружен в большем количестве городов, чем ему позволяет лимит:</b>',
                                '',
                                f'<tg-emoji emoji-id="5285350148451344065">💬</tg-emoji> Telegram id: <code>{data.telegram_id}</code>',
                                f'<tg-emoji emoji-id="5275979556308674886">👤</tg-emoji> Username: <code>{data.username}</code>',
                                f'<tg-emoji emoji-id="5278305362703835500">🔗</tg-emoji> Количество сессий: {len(data.sessions)}',
                                f'<tg-emoji emoji-id="6048522487845621737">📱</tg-emoji> Лимит устройств: {data.hwid_limit}',
                                f'<tg-emoji emoji-id="6048572296581353415">📊</tg-emoji> Количество городов: {len(cites)}',
                                '',
                                f'<tg-emoji emoji-id="5276412364458059956">🕓</tg-emoji> Время отчета: {AnalyzeResult.pretty_date()}',
                                '',
                                '<b><tg-emoji emoji-id="5276314275994954605">🔨</tg-emoji></b><b> Список городов:</b>',
                                f'<blockquote>{"\n".join(cites)}</blockquote>'
                            ])
                        )
                    )
        return result
