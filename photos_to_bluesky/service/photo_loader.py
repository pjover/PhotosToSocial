import logging
import os
import subprocess
from typing import List

from photos_to_bluesky.model.photo import Photo
from photos_to_bluesky.model.post import Post

tags_to_store = {
    "Title": "title",
    "Description": "caption",
    "Subject ": "keywords",
    "Transmission Reference": "job_id",
    "Image Width": "width",
    "Image Height": "height",
}


class PhotoLoader:
    def __init__(self, home_directory: str):
        self._home_directory = home_directory

    def read_new_photos(self, stored_posts: List[Post]) -> List[Photo]:
        files = self._read_all_files()
        new_files = [file for file in files if self._is_new_file(file, stored_posts)]
        photos = []
        index = 0
        for file in sorted(new_files):
            photos.append(self._read(index, file))
            index += 1
        if photos:
            logging.info(f"Found {len(photos)} new photos.")
        else:
            logging.info("No new photos found.")
        return photos

    def _read_all_files(self) -> List[str]:
        _files = []
        for root, dirs, files in os.walk(self._home_directory):
            _files = [x for x in sorted(files) if x.lower().endswith(('.jpg', '.jpeg'))]
            return _files

    @staticmethod
    def _is_new_file(file: str, stored_posts: List[Post]) -> bool:
        for post in stored_posts:
            post_images = [image.file for image in post.images]
            if file in post_images:
                return False
        return True

    def _read(self, index: int, file: str) -> Photo:
        photo = Photo(id=index, file=file)
        xmp_lines = self._command(["exiftool", "-XMP:all", os.path.join(self._home_directory, file)])
        file_lines = self._command(["exiftool", "-File:all", os.path.join(self._home_directory, file)])
        for line in xmp_lines + file_lines:
            self._extract_tag(line, photo)
        if not photo.title:
            raise RuntimeError(f"Title not found for photo {photo.file}")

        photo.id = self._build_id(photo, index)
        logging.info(f"Read photo: {photo}")
        return photo

    @staticmethod
    def _build_id(photo: Photo, index: int) -> int:
        base = int(photo.job_id.replace('JOB', ''))
        return base * 10000 + index

    @staticmethod
    def _command(command) -> List[str]:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            return result.stdout.splitlines()
        else:
            raise RuntimeError(f"Error running command {command}: {result.stderr}")

    @staticmethod
    def _extract_tag(line: str, photo: Photo) -> Photo:
        for tag, field in tags_to_store.items():
            if not line.startswith(tag):
                continue
            content = line.split(":")[1].strip()
            if field == "keywords":
                photo.keywords = content.replace("#", "").split(", ")
            elif field == "title":
                photo.title = content
            elif field == "caption":
                photo.caption = content
            elif field == "job_id":
                photo.job_id = content
            elif field == "width":
                photo.width = content
            elif field == "height":
                photo.height = content
        return photo
