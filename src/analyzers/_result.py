import dataclasses
import datetime


@dataclasses.dataclass
class AnalyzeResult:
    __TZ = datetime.timezone(datetime.timedelta(hours=3), name="MSK")
    user_id: int
    username: str
    for_admin_message: str

    @classmethod
    def pretty_date(cls) -> str:
        return datetime.datetime.now(tz=cls.__TZ).strftime("%d.%m.%y %H:%M МСК")
