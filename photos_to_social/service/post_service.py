import logging
import typing
from datetime import datetime

from photos_to_social.model.config import Config
from photos_to_social.ports.isocialmedia import ISocialMedia
from photos_to_social.ports.istorage import IStorage


class PostService:
    def __init__(self, config: Config, storage: IStorage, social_media: typing.List[ISocialMedia]):
        self._home_directory = config.home_directory
        self._storage = storage
        self._social_media = social_media

    def run(self):
        next_post = self._storage.read_next_post()
        if not next_post:
            logging.info("No posts to publish.")
            return
        logging.info(f"Publishing post: {next_post}")
        for social_media in self._social_media:
            social_media.publish_post(next_post)
        next_post.sent_on = datetime.now().isoformat()
        self._storage.update(next_post)
