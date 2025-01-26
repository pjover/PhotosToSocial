import argparse
import logging
import os
import sys
from logging.handlers import RotatingFileHandler

from photos_to_social.adaptors.error_notifier.email import EmailErrorNotifier
from photos_to_social.adaptors.social.blue_sky import BlueSky
from photos_to_social.adaptors.social.word_press import WordPress
from photos_to_social.adaptors.storage.json_storage import JsonStorage
from photos_to_social.model.config import Config
from photos_to_social.ports.storage import Storage
from photos_to_social.service.loader_service import LoaderService
from photos_to_social.service.post_service import PostService

POSTS_FILENAME = "posts.jsonl"
LOG_FILENAME = "photos_to_social.log"
MAX_LOG_SIZE = 1024 * 512


def _check_directory(directory: str) -> str:
    if not os.path.isdir(directory):
        raise RuntimeError(f"Error: '{directory}' is not a valid directory.")
    return directory


def _load_config() -> Config:
    _dir = os.getenv("PHOTOS_TO_SOCIAL_HOME")
    if not _dir:
        raise RuntimeError("Error: PHOTOS_TO_SOCIAL_HOME environment variable is not set.")
    home_directory = _check_directory(_dir)
    return Config(
        home_directory=home_directory,
        posts_file=os.path.join(home_directory, POSTS_FILENAME),
        blue_sky_username=os.getenv("BLUE_SKY_USERNAME"),
        blue_sky_password=os.getenv("BLUE_SKY_PASSWORD"),
        email_user_email=os.getenv("GMAIL_USER_EMAIL"),
        email_app_password=os.getenv("GMAIL_APP_PASSWORD"),
        email_smtp_server="smtp.gmail.com",
        email_smtp_port=465,
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

    _args = parser.parse_args()
    logging.debug(f"Args: load: {_args.load}, send: {_args.send}")
    return _args


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
    logging.debug(f"Logging on file {_file}")


if __name__ == "__main__":
    config = _load_config()
    _init_logging(logging.INFO, config.home_directory)
    args = _load_args()
    logging.info(f"Starting PhotosToSocial ...")
    storage: Storage = JsonStorage(config)
    error_notifier = EmailErrorNotifier(config)
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
            error_notifier,
            [
                BlueSky(config),
                WordPress(config),
            ],
        ).run()

