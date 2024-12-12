from collections import defaultdict
from datetime import datetime
from typing import List

from photos_to_bluesky.model.photo import Photo, NO_GROUP
from photos_to_bluesky.model.post import Post, Image


class PostBuilder:

    def group_photos_into_posts(self, photos: List[Photo]) -> List[Post]:
        grouped_photos = defaultdict(list)
        for photo in photos:
            grouped_photos[photo.group].append(photo)

        posts = []
        for group, photos in grouped_photos.items():
            if group == NO_GROUP:
                for photo in photos:
                    posts.append(self._post_from_photo(photo))
            elif len(photos) == 1:
                posts.append(self._post_from_photo(photos[0]))
            else:
                posts.append(self._merge(photos))

        posts = sorted(posts, key=lambda post: post.id)
        if not posts:
            print("No new posts.")
        else:
            print(f"Found {len(posts)} new posts:")
            for post in posts:
                print(f" - {post}")
        return posts

    @staticmethod
    def _post_from_photo(photo: Photo) -> Post:

        image = Image(
            file=photo.file,
            alt=photo.title,
            width=int(photo.width),
            height=int(photo.height)
        )

        return Post(
            id=photo.id,
            images=[image],
            title=photo.title,
            text=photo.caption,
            group=photo.group,
            keywords=photo.keywords,
            processed_on=datetime.now().isoformat(),
            sent_on=""
        )

    def _merge(self, photos: List[Photo]) -> Post:
        post = self._post_from_photo(photos[0])
        if post.text[0]:
            post.text[0] += "."
        for photo in photos[1:]:
            image = Image(
                file=photo.file,
                alt=photo.title,
                width=photo.width,
                height=photo.height
            )
            post.images.append(image)
            text = self._build_text(photo)
            if text:
                post.text.append(text + ".")
            post.keywords = self._unique_keywords(post.keywords, photo.keywords)
        return post

    @staticmethod
    def _unique_keywords(keywords_left: List[str], keywords_right: List[str]) -> List[str]:
        unique_keywords = []
        for keyword in keywords_left + keywords_right:
            if keyword not in unique_keywords:
                unique_keywords.append(keyword)
        return unique_keywords
