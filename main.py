import json
import os
import subprocess
from typing import List
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime

xmp_tags_to_store = {
    "Title": "title",
    "Description": "caption",
    "Subject Code": "group",
    "Subject ": "keywords",
}

NO_GROUP = "NO_GROUP"

@dataclass
class Image:
    """Class for keeping track of an image read from a file"""
    path: str
    title: str = ""
    caption: str = ""
    group: str = NO_GROUP
    keywords: List[str] = list

@dataclass
class Post:
    """Class for keeping track of a post"""
    images: List[str]
    text: List[str]
    group: str
    keywords: List[str]
    processed_on: str
    scheduled_on: str

    def __str__(self):
        return f"{self.text}, {self.group}, {self.keywords}, {self.images}, {self.processed_on}, {self.scheduled_on}"


class PhotosToBuffer:
    _posts_file: str
    _input_directory: str

    def __init__(self, posts_file: str, input_directory: str):
        self._posts_file = self._check_file(posts_file)
        self._input_directory = self._check_directory(input_directory)

    @staticmethod
    def _check_directory(directory: str) -> str:
        if not os.path.isdir(directory):
            raise RuntimeError(f"Error: '{directory}' is not a valid directory.")
        print(f"Processing files in directory: `{directory}`")
        return directory

    @staticmethod
    def _check_file(images_file: str) -> str:
        if not os.path.isfile(images_file):
            raise RuntimeError(f"Error: '{images_file}' is not a valid file.")
        return images_file

    def _load_stored_posts(self) -> List[Post]:
        _images = []
        with open(self._posts_file, "r") as file:
            for line in file:
                image_data = json.loads(line)
                _images.append(Post(**image_data))
        return _images

    def _store_posts(self, images: List[Post]):
        with open(self._posts_file, "w") as file:
            for image in images:
                json.dump(image.__dict__, file)
                file.write("\n")

    def run(self):
        stored_posts = self._load_stored_posts()
        new_images = self._read_new_images(stored_posts)
        # for post in new_images:
        #     print(f"- {post}")
        posts = self._group_images_into_posts(new_images)
        for post in posts:
            print(f"- {post}")

        # self._store_posts(stored_posts + posts)

    def _read_new_images(self, stored_posts: List[Post]) -> List[Image]:
        images = []
        for root, dirs, files in os.walk(self._input_directory):
            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg')):
                    images.append(self._read_image(os.path.join(root, file)))
        return images

    def _read_image(self, input_file: str) -> Image:
        image = Image(path=input_file)
        lines = self._command(["exiftool", "-XMP:all", input_file])
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

    def _group_images_into_posts(self, images: List[Image]) -> List[Post]:
        grouped_images = defaultdict(list)
        for img in images:
            grouped_images[img.group].append(img)

        posts = []
        for group, images in grouped_images.items():
            if group == NO_GROUP:
                for img in images:
                    posts.append(self._post_from_image(img))
            elif len(images) == 1:
                posts.append(self._post_from_image(images[0]))
            else:
                posts.append(self._merge_posts(images))
        return posts

    def _post_from_image(self, image: Image) -> Post:
        text = []
        text_content = self._build_text(image)
        if text_content:
            text.append(text_content)

        return Post(
            images=[image.path],
            text=text,
            group=image.group,
            keywords=image.keywords,
            processed_on=datetime.now().isoformat(),
            scheduled_on=""
        )

    def _merge_posts(self, images: List[Image]) -> Post:
        post = self._post_from_image(images[0])
        if post.text[0]:
            post.text[0] += "."
        for img in images[1:]:
            post.images.extend(img.path)
            text = self._build_text(img)
            if text:
                post.text.append(text + ".")
            post.keywords = self._unique_keywords(post.keywords, img.keywords)
        return post

    @staticmethod
    def _build_text(image: Image) -> str:
        if image.title and image.caption:
            return f"{image.title}. {image.caption}."
        elif image.title:
            return image.title
        elif image.caption:
            return image.caption
        else:
            return ""

    @staticmethod
    def _unique_keywords(keywords_left: List[str], keywords_right: List[str]) -> List[str]:
        unique_keywords = []
        for keyword in keywords_left + keywords_right:
            if keyword not in unique_keywords:
                unique_keywords.append(keyword)
        return unique_keywords


if __name__ == "__main__":
    # Configure your input and output directories here
    inputDirectory = "/Users/pere/Downloads/exported"  # Change this path as needed

    PhotosToBuffer("/Users/pere/Downloads/exported/posts.jsonl", "/Users/pere/Downloads/exported").run()
