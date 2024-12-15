from pydantic import BaseModel


class Config(BaseModel):
    home_directory: str
    posts_file: str
    blue_sky_username: str
    blue_sky_password: str
    gmail_user_email: str
    gmail_app_password: str
    word_press_post_by_email_to: str
