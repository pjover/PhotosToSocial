from typing import Protocol

from photos_to_social.model.post import Post


class SocialMedia(Protocol):
    def publish_post(self, post: Post):
        """Publishes a post with images to social media."""
        ...

    def name(self) -> str:
        """Returns the name of the social media."""
        ...
