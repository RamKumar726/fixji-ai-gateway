
import logging
import requests
from .config import settings


logger = logging.getLogger(__name__)

class Http_Client:

    def __init__(self):
        self.backend_url = settings.BACKEND_URL
        self.request_timeout = settings.REQUEST_TIMEOUT



    def _clean(self,params: dict | None) -> dict | None:
        """Drop empty params so we never send ?category_id=&subcategory_id="""
        if not params:
            return None
        cleaned = {k: v for k, v in params.items() if v not in ("", None)}
        return cleaned or None

    def api_get(self, path: str, params: dict | None = None):
        url = f"{self.backend_url}/{path.lstrip('/')}"
        params = self._clean(params)
        logger.info("GET %s params=%s", url, params)
        try:
            response = requests.get(url, params=params, timeout=self.request_timeout)
            if response.status_code == 200:
                return response.json()
            logger.warning("GET %s failed: %s %s", url, response.status_code, response.text)
            return {"success": False, "error": f"HTTP {response.status_code}", "details": response.text}
        except requests.exceptions.RequestException as e:
            logger.error("GET %s error: %s", url, e)
            return {"success": False, "error": str(e)}

    def api_post(self, path: str, payload: dict, headers: dict | None = None, timeout: int = 60):
        url = f"{self.backend_url}/{path.lstrip('/')}"
        logger.info("POST %s", url)
        try:
            response = requests.post(url, json=payload, headers=headers or {}, timeout=timeout)
            if response.status_code in (200, 201):
                return response.json()
            logger.warning("POST %s failed: %s %s", url, response.status_code, response.text)
            return {"success": False, "error": f"HTTP {response.status_code}", "details": response.text}
        except requests.exceptions.RequestException as e:
            logger.error("POST %s error: %s", url, e)
            return {"success": False, "error": str(e)}


http_client = Http_Client()