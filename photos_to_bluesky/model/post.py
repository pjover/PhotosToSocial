from dataclasses import dataclass
from typing import List


@dataclass
class Post:
    """Class for keeping track of a post"""
    images: List[str]
    text: List[str]
    group: str
    keywords: List[str]
    processed_on: str
    scheduled_on: str

    def __str__(self):
        return f"{self.text}, {self.group}, {self.keywords}, {self.images}, {self.processed_on}, {self.scheduled_on}"
