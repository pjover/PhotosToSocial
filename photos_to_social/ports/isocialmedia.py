from typing import Protocol

from photos_to_social.model.post import Post


class ISocialMedia(Protocol):
    def publish_post(self, post: Post):
        """Publishes a post with images to social media."""
        ...