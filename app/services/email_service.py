import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import resend
from jinja2 import Environment, FileSystemLoader

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class EmailData:
    subject: str
    html_content: str = ""
    raw_content: str = ""


resend.api_key = settings.RESEND_API_KEY


TEMPLATE_DIRS = {
    "html": Path("app/email-templates/html/build"),
    "raw": Path("app/email-templates/raw"),
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

    response = resend.Emails.send(params)
    logger.info(f"send email result: {response}")


def generate_verification_email(
    *,
    email_to: str,
    username: str,
    token: str,
) -> EmailData:
    link = f"{settings.FRONTEND_HOST}/verify-email?token={token}"
    context = {
        "email": email_to,
        "username": username,
        "link": link,
        "expiration_hours": settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS,
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
    subject = "Vérification de votre adresse email"

    return EmailData(
        subject=subject,
        html_content=html_content,
        raw_content=raw_content,
    )


def generate_password_reset_email(
    *,
    email_to: str,
    username: str,
    token: str,
) -> EmailData:
    link = f"{settings.FRONTEND_HOST}/reset-password?token={token}"
    context = {
        "email": email_to,
        "username": username,
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
    subject = "Réinitialisation de votre mot de passe"

    return EmailData(
        subject=subject,
        html_content=html_content,
        raw_content=raw_content,
    )
