from pydantic import BaseModel


class Config(BaseModel):
    home_directory: str
    posts_file: str
    blue_sky_username: str
    blue_sky_password: str
    email_user_email: str
    email_app_password: str
    email_smtp_server: str
    email_smtp_port: int
    word_press_post_by_email_to: str
