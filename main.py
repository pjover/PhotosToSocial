import argparse
import os

from photos_to_bluesky.adaptors.social.word_press import WordPress
from photos_to_bluesky.adaptors.storage.json_storage import JsonStorage
from photos_to_bluesky.model.config import Config
from photos_to_bluesky.ports.istorage import IStorage
from photos_to_bluesky.service.loader_service import LoaderService
from photos_to_bluesky.service.post_service import PostService

HOME_ENV = "PHOTOS_TO_SOCIAL_HOME"
BLUE_SKY_USERNAME_ENV = "BLUE_SKY_USERNAME"
BLUE_SKY_PASSWORD_ENV = "BLUE_SKY_PASSWORD"
WORD_PRESS_POST_BY_EMAIL_FROM_ENV = "WORD_PRESS_POST_BY_EMAIL_FROM"
WORD_PRESS_POST_BY_EMAIL_TO_ENV = "WORD_PRESS_POST_BY_EMAIL_TO"
WORD_PRESS_POST_BY_EMAIL_CREDENTIALS_FILENAME = "credentials.json"
WORD_PRESS_POST_BY_EMAIL_TOKEN_FILENAME = "token.json"
POSTS_FILENAME = "posts.jsonl"


def _check_directory(directory: str) -> str:
    if not os.path.isdir(directory):
        raise RuntimeError(f"Error: '{directory}' is not a valid directory.")
    return directory


def _load_config() -> Config:
    home_directory = _check_directory(os.getenv(HOME_ENV))
    return Config(
        home_directory=home_directory,
        posts_file=os.path.join(home_directory, POSTS_FILENAME),
        blue_sky_username=os.getenv(BLUE_SKY_USERNAME_ENV),
        blue_sky_password=os.getenv(BLUE_SKY_PASSWORD_ENV),
        word_press_post_by_email_from=os.getenv(WORD_PRESS_POST_BY_EMAIL_FROM_ENV),
        word_press_post_by_email_to=os.getenv(WORD_PRESS_POST_BY_EMAIL_TO_ENV),
        word_press_post_by_email_credentials_filename=WORD_PRESS_POST_BY_EMAIL_CREDENTIALS_FILENAME,
        word_press_post_by_email_token_filename=WORD_PRESS_POST_BY_EMAIL_TOKEN_FILENAME,
    )


def _load_args():
    parser = argparse.ArgumentParser(
        description=
        "Script that processes exported photos from Lightroom and post the to BlueSky."
        "See the README file for more details."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-l", "--load", action="store_true", help="Load photos from home directory and prepare posts.")
    group.add_argument("-p", "--post", action="store_true", help="Send next post to BlueSky.")

    return parser.parse_args()


if __name__ == "__main__":
    args = _load_args()
    config = _load_config()
    storage: IStorage = JsonStorage(config)
    if args.load:
        LoaderService(config, storage).run()
    elif args.post:
        social_media = [
            # BlueSky(config),
            WordPress(config),
        ]
        PostService(config, storage, social_media).run()
