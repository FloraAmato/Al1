"""
Email service using SMTP and template rendering.
"""
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
from typing import Dict

from app.core.config import settings


class EmailService:
    """Service for sending emails using templates."""

    def __init__(self):
        """Initialize email service with template engine."""
        template_dir = Path(__file__).parent.parent / "templates" / "email"
        template_dir.mkdir(parents=True, exist_ok=True)

        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(["html", "xml"]),
        )

    async def send_email(
        self,
        to_email: str,
        subject: str,
        template_name: str,
        context: Dict[str, str],
    ) -> bool:
        """
        Send an email using a template.

        Args:
            to_email: Recipient email address
            subject: Email subject
            template_name: Template file name (without .html)
            context: Variables to substitute in template

        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Render template
            template = self.env.get_template(f"{template_name}.html")
            html_content = template.render(**context)

            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{settings.MAIL_FROM_NAME} <{settings.MAIL_FROM}>"
            message["To"] = to_email

            # Attach HTML content
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)

            # Send email
            await aiosmtplib.send(
                message,
                hostname=settings.MAIL_SERVER,
                port=settings.MAIL_PORT,
                username=settings.MAIL_USERNAME or settings.MAILJET_API_KEY,
                password=settings.MAIL_PASSWORD or settings.MAILJET_API_SECRET,
                use_tls=settings.MAIL_TLS,
            )

            return True

        except Exception as e:
            print(f"Error sending email: {e}")
            return False

    async def send_verification_email(self, to_email: str, username: str, verification_url: str) -> bool:
        """Send email verification email."""
        return await self.send_email(
            to_email=to_email,
            subject="Verify your CREA2 account",
            template_name="verify_email",
            context={
                "username": username,
                "verification_url": verification_url,
            },
        )

    async def send_password_reset_email(self, to_email: str, username: str, reset_url: str) -> bool:
        """Send password reset email."""
        return await self.send_email(
            to_email=to_email,
            subject="Reset your CREA2 password",
            template_name="reset_password",
            context={
                "username": username,
                "reset_url": reset_url,
            },
        )

    async def send_agent_invitation_email(
        self,
        to_email: str,
        dispute_name: str,
        invitation_url: str,
        is_new_user: bool = False,
    ) -> bool:
        """Send agent invitation email."""
        template = "invite_new_agent" if is_new_user else "invite_agent"
        subject = "Invitation to participate in a dispute on CREA2"

        return await self.send_email(
            to_email=to_email,
            subject=subject,
            template_name=template,
            context={
                "dispute_name": dispute_name,
                "invitation_url": invitation_url,
            },
        )
