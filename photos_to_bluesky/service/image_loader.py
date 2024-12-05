import os
import subprocess
from typing import List

from photos_to_bluesky.model.image import Image
from photos_to_bluesky.model.post import Post

xmp_tags_to_store = {
    "Title": "title",
    "Description": "caption",
    "Subject Code": "group",
    "Subject ": "keywords",
}


class ImageLoader:
    def __init__(self, home_directory: str):
        self._home_directory = home_directory

    def read_new_images(self, stored_posts: List[Post]) -> List[Image]:
        # TODO return new image, not all images in directory
        images = []
        for root, dirs, files in os.walk(self._home_directory):
            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg')):
                    image_file = os.path.join(root, file)
                    image = self._read(image_file)
                    images.append(image)
        return images

    def _read(self, image_file: str) -> Image:
        image = Image(path=image_file)
        lines = self._command(["exiftool", "-XMP:all", image_file])
        for line in lines:
            self._extract_tag(line, image)
        return image

    @staticmethod
    def _command(command) -> List[str]:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            return result.stdout.splitlines()
        else:
            raise RuntimeError(f"Error running command {command}: {result.stderr}")

    @staticmethod
    def _extract_tag(line: str, image: Image) -> Image:
        for tag, field in xmp_tags_to_store.items():
            if not line.startswith(tag):
                continue
            content = line.split(":")[1].strip()
            if field == "keywords":
                image.keywords = content.split(", ")
            elif field == "title":
                image.title = content
            elif field == "caption":
                image.caption = content
            elif field == "group":
                image.group = content
        return image
