from datetime import datetime

from photos_to_bluesky.model.config import Config
from photos_to_bluesky.ports.isocialmedia import ISocialMedia
from photos_to_bluesky.ports.istorage import IStorage


class PostService:
    def __init__(self, config: Config, storage: IStorage, social_media: ISocialMedia):
        self._home_directory = config.home_directory
        self._storage = storage
        self._social_media = social_media

    def run(self):
        next_post = self._storage.read_next_post()
        if not next_post:
            print("No posts to publish.")
            return
        print(f"Publishing post: {next_post}")
        self._social_media.publish_post(next_post)
        next_post.sent_on = datetime.now().isoformat()
        # self._storage.update(next_post)
