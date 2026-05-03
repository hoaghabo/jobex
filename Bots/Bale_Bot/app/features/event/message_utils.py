from __future__ import annotations

from urllib.parse import urlparse

from aiogram.types import InputMediaPhoto
from aiogram.exceptions import TelegramBadRequest, TelegramServerError


PHOTO_CAPTION_LIMIT = 1024


def is_public_url(url: str | None) -> bool:
    if not url:
        return False

    url = url.strip()
    parsed = urlparse(url)

    return (
        parsed.scheme in ("http", "https")
        and bool(parsed.netloc)
        and parsed.hostname not in ("127.0.0.1", "localhost")
    )


async def ensure_public_photo_url(photo_url: str | None) -> str | None:
    """
    این تابع دیگر هیچ آپلودی انجام نمی‌دهد.

    فقط URL عمومی را قبول می‌کند.
    اگر بک‌اند URL لوکال یا خالی بدهد، عکس نمایش داده نمی‌شود.
    """
    if not photo_url:
        return None

    photo_url = photo_url.strip()

    if is_public_url(photo_url):
        return photo_url

    print("NON PUBLIC PHOTO URL IGNORED =>", repr(photo_url))
    return None


async def safe_delete_message(message):
    try:
        await message.delete()
        return True
    except Exception as e:
        print("SAFE DELETE ERROR =>", repr(e))
        return False


def is_not_modified_error(error: Exception) -> bool:
    return "message is not modified" in str(error).lower()


def message_has_media(message) -> bool:
    return bool(
        getattr(message, "photo", None)
        or getattr(message, "video", None)
        or getattr(message, "document", None)
        or getattr(message, "animation", None)
    )


async def safe_edit_event_message(
    callback,
    text,
    reply_markup=None,
    photo_url=None,
    photo_file_id=None,
):
    message = callback.message
    if not message:
        return

    try:
        # اولویت با file_id
        if photo_file_id:
            # اگر پیام فعلی عکس‌دار است
            if getattr(message, "photo", None):
                try:
                    await message.edit_caption(
                        caption=text,
                        reply_markup=reply_markup,
                        parse_mode="Markdown",
                    )
                    return
                except Exception:
                    pass

            # fallback: حذف و ارسال مجدد
            try:
                await message.delete()
            except Exception:
                pass

            await callback.message.answer_photo(
                photo=photo_file_id,
                caption=text,
                reply_markup=reply_markup,
                parse_mode="Markdown",
            )
            return

        # اگر file_id نبود ولی url هست
        if photo_url:
            if getattr(message, "photo", None):
                try:
                    await message.edit_caption(
                        caption=text,
                        reply_markup=reply_markup,
                        parse_mode="Markdown",
                    )
                    return
                except Exception:
                    pass

            try:
                await message.delete()
            except Exception:
                pass

            await callback.message.answer_photo(
                photo=photo_url,
                caption=text,
                reply_markup=reply_markup,
                parse_mode="Markdown",
            )
            return

        # متن ساده
        if getattr(message, "photo", None):
            try:
                await message.delete()
            except Exception:
                pass

            await callback.message.answer(
                text=text,
                reply_markup=reply_markup,
                parse_mode="Markdown",
            )
            return

        await message.edit_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode="Markdown",
        )

    except Exception as e:
        print("ERROR safe_edit_event_message:", e)

        try:
            await callback.message.answer(
                text=text,
                reply_markup=reply_markup,
                parse_mode="Markdown",
            )
        except Exception as inner_e:
            print("ERROR safe_edit_event_message fallback:", inner_e)
