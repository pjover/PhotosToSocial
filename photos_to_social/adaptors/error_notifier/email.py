import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from photos_to_social.model.config import Config
from photos_to_social.ports.error_notifier import ErrorNotifier


class EmailErrorNotifier(ErrorNotifier):
    def __init__(self, config: Config):
        self._email_account = config.email_user_email
        self._email_app_password = config.email_app_password
        self._email_smtp_server = config.email_smtp_server
        self._email_smtp_port = config.email_smtp_port
        self._to = self._email_account

    def notify(self, title: str, error: str):
        logging.error(f"{title}`: {error}")

        message = MIMEMultipart()
        message['Subject'] = title
        message['From'] = self._email_account
        message['To'] = self._email_account

        text = error
        html_part = MIMEText(text)
        message.attach(html_part)

        with smtplib.SMTP_SSL(self._email_smtp_server, self._email_smtp_port) as server:
            server.login(self._email_account, self._email_app_password)
            server.sendmail(self._email_account, self._to, message.as_string())

        logging.debug("Sent error by email")
