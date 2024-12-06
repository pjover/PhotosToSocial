import logging
import os
import subprocess
from datetime import datetime
from typing import List

from photos_to_bluesky.model.photo import Photo
from photos_to_bluesky.model.post import Post

tags_to_store = {
    "Title": "title",
    "Description": "caption",
    "Subject ": "keywords",
    "Image Width": "width",
    "Image Height": "height",
}

MAX_JOB_SIZE = 10 ** 3


class PhotoLoader:
    def __init__(self, home_directory: str):
        self._home_directory = home_directory

    def read_new_photos(self, stored_posts: List[Post]) -> List[Photo]:
        job_id = self._generate_job_id()
        files = self._read_all_files()
        new_files = self._new_files(files, stored_posts)
        photos = []
        index = 1
        for file in sorted(new_files):
            _id = self._build_id(job_id, index)
            photos.append(self._read(_id, file))
            index += 1
        if photos:
            logging.info(f"Found {len(photos)} new photos.")
        else:
            logging.info("No new photos found.")
        return photos

    @staticmethod
    def _generate_job_id() -> int:
        now = datetime.now()
        year = now.year % 100
        day_of_year = now.timetuple().tm_yday
        seconds_of_day = now.hour * 3600 + now.minute * 60 + now.second
        job_id = f"{year:02}{day_of_year:03}{seconds_of_day:05}"
        return int(job_id)

    @staticmethod
    def _build_id(job_id: int, index: int) -> int:
        return job_id * MAX_JOB_SIZE + index

    def _read_all_files(self) -> List[str]:
        _files = []
        for root, dirs, files in os.walk(self._home_directory):
            _files = [x for x in sorted(files) if x.lower().endswith(('.jpg', '.jpeg'))]
            return _files

    def _new_files(self, files: List[str], stored_posts: List[Post]) -> List[str]:
        new_files = [file for file in files if self._is_new_file(file, stored_posts)]
        if len(new_files) >= MAX_JOB_SIZE:
            raise RuntimeError(f"Too many new files ({len(new_files)}) in job, max is {MAX_JOB_SIZE}")
        return new_files

    @staticmethod
    def _is_new_file(file: str, stored_posts: List[Post]) -> bool:
        for post in stored_posts:
            post_images = [image.file for image in post.images]
            if file in post_images:
                return False
        return True

    def _read(self, photo_id: int, file: str) -> Photo:
        photo = Photo(id=photo_id, file=file)
        xmp_lines = self._command(["exiftool", "-XMP:all", os.path.join(self._home_directory, file)])
        file_lines = self._command(["exiftool", "-File:all", os.path.join(self._home_directory, file)])
        for line in xmp_lines + file_lines:
            self._extract_tag(line, photo)
        if not photo.title:
            raise RuntimeError(f"Title not found for photo {photo.file}")
        logging.info(f"Read photo: {photo}")
        return photo

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
