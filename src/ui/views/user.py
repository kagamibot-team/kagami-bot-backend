from pydantic import BaseModel


class UserData(BaseModel):
    uid: int
    qqid: str
    name: str
