import os
import os.path
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from photos_to_bluesky.model.config import Config
from photos_to_bluesky.model.post import Post
from photos_to_bluesky.ports.isocialmedia import ISocialMedia

CATEGORY = "Foto"
STATUS = "publish"


# How to Send Emails in Python with Gmail SMTP and API: https://mailtrap.io/blog/python-send-email-gmail/
# Sign in with app passwords: https://support.google.com/mail/answer/185833?hl=en
# WordPress Post by Email: https://wordpress.com/support/post-by-email/

class WordPress(ISocialMedia):
    def __init__(self, config: Config):
        self._home_directory = config.home_directory
        self._gmail_account = config.gmail_user_email
        self._gmail_app_password = config.gmail_app_password
        self._to = config.word_press_post_by_email_to

    def publish_post(self, post: Post):
        message = MIMEMultipart()
        message['Subject'] = post.title
        message['From'] = self._gmail_account
        message['To'] = self._to
        body = f"{post.text}\n[category {CATEGORY}]\n[tags {','.join(post.keywords)}]\n[status {STATUS}]"
        html_part = MIMEText(body)
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
