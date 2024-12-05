import json
import os
from typing import List

from photos_to_bluesky.model.config import Config
from photos_to_bluesky.model.post import Post
from photos_to_bluesky.ports.storage import IStorage


class JsonStorage(IStorage):
    def __init__(self, config: Config):
        self._file_path = self._check_file(config.posts_file)

    @staticmethod
    def _check_file(file_path: str) -> str:
        if not os.path.isfile(file_path):
            raise RuntimeError(f"Error: '{file_path}' is not a valid file.")
        return file_path

    def load(self) -> List[Post]:
        posts = []
        with open(self._file_path, "r") as file:
            for line in file:
                data = json.loads(line)
                posts.append(Post(**data))
        return posts

    def store(self, stored_posts: List[Post], new_posts: List[Post]):
        posts = sorted(stored_posts + new_posts, key=lambda post: post.id)
        with open(self._file_path, "w") as file:
            for post in posts:
                json.dump(post.__dict__, file)
                file.write("\n")
