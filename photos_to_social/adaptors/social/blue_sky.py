import logging
import os.path
from math import gcd

from atproto import Client, client_utils
from atproto_client.models.app.bsky.embed.defs import AspectRatio

from photos_to_social.model.config import Config
from photos_to_social.model.post import Post
from photos_to_social.ports.error_notifier import ErrorNotifier
from photos_to_social.ports.social_media import SocialMedia


class BlueSky(SocialMedia):
    def __init__(self, config: Config, error_notifier: ErrorNotifier):
        self._home_directory = config.home_directory
        self._client = self._client(config.blue_sky_username, config.blue_sky_password)
        self._error_notifier = error_notifier

    def _client(self, username: str, password: str):
        try:
            _client = Client()
            _client.login(username, password)
            return _client
        except Exception as e:
            msg = f"Failed to login to BlueSky: {e}"
            self._error_notifier.notify(msg, str(e))
            raise RuntimeError(f"{msg}: {e}")

    def name(self) -> str:
        return "BlueSky"

    def publish_post(self, post: Post):
        logging.info(f"Publishing post `{post.id}` to BlueSky ...")
        paths = [os.path.join(self._home_directory, img.file) for img in post.images]
        image_alts = [img.title for img in post.images]
        image_aspect_ratios = [self._aspect_ratio(height=img.height, width=img.width) for img in post.images]

        images = []
        for path in paths:
            with open(path, 'rb') as f:
                images.append(f.read())

        text_builder = client_utils.TextBuilder()
        text_builder.text(self.build_text(post))
        for keyword in post.keywords:
            text_builder.tag(f"#{keyword} ", keyword)

        self._client.send_images(
            text=text_builder,
            images=images,
            image_alts=image_alts,
            image_aspect_ratios=image_aspect_ratios,
        )
        logging.info(f"Published post `{post.id}` to BlueSky")

    @staticmethod
    def build_text(post: Post) -> str:
        text = ""
        if post.caption:
            text += f"{post.caption}\n\n"
        if len(post.images) > 1:
            for image in post.images:
                if image.title:
                    text += f"- {image.title}\n"
            text += "\n"
        else:
            text += f"{post.images[0].title}\n\n"

        if post.headline:
            text += f"{post.headline}\n\n"

        return text

    @staticmethod
    def _aspect_ratio(height, width) -> AspectRatio:
        # Compute the greatest common divisor
        divisor = gcd(width, height)
        # Simplify the width and height by dividing by the GCD
        aspect_height = height // divisor
        aspect_width = width // divisor
        return AspectRatio(height=aspect_height, width=aspect_width)
