from dataclasses import dataclass


@dataclass
class Config:
    home_directory: str
    posts_file: str
    blue_sky_username: str
    blue_sky_password: str
    gmail_account: str
    gmail_app_password: str
    word_press_post_by_email_to: str
