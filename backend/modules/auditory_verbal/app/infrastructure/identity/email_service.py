from app.core.logging import logger


class EmailService:
    """Mock/log service simulating sending system emails for accounts registration and verification."""

    @staticmethod
    async def send_verification_email(email: str, token: str) -> None:
        logger.info(f"[EMAIL SERVICE] Verification email sent to '{email}' with verification token: {token}")

    @staticmethod
    async def send_password_reset_email(email: str, token: str) -> None:
        logger.info(f"[EMAIL SERVICE] Password reset instruction sent to '{email}' with reset token: {token}")
