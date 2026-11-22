import uuid
import typing
import asyncio
import logging

from ._base import Base

logger = logging.getLogger(__name__)


class Connections(Base):
    async def by_node(
        self,
        node_uuid: uuid.UUID
    ) -> list[dict[str, typing.Any]]:
        data: dict[str, typing.Any] = await self.post(
            url=self._base_url / f"api/connections/by-node/{node_uuid}"
        )
        job_id = data.get("response", {}).get("jobId")
        if not job_id:
            raise RuntimeError(
                "Invalid answer from remnawave api: %s", data
            )

        for attempt in range(15):
            data: dict[str, typing.Any] = await self.get(
                url=self._base_url / f"api/connections/by-node/{job_id}"
            )
            response: dict[str, typing.Any] | None = data.get("response")
            if not response:
                raise RuntimeError("Invalid API answer: %s", response)
            failed: bool | None = response.get("isFailed")
            completed: bool | None = response.get("isCompleted")
            if completed is None or failed is None:
                raise RuntimeError("Invalid API answer: %s", response)
            if failed or completed:
                break
            logger.debug(
                "No ready yet. Wait 3 seconds and try again. Attempt: %s", attempt)
            await asyncio.sleep(3)

        try:
            return data["response"]["result"]["users"]
        except Exception as e:
            logger.warning(
                "Response failed with error %s. Response data: %s", e, data)
        return []
