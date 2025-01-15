from typing import List

from pydantic import BaseModel


class Photo(BaseModel):
    """Class for keeping track of a photo read from a file"""
    id: int
    file: str
    headline: str = ""
    order: str = ""
    caption: str = ""
    title: str = ""
    keywords: List[str] = list()
    width: int = 0
    height: int = 0
