import aiohttp
from typing import Any, Optional

from app.config import settings


class BackendAPIError(Exception):
    pass


class BackendClient:
    def __init__(self, base_url: Optional[str] = None, timeout: int = 10):
        self.base_url = (base_url or settings.BACKEND_BASE_URL).rstrip("/")
        self.timeout = aiohttp.ClientTimeout(total=timeout)

    def _make_url(self, endpoint: str) -> str:
        endpoint = endpoint.lstrip("/")
        return f"{self.base_url}/{endpoint}"

    async def _request(
        self,
        method: str,
        endpoint: str,
        *,
        params: dict | None = None,
        json: dict | None = None,
        data: Any = None,
        headers: dict | None = None,
    ) -> Any:
        url = self._make_url(endpoint)

        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.request(
                    method=method.upper(),
                    url=url,
                    params=params,
                    json=json,
                    data=data,
                    headers=headers,
                ) as response:
                    content_type = response.headers.get("Content-Type", "")

                    if response.status >= 400:
                        try:
                            error_body = await response.json()
                        except Exception:
                            error_body = await response.text()

                        raise BackendAPIError(
                            f"Backend request failed | "
                            f"method={method.upper()} url={url} "
                            f"status={response.status} body={error_body}"
                        )

                    if "application/json" in content_type:
                        return await response.json()

                    return await response.text()

        except aiohttp.ClientError as e:
            raise BackendAPIError(f"Connection error while calling {url}: {e}") from e

    async def get(
        self,
        endpoint: str,
        *,
        params: dict | None = None,
        headers: dict | None = None,
    ) -> Any:
        return await self._request(
            "GET",
            endpoint,
            params=params,
            headers=headers,
        )

    async def get_raw(
        self,
        endpoint: str,
        *,
        params: dict | None = None,
        headers: dict | None = None,
    ) -> bytes:
        url = self._make_url(endpoint)

        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(
                    url,
                    params=params,
                    headers=headers,
                ) as response:
                    if response.status >= 400:
                        try:
                            error_body = await response.json()
                        except Exception:
                            error_body = await response.text()

                        raise BackendAPIError(
                            f"Backend raw request failed | "
                            f"method=GET url={url} "
                            f"status={response.status} body={error_body}"
                        )

                    return await response.read()

        except aiohttp.ClientError as e:
            raise BackendAPIError(f"Connection error while calling {url}: {e}") from e

    async def post(
        self,
        endpoint: str,
        *,
        json: dict | None = None,
        data: Any = None,
        headers: dict | None = None,
        params: dict | None = None,
    ) -> Any:
        return await self._request(
            "POST",
            endpoint,
            json=json,
            data=data,
            headers=headers,
            params=params,
        )

    async def put(
        self,
        endpoint: str,
        *,
        json: dict | None = None,
        data: Any = None,
        headers: dict | None = None,
        params: dict | None = None,
    ) -> Any:
        return await self._request(
            "PUT",
            endpoint,
            json=json,
            data=data,
            headers=headers,
            params=params,
        )

    async def patch(
        self,
        endpoint: str,
        *,
        json: dict | None = None,
        data: Any = None,
        headers: dict | None = None,
        params: dict | None = None,
    ) -> Any:
        return await self._request(
            "PATCH",
            endpoint,
            json=json,
            data=data,
            headers=headers,
            params=params,
        )

    async def delete(
        self,
        endpoint: str,
        *,
        headers: dict | None = None,
        params: dict | None = None,
    ) -> Any:
        return await self._request(
            "DELETE",
            endpoint,
            headers=headers,
            params=params,
        )
