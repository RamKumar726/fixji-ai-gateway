from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

bearer_scheme = HTTPBearer(description="Fixji customer JWT from /auth/login")


def get_token(creds: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> str:
    return creds.credentials