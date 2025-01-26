from typing import List, Protocol, Optional

from photos_to_social.model.post import Post


class Storage(Protocol):
    def read_all_posts(self) -> List[Post]:
        """Load all stored posts and return them as a list."""
        ...

    def read_next_post(self) -> Optional[Post]:
        """Load the next post to be published."""
        ...

    def update(self, post: Post):
        """Store the given post."""
        ...

    def store(self, stored_posts: List[Post], new_posts: List[Post]):
        """Store the given lists of posts."""
        ...
