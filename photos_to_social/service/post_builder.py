import logging
from collections import defaultdict
from datetime import datetime
from typing import List

from photos_to_social.model.photo import Photo
from photos_to_social.model.post import Post, Image


class PostBuilder:

    def group_photos_into_posts(self, photos: List[Photo]) -> List[Post]:
        grouped_photos = defaultdict(list)
        for photo in photos:
            if photo.caption:
                grouped_photos[photo.caption].append(photo)
            else:
                grouped_photos[photo.id].append(photo)

        posts = []
        for title, grouped_photos in grouped_photos.items():
            if len(grouped_photos) == 1:
                if not grouped_photos[0].title:
                    raise ValueError(f"Photo {grouped_photos[0].id} has no title.")
                posts.append(self._post_from_photo(grouped_photos[0]))
            else:
                posts.append(self._merge(grouped_photos))

        posts = sorted(posts, key=lambda x: x.id)
        if not posts:
            logging.info("No new posts.")
        else:
            logging.info(f"Found {len(posts)} new posts:")
            for post in posts:
                logging.info(f" - {post}")
        return posts

    def _post_from_photo(self, photo: Photo) -> Post:
        if photo.order:
            _id = photo.order
        else:
            _id = str(photo.id)

        return Post(
            id=_id,
            images=[self._image(photo)],
            caption=photo.caption,
            headline=photo.headline,
            keywords=photo.keywords,
            processed_on=datetime.now().isoformat(),
            sent_on=""
        )

    @staticmethod
    def _image(photo: Photo) -> Image:
        return Image(
            file=photo.file,
            title=photo.title,
            width=photo.width,
            height=photo.height
        )

    def _merge(self, photos: List[Photo]) -> Post:
        # The post is built from the first photo
        post = self._post_from_photo(photos[0])

        for photo in photos[1:]:
            # Add image
            post.images.append(self._image(photo))
            # Merge keywords
            post.keywords = self._unique_items(post.keywords, photo.keywords)

        return post

    @staticmethod
    def _unique_items(items_left: List[str], items_right: List[str]) -> List[str]:
        unique_items = []
        for item in items_left + items_right:
            if item not in unique_items:
                unique_items.append(item)
        return unique_items
