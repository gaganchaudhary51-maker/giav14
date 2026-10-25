import hmac

from fastapi import HTTPException, status


def verify_voice_webhook_auth(authorization: str | None, token: str, app_env: str) -> None:
    """Validate webhook bearer auth and fail closed when production is misconfigured."""
    if not token:
        if app_env.casefold() == "production":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Voice webhook authentication is not configured",
            )
        return
    expected = f"Bearer {token}"
    if authorization is None or not hmac.compare_digest(authorization, expected):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid webhook credentials")
