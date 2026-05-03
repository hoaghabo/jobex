from app.infrastructure.backend.client import BackendClient


client = BackendClient()


async def get_my_registered_events(bale_user_id: int):
    return await client.get(
        "api/bot/my-events/",
        params={"bale_user_id": bale_user_id},
    )



