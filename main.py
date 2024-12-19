import argparse
import logging
import os
import sys
from logging.handlers import RotatingFileHandler

from photos_to_bluesky.adaptors.social.blue_sky import BlueSky
from photos_to_bluesky.adaptors.social.word_press import WordPress
from photos_to_bluesky.adaptors.storage.json_storage import JsonStorage
from photos_to_bluesky.model.config import Config
from photos_to_bluesky.ports.istorage import IStorage
from photos_to_bluesky.service.loader_service import LoaderService
from photos_to_bluesky.service.post_service import PostService

POSTS_FILENAME = "posts.jsonl"
LOG_FILENAME = "photos_to_social.log"
MAX_LOG_SIZE = 1024 * 512


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
    group.add_argument("-s", "--send", action="store_true", help="Send next post to Social media.")

    return parser.parse_args()


def _init_logging(level, home_directory):
    _file = os.path.join(home_directory, LOG_FILENAME)
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            RotatingFileHandler(filename=_file, maxBytes=MAX_LOG_SIZE, backupCount=5),
            logging.StreamHandler(sys.stdout)
        ]
    )


if __name__ == "__main__":
    logging.info("Setting up PhotosToSocial ...")
    args = _load_args()
    config = _load_config()
    _init_logging(logging.INFO, config.home_directory)
    logging.info(f"Loaded config: {config}")
    storage: IStorage = JsonStorage(config)
    if args.load:
        logging.info(f"Loading new posts from {config.home_directory} ...")
        LoaderService(
            config,
            storage,
        ).run()
    elif args.send:
        logging.info("Sending one post to social media ...")
        PostService(
            config,
            storage,
            [
                BlueSky(config),
                WordPress(config),
            ],
        ).run()
