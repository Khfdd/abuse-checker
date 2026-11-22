from ._base import Base


class Nodes(Base):
    async def get_all(
        self
    ):
        return await self.get(
            url=self._base_url / "api/nodes"
        )
