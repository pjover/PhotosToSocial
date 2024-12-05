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
        files = self._read_all_files()
        images = []
        for file in files:
            if self._is_new_file(file, stored_posts):
                images.append(self._read(file))
        return images

    def _read_all_files(self) -> List[str]:
        _files = []
        for root, dirs, files in os.walk(self._home_directory):
            _files = [os.path.join(root, x) for x in sorted(files) if x.lower().endswith(('.jpg', '.jpeg'))]
            return _files

    def _read_file(self, file: str, stored_posts: List[Post]) -> Image | None:
        if self._is_new_file(file, stored_posts):
            return self._read(file)
        return None

    @staticmethod
    def _is_new_file(file: str, stored_posts: List[Post]) -> bool:
        for post in stored_posts:
            if file in post.images:
                return False
        return True

    def _read(self, file: str) -> Image:
        image = Image(path=file)
        lines = self._command(["exiftool", "-XMP:all", file])
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
