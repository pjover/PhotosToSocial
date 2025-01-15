import logging
import os
from datetime import datetime, timedelta
from typing import List, Optional

from photos_to_social.model.config import Config
from photos_to_social.model.post import Post
from photos_to_social.ports.istorage import IStorage


class JsonStorage(IStorage):
    def __init__(self, config: Config):
        self._file_path = self._check_file(config.posts_file)

    @staticmethod
    def _check_file(file_path: str) -> str:
        if not os.path.isfile(file_path):
            open(file_path, 'a').close()
            logging.info(f"File '{file_path}' did not exist and was created.")
        return file_path

    def read_all_posts(self) -> List[Post]:
        posts = []
        with open(self._file_path, "r") as file:
            for line in file:
                _line = line.strip()
                if not _line:
                    continue
                post = Post.model_validate_json(_line)
                posts.append(post)
        return posts

    def read_next_post(self) -> Optional[Post]:
        all_posts = self.read_all_posts()
        if not all_posts:
            return None
        not_sent_posts = [post for post in all_posts if not post.sent_on]
        if not not_sent_posts:
            return None
        date_until = datetime.today() + timedelta(days=len(not_sent_posts))
        logging.info(f"There are {len(not_sent_posts)} posts to publish, until {date_until}.")
        sorted_not_sent_posts = sorted(not_sent_posts, key=lambda post: post.id)
        return sorted_not_sent_posts[0]

    def update(self, post: Post):
        all_posts = self.read_all_posts()
        other_posts = [p for p in all_posts if p.id != post.id]
        self.store(other_posts, [post])

    def store(self, stored_posts: List[Post], new_posts: List[Post]):
        posts = sorted(stored_posts + new_posts, key=lambda post: post.id)
        with open(self._file_path, "w") as file:
            for post in posts:
                line = post.model_dump_json()
                file.write(f"{line}\n")
