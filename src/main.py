import asyncio
import aiohttp
import yarl
import logging
from settings import settings
from clients import remnawave, maxmind
from loaders import SessionLoader
from analyzers import GeoAnalyzers
from notifications import Telegram

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(filename)s | %(funcName)s -> %(message)s",
)
logger = logging.getLogger(__name__)


async def scan():
    async with aiohttp.ClientSession(
        proxy=settings.PROXY
    ) as session:
        notifier = Telegram(
            bot_token=settings.TELEGRAM_BOT_TOKEN,
            chat_id=settings.TELEGRAM_CHAT_ID,
            topic_id=settings.TELEGRAM_TOPIC_ID,
            session=session
        )
        maxmind_client = maxmind.Client(
            account_id=settings.MAXMIND_ACCOUNT_ID,
            license_key=settings.MAXMIND_LICENSE_KEY,
            data_dir=settings.DATA_DIR,
            session=session
        )
        await maxmind_client.update_local_database()

        remnawave_client = remnawave.Client(
            base_url=yarl.URL(
                settings.REMNAWAVE_API_BASE_URL.rstrip("/")),
            token=settings.REMNAWAVE_API_TOKEN,
            session=session
        )

        logger.info("-----> GEO ANALYZER <-----")
        violations = await GeoAnalyzers(
            maxmind_client=maxmind_client,
            sessions=await SessionLoader(
                remnawave_client=remnawave_client,
                exclude_node_tags=["NO_REAL_IP"],
                min_session_count=4,
                device_limit_multiplier=3
            ).load()
        ).check()

        logger.info("-----> LIMIT ANALYZER <-----")

        if len(violations) > 5:
            await notifier.send(
                f"Большое количество нарушений: {len(violations)}"
            )

        for violation in violations[:5]:
            await notifier.send(
                violation.for_admin_message
            )
            try:
                await remnawave_client.users.update_by_id(
                    user_id=violation.user_id,
                    active_internal_squads=[
                        settings.REMNAWAVE_BLOCK_SQUAD
                    ]
                )
            except Exception as e:
                await notifier.send(
                    f"Failed: {e}"
                )
                logger.exception("Failed for violation: %s",
                                 violation.for_admin_message, exc_info=e)


async def main():
    while True:
        try:
            await scan()
        except Exception as e:
            logger.exception("Failed.", exc_info=e)
            logger.info("Sleep 60 seconds and try again.")
            await asyncio.sleep(60)
            continue
        for progress in range(10):
            logger.info(
                f"Sleep {settings.SLEEP} seconds. Progress: {progress*10}%")
            await asyncio.sleep(settings.SLEEP/10)

if __name__ == "__main__":
    asyncio.run(main())
