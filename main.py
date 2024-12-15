import argparse
import os

from photos_to_bluesky.adaptors.social.blue_sky import BlueSky
from photos_to_bluesky.adaptors.social.word_press import WordPress
from photos_to_bluesky.adaptors.storage.json_storage import JsonStorage
from photos_to_bluesky.model.config import Config
from photos_to_bluesky.ports.istorage import IStorage
from photos_to_bluesky.service.loader_service import LoaderService
from photos_to_bluesky.service.post_service import PostService

POSTS_FILENAME = "posts.jsonl"


def _check_directory(directory: str) -> str:
    if not os.path.isdir(directory):
        raise RuntimeError(f"Error: '{directory}' is not a valid directory.")
    return directory


def _load_config() -> Config:
    home_directory = _check_directory(os.getenv("PHOTOS_TO_SOCIAL_HOME"))
    return Config(
        home_directory=home_directory,
        posts_file=os.path.join(home_directory, POSTS_FILENAME),
        blue_sky_username=os.getenv("BLUE_SKY_USERNAME"),
        blue_sky_password=os.getenv("BLUE_SKY_PASSWORD"),
        gmail_user_email=os.getenv("GMAIL_USER_EMAIL"),
        gmail_app_password=os.getenv("GMAIL_APP_PASSWORD"),
        word_press_post_by_email_to=os.getenv("WORD_PRESS_POST_BY_EMAIL_TO"),
    )


def _load_args():
    parser = argparse.ArgumentParser(
        description=
        "Script that processes exported photos from Lightroom and post the to BlueSky."
        "See the README file for more details."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-l", "--load", action="store_true", help="Load photos from home directory and prepare posts.")
    group.add_argument("-p", "--post", action="store_true", help="Send next post to Social media.")

    return parser.parse_args()


if __name__ == "__main__":
    args = _load_args()
    config = _load_config()
    storage: IStorage = JsonStorage(config)
    if args.load:
        LoaderService(
            config,
            storage,
        ).run()
    elif args.post:
        PostService(
            config,
            storage,
            [
                BlueSky(config),
                WordPress(config),
            ],
        ).run()
