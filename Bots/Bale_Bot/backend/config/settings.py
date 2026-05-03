from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BASE_DIR.parent

load_dotenv(ROOT_DIR / ".env")

SECRET_KEY = os.getenv("SECRET_KEY", "unsafe-dev-secret-key")

DEBUG = os.getenv("DEBUG", "False") == "True"

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "rest_framework",

    "users",
    "reports",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DATABASE_NAME", "hamkhan_bot"),
        "USER": os.getenv("DATABASE_USER", "postgres"),
        "PASSWORD": os.getenv("DATABASE_PASSWORD", "postgres"),
        "HOST": os.getenv("DATABASE_HOST", "localhost"),
        "PORT": os.getenv("DATABASE_PORT", "5432"),
    }
}

LANGUAGE_CODE = "fa-ir"

TIME_ZONE = "Asia/Tehran"

USE_I18N = True

USE_TZ = True

STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

BALE_BOT_TOKEN = os.getenv("BALE_BOT_TOKEN")
BALE_API_BASE_URL = os.getenv("BALE_API_BASE_URL")


ADMIN_USER_IDS = [
    int(x)
    for x in os.getenv("ADMIN_USER_IDS", "").split(",")
    if x.strip()
]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"



from decouple import config, Csv

ZARINPAL_MERCHANT_ID = config("ZARINPAL_MERCHANT_ID")

ZARINPAL_REQUEST_URL = config(
    "ZARINPAL_REQUEST_URL",
    default="https://api.zarinpal.com/pg/v4/payment/request.json",
)

ZARINPAL_VERIFY_URL = config(
    "ZARINPAL_VERIFY_URL",
    default="https://api.zarinpal.com/pg/v4/payment/verify.json",
)

ZARINPAL_STARTPAY_URL = config(
    "ZARINPAL_STARTPAY_URL",
    default="https://www.zarinpal.com/pg/StartPay",
)

BACKEND_BASE_URL = config("BACKEND_BASE_URL")
BALE_BOT_TOKEN = config("BALE_BOT_TOKEN", default="")


DOWNLOAD_FTP_HOST = os.getenv("DOWNLOAD_FTP_HOST")
DOWNLOAD_FTP_PORT = int(os.getenv("DOWNLOAD_FTP_PORT", "21"))
DOWNLOAD_FTP_USER = os.getenv("DOWNLOAD_FTP_USER")
DOWNLOAD_FTP_PASS = os.getenv("DOWNLOAD_FTP_PASS")
DOWNLOAD_PUBLIC_BASE_URL = os.getenv("DOWNLOAD_PUBLIC_BASE_URL")
ENABLE_DOWNLOAD_FTP = os.getenv("ENABLE_DOWNLOAD_FTP", "False") == "True"
DOWNLOAD_FTP_HOST = os.getenv("DOWNLOAD_FTP_HOST")