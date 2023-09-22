import time

from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Union, Any
import jwt
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days
ALGORITHM = "HS256"
JWT_SECRET_KEY = "TEST"  # should be kept secret
JWT_REFRESH_SECRET_KEY = "TEST"  # should be kept secret


def get_hashed_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(password: str, hashed_pass: str) -> bool:
    return password_context.verify(password, hashed_pass)


def create_access_token(subject: Union[str, Any]) -> str:
    """
    Generates an access token for the given subject.

    Args:
        subject (Union[str, Any]): The subject for which the access token is being generated.

    Returns:
        str: The generated access token.
    """
    expires_delta = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)
    return encoded_jwt


def create_refresh_token(subject: Union[str, Any]) -> str:
    """
    Generates a refresh token for the given subject.

    Args:
        subject (Union[str, Any]): The subject of the token.

    Returns:
        str: The encoded refresh token.
    """
    expires_delta = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expires_delta, "sub": {"refresh_for": str(subject)}}
    encoded_jwt = jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, ALGORITHM)
    return encoded_jwt


def decodeJWT(token: str) -> dict:
    """
    Decode a JSON Web Token (JWT) and return the decoded payload.

    Parameters:
        token (str): The JWT to be decoded.

    Returns:
        dict: The decoded payload as a dictionary, or an empty dictionary if decoding fails.
    """
    try:
        decoded_token = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_token if decoded_token["exp"] >= time.time() else None
    except:
        return {}


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        """
        Asynchronously processes a request by validating the JWT bearer token in the authorization header.

        Args:
            request (Request): The incoming request object.

        Returns:
            The JWT bearer token if it is valid and authorized.

        Raises:
            HTTPException: If the authentication scheme is not "Bearer" or if the token is invalid or expired.
        """
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=403, detail="Invalid token or expired token.")
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    def verify_jwt(self, jwtoken: str) -> bool:
        """
        Verify the validity of a JWT token.

        Parameters:
            jwtoken (str): The JWT token to be verified.

        Returns:
            bool: True if the JWT token is valid, False otherwise.
        """
        isTokenValid: bool = False

        try:
            payload = decodeJWT(jwtoken)
        except:
            payload = None
        if payload:
            isTokenValid = True
        return isTokenValid
