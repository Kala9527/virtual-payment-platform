from dataclasses import dataclass
from datetime import datetime
from email.message import EmailMessage
import smtplib
from pathlib import Path

from app.core.config import Settings


@dataclass(frozen=True)
class EmailSendResult:
    sent: bool
    channel: str


class EmailService:
    def __init__(self, settings: Settings):
        self.settings = settings

    def send_payment_confirmation(self, recipient: str, subject: str, body: str) -> EmailSendResult:
        if self.settings.smtp_host:
            self._send_smtp(recipient, subject, body)
            return EmailSendResult(sent=True, channel="smtp")

        self._write_outbox(recipient, subject, body)
        return EmailSendResult(sent=True, channel="local_outbox")

    def _send_smtp(self, recipient: str, subject: str, body: str) -> None:
        message = EmailMessage()
        message["From"] = str(self.settings.smtp_from_email)
        message["To"] = recipient
        message["Subject"] = subject
        message.set_content(body)

        with smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port, timeout=15) as smtp:
            if self.settings.smtp_use_tls:
                smtp.starttls()
            if self.settings.smtp_username and self.settings.smtp_password:
                smtp.login(self.settings.smtp_username, self.settings.smtp_password)
            smtp.send_message(message)

    def _write_outbox(self, recipient: str, subject: str, body: str) -> None:
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
        safe_recipient = recipient.replace("@", "_at_").replace(".", "_")
        path: Path = self.settings.outbox_dir / f"{timestamp}_{safe_recipient}.txt"
        path.write_text(
            f"To: {recipient}\nSubject: {subject}\n\n{body}\n",
            encoding="utf-8",
        )

