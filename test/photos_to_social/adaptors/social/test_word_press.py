from photos_to_social.adaptors.social.word_press import WordPress
from photos_to_social.model.post import Image, Post

_post_with_grouped_photos = Post(
    id="post0011",
    images=[
        Image(file="1.jpg", title="Image 1", width=100, height=100),
        Image(file="2.jpg", title="Image 2", width=200, height=200),
    ],
    caption="Caption",
    headline="Headline",
    keywords=["keyword1", "keyword2"],
    processed_on="2021-01-01T00:00:00",
    sent_on={
        "BlueSky": "2021-01-01T00:00:00",
        "WordPress": "2021-01-01T00:00:00",
    },
)

_post_with_single_photo = Post(
    id="post0011",
    images=[
        Image(file="1.jpg", title="Image 1", width=200, height=200),
    ],
    caption="",
    headline="Headline",
    keywords=["keyword1", "keyword2"],
    processed_on="2021-01-01T00:00:00",
    sent_on={
        "BlueSky": "2021-01-01T00:00:00",
        "WordPress": "2021-01-01T00:00:00",
    },
)

_post_with_single_photo_w_caption_wo_headline = Post(
    id="post0011",
    images=[
        Image(file="1.jpg", title="Image 1", width=200, height=200),
    ],
    caption="Caption",
    headline="",
    keywords=["keyword1", "keyword2"],
    processed_on="2021-01-01T00:00:00",
    sent_on={
        "BlueSky": "2021-01-01T00:00:00",
        "WordPress": "2021-01-01T00:00:00",
    },
)

_post_with_single_photo_w_caption_and_headline = Post(
    id="post0011",
    images=[
        Image(file="1.jpg", title="Image 1", width=200, height=200),
    ],
    caption="Caption",
    headline="Headline",
    keywords=["keyword1", "keyword2"],
    processed_on="2021-01-01T00:00:00",
    sent_on={
        "BlueSky": "2021-01-01T00:00:00",
        "WordPress": "2021-01-01T00:00:00",
    },
)

_post_with_grouped_photos_wo_headline = Post(
    id="post0011",
    images=[
        Image(file="1.jpg", title="Image 1", width=100, height=100),
        Image(file="2.jpg", title="Image 2", width=200, height=200),
    ],
    caption="Caption",
    headline="",
    keywords=["keyword1", "keyword2"],
    processed_on="2021-01-01T00:00:00",
    sent_on={
        "BlueSky": "2021-01-01T00:00:00",
        "WordPress": "2021-01-01T00:00:00",
    },
)

_post_with_single_photo_wo_headline = Post(
    id="post0011",
    images=[
        Image(file="1.jpg", title="Image 1", width=200, height=200),
    ],
    caption="",
    headline="",
    keywords=["keyword1", "keyword2"],
    processed_on="2021-01-01T00:00:00",
    sent_on={
        "BlueSky": "2021-01-01T00:00:00",
        "WordPress": "2021-01-01T00:00:00",
    },
)


def test_build_subject_for_post_with_grouped_photos():
    actual = WordPress.build_subject(_post_with_grouped_photos)
    assert actual == "Caption"


def test_build_subject_for_post_with_single_photo():
    actual = WordPress.build_subject(_post_with_single_photo)
    assert actual == "Image 1"


def test_build_text_for_post_with_grouped_photos():
    actual = WordPress.build_text(_post_with_grouped_photos)
    assert actual == (
        'Caption\n'
        '\n'
        '- Image 1\n'
        '- Image 2\n'
        '\n'
        'Headline\n'
        '\n'
        '\n'
        '[category Foto]\n'
        '[tags keyword1,keyword2]\n'
        '[status publish]'
    )


def test_build_text_for_post_with_single_photo():
    actual = WordPress.build_text(_post_with_single_photo)
    assert actual == (
        'Image 1\n'
        '\n'
        'Headline\n'
        '\n'
        '\n'
        '[category Foto]\n'
        '[tags keyword1,keyword2]\n'
        '[status publish]'
    )


def test_build_subject_for_post_with_grouped_photos_wo_headline():
    actual = WordPress.build_subject(_post_with_grouped_photos_wo_headline)
    assert actual == "Caption"


def test_build_subject_for_post_with_single_photo_wo_headline():
    actual = WordPress.build_subject(_post_with_single_photo_wo_headline)
    assert actual == "Image 1"


def test_build_text_for_post_with_grouped_photos_wo_headline():
    actual = WordPress.build_text(_post_with_grouped_photos_wo_headline)
    assert actual == (
        'Caption\n'
        '\n'
        '- Image 1\n'
        '- Image 2\n'
        '\n'
        '\n'
        '[category Foto]\n'
        '[tags keyword1,keyword2]\n'
        '[status publish]'
    )


def test_build_text_for_post_with_single_photo_wo_headline():
    actual = WordPress.build_text(_post_with_single_photo_wo_headline)
    assert actual == (
        'Image 1\n'
        '\n'
        '\n'
        '[category Foto]\n'
        '[tags keyword1,keyword2]\n'
        '[status publish]'
    )


def test_build_text_for_post_with_single_photo_w_caption_and_headline():
    actual = WordPress.build_text(_post_with_single_photo_w_caption_and_headline)

    assert actual == (
        'Caption\n'
        '\n'
        'Image 1\n'
        '\n'
        'Headline\n'
        '\n'
        '\n'
        '[category Foto]\n'
        '[tags keyword1,keyword2]\n'
        '[status publish]'
    )


def test_build_text_for_post_with_single_photo_w_caption_wo_headline():
    actual = WordPress.build_text(_post_with_single_photo_w_caption_wo_headline)

    assert actual == (
        'Caption\n'
        '\n'
        'Image 1\n'
        '\n'
        '\n'
        '[category Foto]\n'
        '[tags keyword1,keyword2]\n'
        '[status publish]'
    )
