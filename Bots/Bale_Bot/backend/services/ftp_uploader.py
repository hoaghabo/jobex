from ftplib import FTP, all_errors
from urllib.parse import urljoin
import posixpath

from django.conf import settings


def _get_required_setting(name):
    value = getattr(settings, name, None)
    if value in [None, ""]:
        raise ValueError(f"Missing required setting: {name}")
    return value


def _normalize_remote_path(remote_path):
    # FTP paths should use forward slash
    remote_path = remote_path.replace("\\", "/")
    remote_path = remote_path.strip("/")
    return remote_path


def upload_file_to_download_host(local_path, remote_path):
    if not getattr(settings, "ENABLE_DOWNLOAD_FTP", False):
        return None

    host = _get_required_setting("DOWNLOAD_FTP_HOST")
    user = _get_required_setting("DOWNLOAD_FTP_USER")
    password = _get_required_setting("DOWNLOAD_FTP_PASS")
    public_base_url = _get_required_setting("DOWNLOAD_PUBLIC_BASE_URL")

    port = int(getattr(settings, "DOWNLOAD_FTP_PORT", 21))

    # خیلی مهم: host نباید protocol یا path داشته باشد
    if host.startswith("http://") or host.startswith("https://") or host.startswith("ftp://"):
        raise ValueError(
            "DOWNLOAD_FTP_HOST must be only hostname or IP, "
            "without http://, https://, ftp://"
        )

    if "/" in host:
        raise ValueError(
            "DOWNLOAD_FTP_HOST must not contain path. "
            "Example: ftp.example.com"
        )

    remote_path = _normalize_remote_path(remote_path)

    ftp = None

    try:
        ftp = FTP()
        ftp.connect(host=host, port=port, timeout=20)
        ftp.login(user=user, passwd=password)
        ftp.set_pasv(True)

        directories = remote_path.split("/")[:-1]

        # ساخت فولدرها یکی‌یکی
        for directory in directories:
            if not directory:
                continue

            try:
                ftp.cwd(directory)
            except all_errors:
                ftp.mkd(directory)
                ftp.cwd(directory)

        filename = remote_path.split("/")[-1]

        with open(local_path, "rb") as f:
            ftp.storbinary(f"STOR {filename}", f)

        public_url = urljoin(public_base_url.rstrip("/") + "/", remote_path)

        return public_url

    except all_errors as e:
        raise RuntimeError(f"FTP upload failed: {e}") from e

    finally:
        if ftp is not None:
            try:
                ftp.quit()
            except Exception:
                pass
