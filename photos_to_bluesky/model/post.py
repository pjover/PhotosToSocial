from dataclasses import dataclass
from typing import List


@dataclass
class Image:
    """Class for keeping track of an image from a post"""
    file: str
    alt: str
    width: int
    height: int


@dataclass
class Post:
    """Class for keeping track of a post"""
    id: int
    images: List[Image]
    text: List[str]
    group: str
    keywords: List[str]
    processed_on: str
    sent_on: str

    def __str__(self):
        return f"{self.id}: {self.text}, {self.group}, {self.keywords}, {self.images}, {self.processed_on}, {self.sent_on}"
