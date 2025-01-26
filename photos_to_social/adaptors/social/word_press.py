import logging
import os
import os.path
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from photos_to_social.model.config import Config
from photos_to_social.model.post import Post
from photos_to_social.ports.social_media import SocialMedia

CATEGORY = "Foto"
STATUS = "publish"


# How to Send Emails in Python with Gmail SMTP and API: https://mailtrap.io/blog/python-send-email-gmail/
# Sign in with app passwords: https://support.google.com/mail/answer/185833?hl=en
# WordPress Post by Email: https://wordpress.com/support/post-by-email/

class WordPress(SocialMedia):
    def __init__(self, config: Config):
        self._home_directory = config.home_directory
        self._gmail_account = config.gmail_user_email
        self._gmail_app_password = config.gmail_app_password
        self._to = config.word_press_post_by_email_to

    def name(self) -> str:
        return "WordPress"

    def publish_post(self, post: Post):
        logging.info(f"Publishing post `{post.id}` to WordPress ...")

        message = MIMEMultipart()
        message['Subject'] = self.build_subject(post)
        message['From'] = self._gmail_account
        message['To'] = self._to

        text = self.build_text(post)
        html_part = MIMEText(text)
        message.attach(html_part)

        for image in post.images:
            file = os.path.join(self._home_directory, image.file)
            with open(file, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename= {image.file}",
                )
                message.attach(part)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(self._gmail_account, self._gmail_app_password)
            server.sendmail(self._gmail_account, self._to, message.as_string())

        logging.info(f"Published post `{post.id}` to WordPress")

    @staticmethod
    def build_subject(post: Post) -> str:
        if post.caption:
            return post.caption
        else:
            return post.images[0].title

    @staticmethod
    def build_text(post: Post) -> str:
        text = ""
        if post.caption:
            text += f"{post.caption}\n\n"
        if len(post.images) > 1:
            for image in post.images:
                if image.title:
                    text += f"- {image.title}\n"
            text += "\n"
        else:
            text += f"{post.images[0].title}\n\n"

        if post.headline:
            text += f"{post.headline}\n\n"

        keywords = ','.join(post.keywords)

        return f"{text}\n[category {CATEGORY}]\n[tags {keywords}]\n[status {STATUS}]"
