import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone

SECRET = os.getenv("GIA_AUTH_SECRET", "dev-only-change-me")


def validate_secret_configuration() -> None:
    """Fail closed in production if the token-signing key is a development default."""
    environment = os.getenv("GIA_ENV", "development").strip().lower()
    if environment in {"production", "prod"} and (
        SECRET == "dev-only-change-me" or len(SECRET) < 32
    ):
        raise RuntimeError(
            "GIA_AUTH_SECRET must be a unique random value of at least 32 characters in production"
        )


validate_secret_configuration()


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 120_000)
    return f"{salt}${digest.hex()}"

def verify_password(password: str, encoded: str) -> bool:
    try:
        salt, expected = encoded.split("$", 1)
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 120_000).hex()
        return hmac.compare_digest(actual, expected)
    except ValueError:
        return False

def issue_token(user_id: str, ttl_minutes: int = 60) -> str:
    # Signed opaque token; production should move to a dedicated session/token store.
    exp = int((datetime.now(timezone.utc) + timedelta(minutes=ttl_minutes)).timestamp())
    payload = f"{user_id}:{exp}"
    sig = hmac.new(SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}:{sig}"

def verify_token(token: str) -> str | None:
    try:
        user_id, exp, sig = token.rsplit(":", 2)
        payload = f"{user_id}:{exp}"
        expected = hmac.new(SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected) or int(exp) < int(datetime.now(timezone.utc).timestamp()):
            return None
        return user_id
    except Exception:
        return None
