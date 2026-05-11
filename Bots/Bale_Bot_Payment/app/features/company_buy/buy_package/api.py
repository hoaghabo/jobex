from urllib.parse import urlencode

from app.infrastructure.backend.client import BackendClient
from app.infrastructure.backend.client import BackendAPIError
from app.config import settings


client = BackendClient()

PRODUCTS_ENDPOINT = "/api/billing/products/"


def _build_bot_headers() -> dict:
    return {
        "X-Bot-Token": settings.BACKEND_BOT_API_TOKEN,
        "Content-Type": "application/json",
    }


def _build_query_params(params: dict) -> str:
    clean_params = {
        key: value
        for key, value in params.items()
        if value is not None and value != ""
    }

    if not clean_params:
        return ""

    return "?" + urlencode(clean_params)


def _normalize_products_response(response):
    if isinstance(response, list):
        return response

    if isinstance(response, dict):
        if isinstance(response.get("results"), list):
            return response["results"]

        if isinstance(response.get("data"), list):
            return response["data"]

        if isinstance(response.get("products"), list):
            return response["products"]

    print("فرمت response محصولات نامعتبر است:", response)
    return []


async def get_products(
    category=None,
    category_slug=None,
    product_type=None,
    type_code=None,
    status=None,
    is_active=True,
    is_public=True,
):
    params = {
        "category": category,
        "product_type": product_type,
        "category_slug": category_slug,
        "type_code": type_code,
        "status": status,
        "is_active": is_active,
        "is_public": is_public,
    }

    url = PRODUCTS_ENDPOINT + _build_query_params(params)

    try:
        response = await client.get(
            url,
            headers=_build_bot_headers(),
        )
        return _normalize_products_response(response)

    except BackendAPIError as e:
        print("خطا در دریافت لیست محصولات")
        print("message:", e.message)
        print("status:", e.status_code)
        print("body:", e.body)
        return []

    except Exception as e:
        print(f"خطای غیرمنتظره در دریافت محصولات: {str(e)}")
        return []


async def get_company_products():
    products = await get_products(is_active=True, is_public=True)
    print(products)

    return [
        product for product in products
        if product.get("product_type", {}).get("code") == "employer_package"
    ]
