import smtplib
from email.message import EmailMessage

from config.constants import Constants
from config.logger import get_logger


class SmtpClientAdapter:
    """SMTP client adapter for sending email notifications."""

    def __init__(self) -> None:
        self.logger = get_logger(__name__)
        self.host = Constants.SMTP_HOST
        self.port = Constants.SMTP_PORT
        self.user = Constants.SMTP_USER
        self.password = Constants.SMTP_PASSWORD
        self.sender = Constants.SMTP_FROM

    def send_email(self, recipients: list[str], subject: str, body: str) -> bool:
        if not recipients:
            self.logger.warning("No recipients provided for email")
            return False
        if not self.host or not self.port or not self.sender:
            self.logger.error("SMTP settings are not configured")
            return False

        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = self.sender
        message["To"] = ", ".join(recipients)
        message.set_content(body)

        try:
            with smtplib.SMTP(self.host, self.port) as server:
                server.starttls()
                if self.user and self.password:
                    server.login(self.user, self.password)
                server.send_message(message)
            self.logger.info("Notification email sent to %s", recipients)
            return True
        except Exception as exc:
            self.logger.error("Failed to send email: %s", exc)
            return False
