from collections import defaultdict
from datetime import datetime
from typing import List

from photos_to_bluesky.model.image import Image, NO_GROUP
from photos_to_bluesky.model.post import Post


class PostBuilder:

    def group_images_into_posts(self, images: List[Image]) -> List[Post]:
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
                posts.append(self._merge(images))

        posts = sorted(posts, key=lambda post: post.id)
        if not posts:
            print("No new posts.")
        else:
            print(f"Found {len(posts)} new posts:")
            for post in posts:
                print(f" - {post}")
        return posts

    def _post_from_image(self, image: Image) -> Post:
        text = []
        text_content = self._build_text(image)
        if text_content:
            text.append(text_content)

        return Post(
            id=image.id,
            images=[image.file],
            text=text,
            group=image.group,
            keywords=image.keywords,
            processed_on=datetime.now().isoformat(),
            scheduled_on=""
        )

    def _merge(self, images: List[Image]) -> Post:
        post = self._post_from_image(images[0])
        if post.text[0]:
            post.text[0] += "."
        for img in images[1:]:
            post.images.append(img.file)
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
