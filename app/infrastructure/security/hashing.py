import hashlib
import os


class PasswordHasher:
    """Infrastructure service for hashing and verifying passwords."""

    @staticmethod
    def hash_password(password: str) -> str:
        salt = os.urandom(16).hex()
        hashed = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000
        ).hex()
        return f"{salt}${hashed}"

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        try:
            salt, stored_hash = hashed_password.split("$")
            new_hash = hashlib.pbkdf2_hmac(
                "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000
            ).hex()
            return new_hash == stored_hash
        except ValueError:
            return False
