from pydantic import BaseModel


class DateFull(BaseModel):
    year: str
    month: str
    day: str

    @property
    def text(self) -> str:
        return f"{self.year}/{self.month}/{self.day}"
