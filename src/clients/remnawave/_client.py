import yarl
from aiohttp import ClientSession
from .connections import Connections
from .nodes import Nodes
from .users import Users


class Client:
    def __init__(
            self,
            base_url: yarl.URL,
            token: str,
            session: ClientSession
    ) -> None:

        self.connections = Connections(
            base_url=base_url,
            token=token,
            session=session
        )
        self.nodes = Nodes(
            base_url=base_url,
            token=token,
            session=session
        )

        self.users = Users(
            base_url=base_url,
            token=token,
            session=session
        )
