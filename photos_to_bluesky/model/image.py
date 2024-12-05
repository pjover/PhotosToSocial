from dataclasses import dataclass
from typing import List

NO_GROUP = "NO_GROUP"


@dataclass
class Image:
    """Class for keeping track of an image read from a file"""
    id: id
    file: str
    title: str = ""
    caption: str = ""
    group: str = NO_GROUP
    keywords: List[str] = list
    job_id: str = ""
