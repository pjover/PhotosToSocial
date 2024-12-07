from dataclasses import dataclass


@dataclass
class Config:
    home_directory: str
    posts_file: str
    blue_sky_handle: str
    blue_sky_password: str
