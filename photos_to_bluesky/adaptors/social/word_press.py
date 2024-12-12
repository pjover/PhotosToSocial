import base64
import mimetypes
import os
import os.path
from email.message import EmailMessage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from photos_to_bluesky.model.config import Config
from photos_to_bluesky.model.post import Post
from photos_to_bluesky.ports.isocialmedia import ISocialMedia

CATEGORY = "Foto"

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


# ❌ Google API with OAUTH: https://developers.google.com/gmail/api/guides/sending#python
# ❌ Google API (try with App password): https://developers.google.com/gmail/api/guides/sending#python
# ❓ Another option: https://mailtrap.io/blog/python-send-email-gmail/
# Sign in with app passwords: https://support.google.com/mail/answer/185833?hl=en
# WordPress Post by Email: https://wordpress.com/support/post-by-email/

class WordPress(ISocialMedia):
    def __init__(self, config: Config):
        self._home_directory = config.home_directory
        self._from = config.word_press_post_by_email_from
        self._to = config.word_press_post_by_email_to
        self._creds_file = self._creds(
            config.word_press_post_by_email_credentials_filename,
            config.word_press_post_by_email_token_filename,
        )

    def publish_post(self, post: Post):
        # create gmail api client
        service = build("gmail", "v1", credentials=self._creds)
        mime_message = EmailMessage()

        # headers
        mime_message["To"] = self._to
        mime_message["From"] = self._from
        mime_message["Subject"] = post.title

        # text
        content = f"{post.title}\n\n{post.text}\n[category {CATEGORY}][tags {','.join(post.keywords)}]"
        mime_message.set_content(post.text)

        for image in post.images:
            # attachment
            attachment_filename = os.path.join(self._home_directory, image.file)

            # guessing the MIME type
            type_subtype, _ = mimetypes.guess_type(attachment_filename)
            maintype, subtype = type_subtype.split("/")

            with open(attachment_filename, "rb") as fp:
                attachment_data = fp.read()
            mime_message.add_attachment(attachment_data, maintype, subtype)

        encoded_message = base64.urlsafe_b64encode(mime_message.as_bytes()).decode()

        create_message = {"raw": encoded_message}
        # pylint: disable=E1101
        send_message = (
            service.users()
            .messages()
            .send(userId="me", body=create_message)
            .execute()
        )
        print(f'Message Id: {send_message["id"]}')

    def build_file_part(file):
        """Creates a MIME part for a file.

        Args:
          file: The path to the file to be attached.

        Returns:
          A MIME part that can be attached to a message.
        """
        content_type, encoding = mimetypes.guess_type(file)

        if content_type is None or encoding is not None:
            content_type = "application/octet-stream"
        main_type, sub_type = content_type.split("/", 1)
        if main_type == "text":
            with open(file, "rb"):
                msg = MIMEText("r", _subtype=sub_type)
        elif main_type == "image":
            with open(file, "rb"):
                msg = MIMEImage("r", _subtype=sub_type)
        elif main_type == "audio":
            with open(file, "rb"):
                msg = MIMEAudio("r", _subtype=sub_type)
        else:
            with open(file, "rb"):
                msg = MIMEBase(main_type, sub_type)
                msg.set_payload(file.read())
        filename = os.path.basename(file)
        msg.add_header("Content-Disposition", "attachment", filename=filename)
        return msg

    def _creds(self, creds_filename, token_filename):
        _credentials_file = os.path.join(self._home_directory, creds_filename)
        _token_file = os.path.join(self._home_directory, token_filename)

        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(_token_file):
            creds = Credentials.from_authorized_user_file(_token_file, SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    _credentials_file,
                    SCOPES,
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(_token_file, "w") as token:
                token.write(creds.to_json())
        return creds
