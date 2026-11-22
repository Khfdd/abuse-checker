from ._base import Base


class Users(Base):
    async def get_by_id(
        self,
        user_id: int
    ):
        return await self.get(
            self._base_url / f"api/users/{user_id}"
        )

    async def update_by_id(
        self,
        user_id: int,
        active_internal_squads: list[str]
    ):

        return await self.patch(
            self._base_url / f"api/users",
            json={key: value for key, value in {
                "id": user_id,
                "activeInternalSquads": active_internal_squads
            }.items() if value}
        )
