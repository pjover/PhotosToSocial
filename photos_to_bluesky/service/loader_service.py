import logging

from photos_to_bluesky.model.config import Config
from photos_to_bluesky.ports.istorage import IStorage
from photos_to_bluesky.service.photo_loader import PhotoLoader
from photos_to_bluesky.service.post_builder import PostBuilder

xmp_tags_to_store = {
    "Title": "title",
    "Description": "caption",
    "Subject Code": "group",
    "Subject ": "keywords",
}


class LoaderService:
    _posts_file: str
    _home_directory: str

    def __init__(self, config: Config, storage: IStorage):
        self._home_directory = config.home_directory
        self._storage = storage
        self._photo_loader = PhotoLoader(self._home_directory)
        self._post_builder = PostBuilder()
        logging.info(f"Loading photos from directory: `{self._home_directory}`")

    def run(self):
        all_posts = self._storage.read_all_posts()

        new_photos = self._photo_loader.read_new_photos(all_posts)
        if not new_photos:
            return

        new_posts = self._post_builder.group_photos_into_posts(new_photos)
        if not new_posts:
            return

        self._storage.store(all_posts, new_posts)
