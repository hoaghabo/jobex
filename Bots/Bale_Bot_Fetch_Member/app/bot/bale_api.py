from aiogram.client.telegram import TelegramAPIServer

BALE_API = TelegramAPIServer(
    base="https://tapi.bale.ai/bot{token}/{method}",
    file="https://tapi.bale.ai/file/bot{token}/{path}",
)
