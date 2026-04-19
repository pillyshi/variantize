from pydantic import BaseModel


class DateFull(BaseModel):
    year: str
    month: str
    day: str
    template: str = "{year}/{month}/{day}"
