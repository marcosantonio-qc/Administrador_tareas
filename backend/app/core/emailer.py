from __future__ import annotations
import smtplib
from email.mime.text import MIMEText
import logging
from app.core.config import get_settings

logger = logging.getLogger(__name__)


def send_email(subject: str, body: str, to_address: str) -> None:
    settings = get_settings()
    if not settings.smtp_host or not settings.smtp_user or not settings.smtp_password:
        logger.info("SMTP not configured; skipping email to %s: %s", to_address, subject)
        return

    msg = MIMEText(body, _charset="utf-8")
    msg["Subject"] = subject
    msg["From"] = settings.smtp_from
    msg["To"] = to_address

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.starttls()
        server.login(settings.smtp_user, settings.smtp_password)
        server.sendmail(settings.smtp_from, [to_address], msg.as_string())
