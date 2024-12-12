from dataclasses import dataclass


@dataclass
class Config:
    home_directory: str
    posts_file: str
    blue_sky_username: str
    blue_sky_password: str
    word_press_post_by_email_from: str
    word_press_post_by_email_to: str
    word_press_post_by_email_credentials_filename: str
    word_press_post_by_email_token_filename: str
