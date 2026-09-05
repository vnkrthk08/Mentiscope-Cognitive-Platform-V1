import bcrypt


class PasswordHasher:
    """Utility service wrapping raw bcrypt for secure password hashing and verification.
    Bypasses deprecated passlib to avoid Python 3.14/bcrypt compatibility bugs.
    """

    @staticmethod
    def hash_password(password: str) -> str:
        if not password or not password.strip():
            raise ValueError("Password cannot be empty.")
        # Ensure password is under bcrypt length limit (72 bytes)
        pwd_bytes = password.encode("utf-8")[:72]
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(pwd_bytes, salt)
        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        if not plain_password or not hashed_password:
            return False
        try:
            pwd_bytes = plain_password.encode("utf-8")[:72]
            hash_bytes = hashed_password.encode("utf-8")
            return bcrypt.checkpw(pwd_bytes, hash_bytes)
        except Exception:
            return False
