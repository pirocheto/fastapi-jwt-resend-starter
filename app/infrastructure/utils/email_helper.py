import logging
from dataclasses import dataclass
from typing import Any

import resend
from jinja2 import Environment, FileSystemLoader

from app.core.config import settings

logger = logging.getLogger(__name__)

BASE_DIR = settings.app_dir

resend.api_key = settings.RESEND_API_KEY


@dataclass
class EmailData:
    subject: str
    html_content: str = ""
    raw_content: str = ""


TEMPLATE_DIRS = {
    "html": BASE_DIR / "infrastructure/templates/html",
    "raw": BASE_DIR / "infrastructure/templates/raw",
}


envs = {
    "html": Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIRS["html"])),
        autoescape=True,
    ),
    "raw": Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIRS["raw"])),
        autoescape=False,
    ),
}


def render_email_template(template_name: str, context: dict[str, Any], template_type: str) -> str:
    env = envs[template_type]
    template = env.get_template(template_name)
    return template.render(context)


def send_email(*, email_to: str, subject: str = "", html_content: str = "", raw_content: str = "") -> None:
    assert settings.emails_enabled, "no provided configuration for email variables"

    params: resend.Emails.SendParams = {
        "from": f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>",
        "to": [email_to],
        "subject": subject,
        "html": html_content,
        "text": raw_content,
    }

    resend.Emails.send(params)


def generate_verification_email(*, email_to: str, token: str) -> EmailData:
    link = f"{settings.FRONTEND_HOST}/verify-email?token={token}"
    context = {
        "email": email_to,
        "username": email_to,
        "link": link,
        "expiration_hours": settings.VERIFICATION_TOKEN_EXPIRE_HOURS,
        "project_name": settings.PROJECT_NAME,
    }
    html_content = render_email_template(
        template_name="verify_email.html",
        context=context,
        template_type="html",
    )
    raw_content = render_email_template(
        template_name="verify_email.txt",
        context=context,
        template_type="raw",
    )
    subject = "Email Address Verification"

    return EmailData(
        subject=subject,
        html_content=html_content,
        raw_content=raw_content,
    )


def generate_password_reset_email(*, email_to: str, token: str) -> EmailData:
    link = f"{settings.FRONTEND_HOST}/reset-password?token={token}"
    context = {
        "email": email_to,
        "username": email_to,
        "link": link,
        "expiration_hours": settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS,
        "project_name": settings.PROJECT_NAME,
    }
    html_content = render_email_template(
        template_name="reset_password.html",
        context=context,
        template_type="html",
    )
    raw_content = render_email_template(
        template_name="reset_password.txt",
        context=context,
        template_type="raw",
    )
    subject = "Password Reset Request"

    return EmailData(
        subject=subject,
        html_content=html_content,
        raw_content=raw_content,
    )
