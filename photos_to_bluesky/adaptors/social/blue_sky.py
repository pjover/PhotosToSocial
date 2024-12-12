import os.path
from math import gcd

from atproto import Client, client_utils
from atproto_client.models.app.bsky.embed.defs import AspectRatio

from photos_to_bluesky.model.config import Config
from photos_to_bluesky.model.post import Post
from photos_to_bluesky.ports.isocialmedia import ISocialMedia


class BlueSky(ISocialMedia):
    def __init__(self, config: Config):
        self._home_directory = config.home_directory
        self._client = Client()
        self._client.login(config.blue_sky_username, config.blue_sky_password)

    def publish_post(self, post: Post):
        print(f"Publishing post `{post.id}` to BlueSky ...")
        paths = [os.path.join(self._home_directory, img.file) for img in post.images]
        image_alts = [img.alt for img in post.images]
        image_aspect_ratios = [self._aspect_ratio(height=img.height, width=img.width) for img in post.images]

        images = []
        for path in paths:
            with open(path, 'rb') as f:
                images.append(f.read())

        text = f"{post.title}\n\n{post.text}"
        text_builder = client_utils.TextBuilder()
        text_builder.text(text)

        for keyword in post.keywords:
            text_builder.tag(f"#{keyword} ", keyword)

        self._client.send_images(
            text=text_builder,
            images=images,
            image_alts=image_alts,
            image_aspect_ratios=image_aspect_ratios,
        )

    @staticmethod
    def _aspect_ratio(height, width) -> AspectRatio:
        # Compute the greatest common divisor
        divisor = gcd(width, height)
        # Simplify the width and height by dividing by the GCD
        aspect_height = height // divisor
        aspect_width = width // divisor
        return AspectRatio(height=aspect_height, width=aspect_width)
