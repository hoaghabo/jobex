import os
import requests


BALE_API_BASE = "https://tapi.bale.ai/bot"


def extract_bale_photo_file_id(result: dict) -> str | None:
    photo = result.get("photo")

    if isinstance(photo, list) and photo:
        return photo[-1].get("file_id")

    if isinstance(photo, dict):
        return photo.get("file_id")

    return None


def upload_event_cover_to_bale(event) -> dict | None:
    token = os.getenv("BALE_BOT_TOKEN")
    chat_id = os.getenv("BALE_CACHE_CHAT_ID")

    if not token:
        print("BALE_BOT_TOKEN is not set")
        return None

    if not chat_id:
        print("BALE_CACHE_CHAT_ID is not set")
        return None

    if not event.cover_image:
        print(f"Event {event.id} has no cover_image")
        return None

    if not getattr(event.cover_image, "path", None):
        print(f"Event {event.id} cover_image has no local path")
        return None

    url = f"{BALE_API_BASE}{token}/sendPhoto"

    try:
        with open(event.cover_image.path, "rb") as photo_file:
            response = requests.post(
                url,
                data={
                    "chat_id": chat_id,
                    "caption": f"Event #{event.id} - {event.title}",
                },
                files={
                    "photo": photo_file,
                },
                timeout=30,
            )

        try:
            data = response.json()
        except Exception:
            print("Bale response is not JSON:", response.text)
            return None

        if not response.ok or not data.get("ok"):
            print("Bale upload failed:", data)
            return None

        result = data.get("result", {})
        file_id = extract_bale_photo_file_id(result)
        message_id = result.get("message_id")

        if not file_id:
            print("Could not extract file_id from Bale response:", data)
            return None

        return {
            "file_id": file_id,
            "message_id": message_id,
            "raw": data,
        }

    except Exception as e:
        print("Upload event cover to Bale error:", repr(e))
        return None
