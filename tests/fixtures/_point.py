from pydantic import BaseModel


class PointFull(BaseModel):
    x: str
    y: str
