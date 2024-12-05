from typing import List, Protocol

from photos_to_bluesky.model.post import Post


class IStorage(Protocol):
    def load(self) -> List[Post]:
        """Load stored posts and return them as a list."""
        ...

    def store(self, stored_posts: List[Post], new_posts: List[Post]):
        """Store the given lists of posts."""
        ...
