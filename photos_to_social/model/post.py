from typing import List

from pydantic import BaseModel


class Image(BaseModel):
    """Class for keeping track of an image from a post"""
    file: str
    title: str
    width: int
    height: int


class Post(BaseModel):
    """Class for keeping track of a post"""
    id: str
    images: List[Image]
    caption: str
    headline: str
    keywords: List[str]
    processed_on: str
    sent_on: str

    def __str__(self):
        return f"{self.id}: {self.caption}, {self.headline}, {self.images}, {self.keywords}, {self.processed_on}, {self.sent_on}"
