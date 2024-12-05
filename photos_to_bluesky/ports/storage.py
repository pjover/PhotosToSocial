from typing import List, Protocol

from photos_to_bluesky.model.post import Post


class IStorage(Protocol):
    def load(self) -> List[Post]:
        """Load stored posts and return them as a list."""
        ...

    def store(self, images: List[Post]):
        """Store the given list of posts."""
        ...
