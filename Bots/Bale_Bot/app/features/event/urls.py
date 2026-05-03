# app/features/event/urls.py

from __future__ import annotations

from typing import Any

from app.features.event.constants import BASE_BACKEND_URL, MEDIA_URL


def normalize_base_url(url: str) -> str:
    return url.rstrip("/")


def normalize_media_url(url: str) -> str:
    if not url:
        return "/media/"

    if not url.startswith("/"):
        url = f"/{url}"

    return url.rstrip("/") + "/"


def build_media_file_url(path: str) -> str:
    """
    path ممکن است یکی از این حالت‌ها باشد:
    - http://...
    - https://...
    - /media/events/covers/x.png
    - media/events/covers/x.png
    - events/covers/x.png

    خروجی:
    - URL کامل قابل استفاده برای answer_photo
    """
    base_url = normalize_base_url(BASE_BACKEND_URL)
    media_url = normalize_media_url(MEDIA_URL)

    path = (path or "").strip()

    if not path:
        return ""

    if path.startswith("http://") or path.startswith("https://"):
        return path

    if path.startswith(media_url):
        return f"{base_url}{path}"

    if path.startswith("/media/"):
        return f"{base_url}{path}"

    if path.startswith("media/"):
        return f"{base_url}/{path}"

    if path.startswith("/"):
        return f"{base_url}{path}"
    
    
    print("PHOTO URL =>", repr(f"{base_url}{media_url}{path}"))

    return f"{base_url}{media_url}{path}"


def get_event_cover_url(event: dict[str, Any]) -> str | None:
    """
    اولویت:
    1) cover_image_url
    2) cover_image
    """
    cover = event.get("cover_image_url") or event.get("cover_image")

    if not cover or not isinstance(cover, str):
        return None

    url = build_media_file_url(cover)
    print(f"url ============> {url}")
    

    return url or None
