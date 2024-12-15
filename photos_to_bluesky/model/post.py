from typing import List

from pydantic import BaseModel


class Image(BaseModel):
    """Class for keeping track of an image from a post"""
    file: str
    alt: str
    width: int
    height: int


class Post(BaseModel):
    """Class for keeping track of a post"""
    id: int
    images: List[Image]
    title: str
    text: str
    keywords: List[str]
    processed_on: str
    sent_on: str

    def __str__(self):
        return f"{self.id}: {self.title}, {self.text}, {self.keywords}, {self.images}, {self.processed_on}, {self.sent_on}"
