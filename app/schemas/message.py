import typing as t
from datetime import datetime
from pydantic import BaseModel


class MessageBase(BaseModel):
    conv_id: int
    content: str
    sender: str
    receiver: str
    sources: t.Optional[str] = ""


class MessageCreate(MessageBase):
    pass


class Message(MessageBase):
    id: int
    ts_created: datetime

    class Config:
        orm_mode = True
