import os

from photos_to_bluesky.adaptors.storage.json_file import JsonStorage
from photos_to_bluesky.model.config import Config
from photos_to_bluesky.ports.storage import IStorage
from photos_to_bluesky.service.service import Service

HOME_ENV = "PhotosToBlueSkyHome"
POSTS_FILENAME = "posts.jsonl"

if __name__ == "__main__":
    config = Config(
        os.getenv(HOME_ENV),
        os.path.join(os.getenv(HOME_ENV), POSTS_FILENAME)
    )
    storage: IStorage = JsonStorage(config)
    Service(config, storage).run()
