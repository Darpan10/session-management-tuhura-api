import requests
from config import settings


class MailService:

    @staticmethod
    # def send_email(to: str, subject: str, text: str):
    def send_email(subject: str, text: str):
        """Send an email through Mailgun API"""

        # Build Mailgun endpoint
        url = f"{settings.mailgun_base_url}/{settings.mailgun_domain}/messages"

        # Auth uses API key from .env
        auth = ("api", settings.mailgun_api_key)

        data = {
            "from": "postmaster@sandbox22a538fa42b349959ca958e7f30a4257.mailgun.org",
            "to": "techtuhura@gmail.com",
            "subject": subject,
            "text": text
        }

        response = requests.post(url, auth=auth, data=data)

        if response.status_code != 200:
            raise Exception(f"Mailgun error: {response.status_code} - {response.text}")

        return response.json()
