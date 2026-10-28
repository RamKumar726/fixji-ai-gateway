import requests
from fastapi import APIRouter, HTTPException

from ..auth import login_with_credentials
from ..schemas import LoginRequest, LoginResponse

router = APIRouter(prefix="/auth", tags=["auth"])


# plain `def` so FastAPI runs the blocking `requests` call in a threadpool
@router.post("/login", response_model=LoginResponse)
def login(body: LoginRequest):
    try:
        token = login_with_credentials(body.identifier, body.password)
    except requests.HTTPError as e:
        status = e.response.status_code if e.response is not None else 502
        if status in (400, 401, 403):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        raise HTTPException(status_code=502, detail="Fixji backend login failed")
    except (requests.RequestException, RuntimeError):
        raise HTTPException(status_code=502, detail="Could not reach Fixji backend")
    return LoginResponse(token=token)