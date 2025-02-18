from datetime import datetime
from fastapi import HTTPException, Header, Security, status
from fastapi.security import APIKeyHeader

from app import constants
from app.libs.storage.json_storage import JsonStorage

api_key_header = APIKeyHeader(name='Authorization', auto_error=True)


def verify_token(api_key: str = Security(api_key_header)):
    """
    Verifies the provided token against a stored API token.
    Returns:
        str: The verified token if it matches the stored API token.
    Raises:
        HTTPException: If the provided token does not match the stored API token.
    """
    tokens = (JsonStorage(constants.API_TOKEN_PATH).get_object() or {})
    if not (tokens.get(api_key) and tokens[api_key]['expiry'] > int(datetime.now().timestamp())):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=constants.INVALID_TOKEN
        )

    return api_key
