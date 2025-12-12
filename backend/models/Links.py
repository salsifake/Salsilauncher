from pydantic import BaseModel, HttpUrl


class Link(BaseModel):
    url: HttpUrl
