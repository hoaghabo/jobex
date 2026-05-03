from __future__ import annotations

import asyncio
import os
import posixpath
import uuid
from ftplib import FTP, FTP_TLS
from pathlib import Path
from urllib.parse import quote, urlparse


FTP_HOST = os.getenv("DOWNLOAD_FTP_HOST", "")
FTP_PORT = int(os.getenv("DOWNLOAD_FTP_PORT", "21"))
FTP_USERNAME = os.getenv("DOWNLOAD_FTP_USERNAME", "")
FTP_PASSWORD = os.getenv("DOWNLOAD_FTP_PASSWORD", "")
FTP_BASE_DIR = os.getenv("DOWNLOAD_FTP_BASE_DIR", "/public_html")
PUBLIC_BASE_URL = os.getenv("DOWNLOAD_PUBLIC_BASE_URL", "").rstrip("/")
FTP_USE_TLS = os.getenv("DOWNLOAD_FTP_USE_TLS", "false").lower() == "true"


class FTPUploadError(Exception):
    pass


def _parse_ftp_host(host: str) -> tuple[str, int]:
    """
    ورودی‌های قابل قبول:
    ftp.example.com
    ftp://ftp.example.com
    ftp://ftp.example.com:21
    """
    if not host:
        raise FTPUploadError("FTP host is empty.")

    if "://" not in host:
        return host, FTP_PORT

    parsed = urlparse(host)

    if not parsed.hostname:
        raise FTPUploadError(f"Invalid FTP host: {host}")

    return parsed.hostname, parsed.port or FTP_PORT


def _ensure_remote_dirs(ftp: FTP, remote_dir: str) -> None:
    """
    مسیر ریموت را مرحله‌به‌مرحله می‌سازد و واردش می‌شود.
    مثلا:
    /public_html/events/covers
    """
    parts = [part for part in remote_dir.strip("/").split("/") if part]

    if remote_dir.startswith("/"):
        try:
            ftp.cwd("/")
        except Exception:
            pass

    for part in parts:
        try:
            ftp.cwd(part)
        except Exception:
            try:
                ftp.mkd(part)
            except Exception:
                pass
            ftp.cwd(part)


def _build_public_url(filename: str) -> str:
    if not PUBLIC_BASE_URL:
        raise FTPUploadError("DOWNLOAD_PUBLIC_BASE_URL is empty.")

    safe_filename = quote(filename)
    return f"{PUBLIC_BASE_URL}/{safe_filename}"


def _upload_file_to_download_host_sync(
    local_file_path: str | Path,
    filename: str | None = None,
) -> str:
    local_file_path = Path(local_file_path)

    if not local_file_path.exists():
        raise FTPUploadError(f"Local file does not exist: {local_file_path}")

    if not local_file_path.is_file():
        raise FTPUploadError(f"Local path is not a file: {local_file_path}")

    host, port = _parse_ftp_host(FTP_HOST)

    if not FTP_USERNAME or not FTP_PASSWORD:
        raise FTPUploadError("FTP username/password is empty.")

    suffix = local_file_path.suffix.lower()

    if filename is None:
        filename = f"{uuid.uuid4().hex}{suffix}"

    # برای جلوگیری از مسیر خطرناک
    filename = Path(filename).name

    if FTP_USE_TLS:
        ftp = FTP_TLS()
    else:
        ftp = FTP()

    try:
        ftp.connect(host=host, port=port, timeout=30)
        ftp.login(user=FTP_USERNAME, passwd=FTP_PASSWORD)

        if FTP_USE_TLS and isinstance(ftp, FTP_TLS):
            ftp.prot_p()

        ftp.set_pasv(True)

        _ensure_remote_dirs(ftp, FTP_BASE_DIR)

        with local_file_path.open("rb") as file_obj:
            ftp.storbinary(f"STOR {filename}", file_obj)

        return _build_public_url(filename)

    except Exception as e:
        raise FTPUploadError(f"FTP upload failed: {repr(e)}") from e

    finally:
        try:
            ftp.quit()
        except Exception:
            try:
                ftp.close()
            except Exception:
                pass


async def upload_file_to_download_host(
    local_file_path: str | Path,
    filename: str | None = None,
) -> str:
    """
    نسخه async برای استفاده داخل aiogram.
    خروجی: لینک عمومی فایل
    """
    return await asyncio.to_thread(
        _upload_file_to_download_host_sync,
        local_file_path,
        filename,
    )
