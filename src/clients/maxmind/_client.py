import pathlib
import time
import logging
import aiohttp
import tarfile
import io
import geoip2.database

logger = logging.getLogger(__name__)


class Client:
    def __init__(
        self,
        account_id: str,
        license_key: str,
        data_dir: pathlib.Path,
        session: aiohttp.ClientSession
    ) -> None:
        self._session = session
        self._account_id = account_id
        self._license_key = license_key
        self._data_dir = data_dir / "maxmind"
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._database_path = self._data_dir / "database.mmdb"
        self._database_url = "https://download.maxmind.com/geoip/databases/GeoLite2-City/download?suffix=tar.gz"

    async def _download_db(
        self
    ):
        async with self._session.get(
            self._database_url,
            auth=aiohttp.BasicAuth(
                login=self._account_id,
                password=self._license_key
            ),
            timeout=aiohttp.ClientTimeout(60)
        ) as response:
            response.raise_for_status()
            buffer = io.BytesIO()
            buffer.write(await response.read())
            buffer.seek(0)

        with tarfile.open(fileobj=buffer, mode="r:gz") as tar:
            member = next(m for m in tar.getmembers()
                          if m.name.endswith(".mmdb"))
            logger.info("Founded next databases: %s", member)
            member.name = self._database_path.name  # убираем вложенную папку
            tar.extract(member, path=self._data_dir)

    async def update_local_database(
        self,
    ):
        if self._database_path.exists():
            if not self._database_path.is_file():
                raise RuntimeError("Maxmind database isn't file.")
            age_seconds = time.time() - self._database_path.stat().st_mtime
            logger.info(
                "Maxmind database is %s days %s hours %s minutes %s seconds old.",
                age_seconds // (3600 * 24),
                (age_seconds // 3600) % 24,
                (age_seconds // 60) % 60,
                round(age_seconds % 60)
            )
            if age_seconds >= 7 * 24 * 3600:
                logger.info("Maxmind is deprecated. Updating...")
                await self._download_db()

        else:
            logger.info("Maxmind database not found. Downloading...")
            await self._download_db()

    def __enter__(self):
        self.reader = geoip2.database.Reader(self._database_path)
        return self.reader

    def __exit__(self, *_):
        self.reader.close()
