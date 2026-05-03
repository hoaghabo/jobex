import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    BALE_BOT_TOKEN = os.getenv("BALE_BOT_TOKEN", "")
    BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "")
    BACKEND_BOT_API_TOKEN = os.getenv("BACKEND_BOT_API_TOKEN", "")

    BOT_USER_ENTRY_ENDPOINT = os.getenv("BOT_USER_ENTRY_ENDPOINT", "/api/bot/user/entry/")
    BOT_USER_STATUS_ENDPOINT = os.getenv("BOT_USER_STATUS_ENDPOINT", "/api/bot/user/status/")
    BALE_PAYMENT_PROVIDER_TOKEN = os.getenv("BALE_PAYMENT_PROVIDER_TOKEN", "")
    


settings = Settings()
