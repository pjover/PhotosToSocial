import os

from photos_to_bluesky.model.config import Config
from photos_to_bluesky.ports.storage import IStorage
from photos_to_bluesky.service.image_loader import ImageLoader
from photos_to_bluesky.service.post_builder import PostBuilder

xmp_tags_to_store = {
    "Title": "title",
    "Description": "caption",
    "Subject Code": "group",
    "Subject ": "keywords",
}


class Service:
    _posts_file: str
    _home_directory: str

    def __init__(self, config: Config, storage: IStorage):
        self._home_directory = self._check_directory(config.home_directory)
        self._storage = storage
        self._image_loader = ImageLoader(self._home_directory)
        self._post_builder = PostBuilder()

    @staticmethod
    def _check_directory(directory: str) -> str:
        if not os.path.isdir(directory):
            raise RuntimeError(f"Error: '{directory}' is not a valid directory.")
        print(f"Processing files in directory: `{directory}`")
        return directory

    def run(self):
        stored_posts = self._storage.load()

        new_images = self._image_loader.read_new_images(stored_posts)
        if not new_images:
            return

        new_posts = self._post_builder.group_images_into_posts(new_images)
        if not new_posts:
            return

        self._storage.store(stored_posts, new_posts)

