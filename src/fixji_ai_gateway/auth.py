import requests

from .config import settings

BACKEND_URL = settings.BACKEND_URL

def login_with_credentials(identifier: str, password: str) -> str:
    r = requests.post(
        f"{BACKEND_URL}/api/auth/login",
        json={"identifier": identifier, "password": password},
        timeout=60,
    )
    r.raise_for_status()
    data = r.json()
    token = data.get("token") or data.get("accessToken")
    if not token:
        raise RuntimeError(f"No token in login response keys: {list(data.keys())}")
    return token