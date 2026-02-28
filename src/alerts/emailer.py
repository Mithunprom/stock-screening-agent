from __future__ import annotations

import smtplib
from email.message import EmailMessage

from src.config import AppConfig
from src.utils.logging import get_logger

logger = get_logger(__name__)


class Emailer:
    def __init__(self, settings: AppConfig) -> None:
        self.settings = settings

    def send(self, subject: str, body: str, dry_run: bool = False) -> None:
        if dry_run or self.settings.email.dry_run_default or not self._smtp_configured():
            print(f"Subject: {subject}\n\n{body}")
            return
        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = self.settings.email.email_from
        message["To"] = ", ".join(self.settings.email.email_to)
        message.set_content(body)
        with smtplib.SMTP(self.settings.email.smtp_host, self.settings.email.smtp_port, timeout=30) as smtp:
            smtp.starttls()
            smtp.login(self.settings.email.smtp_user, self.settings.email.smtp_pass)
            smtp.send_message(message)
        logger.info("Email sent: %s", subject)

    def _smtp_configured(self) -> bool:
        return all(
            [
                self.settings.email.smtp_host,
                self.settings.email.smtp_user,
                self.settings.email.smtp_pass,
                self.settings.email.email_from,
                self.settings.email.email_to,
            ]
        )

