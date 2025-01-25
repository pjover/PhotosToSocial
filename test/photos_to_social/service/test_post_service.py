from unittest import mock
from unittest.mock import MagicMock
from unittest.mock import call, Mock

import pytest

from photos_to_social.model.config import Config
from photos_to_social.model.post import Post, Image
from photos_to_social.ports.isocialmedia import ISocialMedia
from photos_to_social.ports.istorage import IStorage
from photos_to_social.service.post_service import PostService


@pytest.fixture
def post() -> Post:
    return Post(
        id="post0011",
        images=[
            Image(file="1.jpg", title="Image 1", width=200, height=200),
        ],
        caption="Caption",
        headline="",
        keywords=["keyword1", "keyword2"],
        processed_on="2021-01-01T00:00:00",
        sent_on={},
    )


@pytest.fixture
def config() -> Config:
    return Config(
        home_directory="test",
        posts_file="test",
        blue_sky_username="test",
        blue_sky_password="test",
        gmail_user_email="test",
        gmail_app_password="test",
        word_press_post_by_email_to="test",
    )


@pytest.fixture
def storage(post) -> IStorage:
    mock = Mock(speck=IStorage)
    mock.read_next_post = MagicMock(return_value=post)
    return mock


@pytest.fixture
def ok_social_media() -> ISocialMedia:
    mock = Mock(speck=ISocialMedia)
    mock.name = MagicMock(return_value="ok_social_media")
    return mock


@pytest.fixture
def ok2_social_media() -> ISocialMedia:
    mock = Mock(speck=ISocialMedia)
    mock.name = MagicMock(return_value="ok2_social_media")
    return mock


@pytest.fixture
def ko_social_media() -> ISocialMedia:
    mock = Mock(speck=ISocialMedia)
    mock.name = MagicMock(return_value="ko_social_media")
    mock.publish_post = MagicMock(side_effect=Exception("Failed to publish post"))
    return mock


def test_run_with_failing_social_media(post, config, storage, ok_social_media, ko_social_media):
    post_service = PostService(config, storage, [ok_social_media, ko_social_media])

    with (mock.patch("photos_to_social.service.post_service.logging") as mocked_logging):
        post_service.run()
    storage.update.assert_called_once()

    mocked_logging.debug.assert_has_calls(
        [
            call("Published post `post0011` to ok_social_media")
        ]
    )
    mocked_logging.error.assert_has_calls(
        [
            call("Failed to publish post `post0011` to ko_social_media: Failed to publish post")
        ]
    )


def test_run_with_non_failing_social_media(post, config, storage, ok_social_media, ok2_social_media):
    post_service = PostService(config, storage, [ok_social_media, ok2_social_media])

    with (mock.patch("photos_to_social.service.post_service.logging") as mocked_logging):
        post_service.run()

    mocked_logging.debug.assert_has_calls(
        [
            call("Published post `post0011` to ok_social_media"),
            call("Published post `post0011` to ok2_social_media"),
        ]
    )
