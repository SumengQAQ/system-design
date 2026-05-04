from pydantic import BaseModel, HttpUrl


class EncodeRequest(BaseModel):
    long_url: HttpUrl
    custom_code: str | None = None
