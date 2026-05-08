# Hamkhan Bale Bot

یک فریم‌ورک سبک، تمیز و feature-based برای ساخت ربات بله با Python.

این پروژه به شکلی طراحی شده که بتوانید هر قابلیت ربات را به صورت جداگانه در قالب Feature توسعه دهید؛ مثل:

- `/start`
- ثبت‌نام چندمرحله‌ای
- راهنما
- ارسال عکس
- ارسال فایل
- دکمه‌های معمولی
- دکمه‌های inline
- مدیریت state کاربر
- مدیریت data موقت کاربر

---

## ساختار پروژه
```text
hamkhan_bot/
│
├── bot/
│   ├── core/
│   │   ├── engine.py
│   │   ├── dispatcher.py
│   │   ├── router.py
│   │   ├── middleware/
│   │   │   └── state_middleware.py
│   │   ├── state/
│   │   │   ├── context.py
│   │   │   ├── storage.py
│   │   │   └── state.py
│   │   ├── messenger.py
│   │   ├── client.py
│   │   ├── poller.py
│   │   ├── parser.py
│   │   └── message.py
│   │
│   ├── features/
│   │   ├── public/
│   │   │   ├── start/
│   │   │   │   ├── handlers.py
│   │   │   │   └── router.py
│   │   │   ├── register/
│   │   │   │   ├── handlers.py
│   │   │   │   └── router.py
│   │   │   └── help/
│   │   │       ├── handlers.py
│   │   │       └── router.py
│   │   └── router.py
│   │
│   ├── utils/
│   │   ├── logger.py
│   │   └── keyboards.py
│   │
│   ├── config.py
│   └── run_bot.py
│
├── requirements.txt
├── .env.example
└── README.md

---

## نصب

ابتدا محیط مجازی بسازید:

bash
python -m venv .venv

در لینوکس یا مک:

bash
source .venv/bin/activate

در ویندوز:

bash
.venv\Scripts\activate

سپس پکیج‌ها را نصب کنید:

bash
pip install -r requirements.txt

---

## تنظیمات

یک فایل `.env` در ریشه پروژه بسازید.

می‌توانید از فایل نمونه کپی بگیرید:

bash
cp .env.example .env

محتوای نمونه:

env
BALE_BOT_TOKEN=your_bale_bot_token
BALE_API_BASE_URL=https://tapi.bale.ai

POLLING_TIMEOUT=30
POLLING_LIMIT=50

USE_REDIS=false
REDIS_URL=redis://localhost:6379/0

LOG_LEVEL=INFO

مقدار `BALE_BOT_TOKEN` را با توکن ربات بله خودتان جایگزین کنید.

---

## اجرا

از ریشه پروژه اجرا کنید:

bash
python -m bot.run_bot

روش زیر توصیه نمی‌شود:

bash
python bot/run_bot.py

چون ممکن است importها به مشکل بخورند.

---

# مفاهیم اصلی پروژه

## Message چیست؟

هر پیام دریافتی از بله بعد از parse شدن به یک آبجکت داخلی به نام `Message` تبدیل می‌شود.

نمونه استفاده:

python
ctx.message.text
ctx.message.chat_id
ctx.message.user_id
ctx.message.command
ctx.message.args

مثلاً اگر کاربر بفرستد:

text
/register ali

مقدارها:

python
ctx.message.command  # "/register"
ctx.message.args     # "ali"

---

## Context چیست؟

`Context` آبجکت اصلی داخل handlerهاست.

در هر handler معمولاً با `ctx` کار می‌کنید.

مثال:

python
async def my_handler(ctx: Context) -> None:
await ctx.reply("سلام")

امکانات اصلی `ctx`:

python
ctx.text
ctx.chat_id
ctx.user_id
ctx.message
ctx.messenger
ctx.storage

متدهای مهم:

python
await ctx.reply("متن پیام")
await ctx.get_state()
await ctx.set_state(state)
await ctx.clear_state()
await ctx.get_data()
await ctx.set_data({...})
await ctx.update_data(name="Ali")
await ctx.clear_data()
await ctx.finish()

---

# ارسال پیام ساده

داخل هر handler:

python
async def hello_handler(ctx: Context) -> None:
await ctx.reply("سلام، خوش آمدی")

---

# تعریف command handler

برای هندل کردن دستورهایی مثل `/start` یا `/help` باید در فایل `router.py` همان feature route تعریف کنید.

مثال:

python
from bot.core.router import Router
from .handlers import start_handler

router = Router()

router.command("/start")(start_handler)

یا:

python
router.command("start")(start_handler)

هر دو حالت کار می‌کند.

---

# تعریف text handler

اگر بخواهید روی متن خاصی واکنش بدهید:

python
router.text("ثبت‌نام")(register_start_handler)

مثلاً اگر کاربر پیام زیر را بفرستد:

text
ثبت‌نام

تابع `register_start_handler` اجرا می‌شود.

---

# تعریف fallback handler

اگر هیچ routeای match نشود، fallback اجرا می‌شود.

در فایل:

text
bot/features/router.py

مثال:

python
@main_router.fallback()
async def fallback_handler(ctx):
await ctx.reply(
"متوجه پیام شما نشدم.\n"
"برای شروع از دستور /start استفاده کن."
)

---

# اضافه کردن دکمه معمولی یا Reply Keyboard

برای ساخت دکمه‌های معمولی از تابع `reply_keyboard` استفاده کنید.

فایل:

python
bot/utils/keyboards.py

نمونه:

python
from bot.utils.keyboards import reply_keyboard

keyboard = reply_keyboard([
["ثبت‌نام"],
["راهنما", "درباره ما"],
])

ارسال همراه پیام:

python
await ctx.reply(
"یکی از گزینه‌های زیر را انتخاب کن:",
reply_markup=keyboard,
)

خروجی برای کاربر:

text
[ ثبت‌نام ]
[ راهنما ] [ درباره ما ]

---

## مثال کامل دکمه معمولی

python
from bot.core.state.context import Context
from bot.utils.keyboards import reply_keyboard


async def menu_handler(ctx: Context) -> None:
keyboard = reply_keyboard([
["ثبت‌نام"],
["راهنما", "پشتیبانی"],
])

await ctx.reply(
"منوی اصلی:",
reply_markup=keyboard,
)

router:

python
router.command("/menu")(menu_handler)

---

# حذف دکمه‌های معمولی

اگر بخواهید کیبورد از صفحه کاربر حذف شود:

python
from bot.utils.keyboards import remove_keyboard

await ctx.reply(
"کیبورد حذف شد.",
reply_markup=remove_keyboard(),
)

---

# اضافه کردن دکمه Inline

دکمه inline دکمه‌ای است که زیر پیام نمایش داده می‌شود.

نمونه:

python
from bot.utils.keyboards import inline_keyboard

keyboard = inline_keyboard([
[
{"text": "سایت", "url": "https://example.com"}
],
[
{"text": "ثبت‌نام", "callback_data": "register"}
]
])

ارسال:

python
await ctx.reply(
"یکی از گزینه‌ها را انتخاب کن:",
reply_markup=keyboard,
)

> نکته: در نسخه پایه این فریم‌ورک، دریافت و هندل کردن `callback_query` هنوز پیاده‌سازی نشده است.  
> ولی ارسال inline keyboard با `url` یا `callback_data` قابل انجام است.  
> برای هندل callback باید parser و message model توسعه داده شوند.

---

# انواع دکمه‌ها

## 1. دکمه معمولی متنی

python
reply_keyboard([
["ثبت‌نام"],
["راهنما"]
])

این نوع دکمه در واقع متن را برای ربات ارسال می‌کند.  
پس می‌توانید با `router.text` آن را هندل کنید:

python
router.text("ثبت‌نام")(register_start_handler)

---

## 2. دکمه لینک‌دار inline

python
inline_keyboard([
[
{
"text": "ورود به سایت",
"url": "https://example.com"
}
]
])

---

## 3. دکمه callback inline

python
inline_keyboard([
[
{
"text": "تایید",
"callback_data": "confirm"
}
]
])

برای هندل callback لازم است پشتیبانی callback به فریم‌ورک اضافه شود.

---

# مدیریت State

State برای زمانی استفاده می‌شود که کاربر در یک فرآیند چندمرحله‌ای قرار دارد.

مثلاً ثبت‌نام:

1. گرفتن نام
2. گرفتن سن
3. گرفتن شهر

برای هر مرحله یک state تعریف می‌کنیم.

---

## تعریف State

در فایل handler:

python
from bot.core.state.state import State

REGISTER_NAME = State(feature="register", step="name")
REGISTER_AGE = State(feature="register", step="age")
REGISTER_CITY = State(feature="register", step="city")

---

## ست کردن State

python
await ctx.set_state(REGISTER_NAME)

---

## گرفتن State فعلی

python
state = await ctx.get_state()

---

## پاک کردن State

python
await ctx.clear_state()

---

## پاک کردن State و Data با هم

python
await ctx.finish()

این متد هر دو مورد زیر را پاک می‌کند:

python
state
data

---

# ذخیره data موقت کاربر

در طول فرآیند چندمرحله‌ای می‌توانید data موقت ذخیره کنید.

مثلاً بعد از گرفتن نام:

python
await ctx.update_data(name="Ali")

بعد از گرفتن سن:

python
await ctx.update_data(age=22)

دریافت data:

python
data = await ctx.get_data()

مثال:

python
name = data.get("name")
age = data.get("age")

پاک کردن data:

python
await ctx.clear_data()

---

# مثال کامل ثبت‌نام چندمرحله‌ای

## `bot/features/public/register/handlers.py`

python
from bot.core.state.context import Context
from bot.core.state.state import State
from bot.utils.keyboards import remove_keyboard


REGISTER_NAME = State(feature="register", step="name")
REGISTER_AGE = State(feature="register", step="age")
REGISTER_CITY = State(feature="register", step="city")


async def register_start_handler(ctx: Context) -> None:
await ctx.clear_data()
await ctx.set_state(REGISTER_NAME)

await ctx.reply(
"فرآیند ثبت‌نام شروع شد.\n\n"
"لطفاً نام و نام خانوادگی خود را وارد کن:",
reply_markup=remove_keyboard(),
)


async def register_name_handler(ctx: Context) -> None:
name = ctx.text.strip()

if len(name) < 3:
await ctx.reply("نام واردشده خیلی کوتاه است. لطفاً دوباره وارد کن:")
return

await ctx.update_data(name=name)
await ctx.set_state(REGISTER_AGE)

await ctx.reply("سن خود را وارد کن:")


async def register_age_handler(ctx: Context) -> None:
text = ctx.text.strip()

if not text.isdigit():
await ctx.reply("سن باید عدد باشد. لطفاً دوباره وارد کن:")
return

age = int(text)

if age < 7 or age > 120:
await ctx.reply("سن واردشده معتبر نیست. لطفاً دوباره وارد کن:")
return

await ctx.update_data(age=age)
await ctx.set_state(REGISTER_CITY)

await ctx.reply("شهر محل سکونت خود را وارد کن:")


async def register_city_handler(ctx: Context) -> None:
city = ctx.text.strip()

if len(city) < 2:
await ctx.reply("نام شهر معتبر نیست. لطفاً دوباره وارد کن:")
return

data = await ctx.update_data(city=city)

await ctx.finish()

await ctx.reply(
"ثبت‌نام شما با موفقیت انجام شد ✅\n\n"
f"نام: {data.get('name')}\n"
f"سن: {data.get('age')}\n"
f"شهر: {data.get('city')}"
)

---

## `bot/features/public/register/router.py`

python
from bot.core.router import Router
from bot.features.public.register.handlers import (
REGISTER_AGE,
REGISTER_CITY,
REGISTER_NAME,
register_age_handler,
register_city_handler,
register_name_handler,
register_start_handler,
)


router = Router()

router.text("ثبت‌نام")(register_start_handler)
router.command("/register")(register_start_handler)

router.state(REGISTER_NAME)(register_name_handler)
router.state(REGISTER_AGE)(register_age_handler)
router.state(REGISTER_CITY)(register_city_handler)

---

# اضافه کردن Feature جدید

مثلاً می‌خواهیم feature جدیدی به نام `profile` بسازیم.

ساختار:

text
bot/features/public/profile/
├── handlers.py
└── router.py

---

## مرحله 1: ساخت handlers

فایل:

text
bot/features/public/profile/handlers.py

کد:

python
from bot.core.state.context import Context


async def profile_handler(ctx: Context) -> None:
await ctx.reply(
"پروفایل شما هنوز تکمیل نشده است."
)

---

## مرحله 2: ساخت router

فایل:

text
bot/features/public/profile/router.py

کد:

python
from bot.core.router import Router
from bot.features.public.profile.handlers import profile_handler


router = Router()

router.command("/profile")(profile_handler)
router.text("پروفایل")(profile_handler)

---

## مرحله 3: include کردن router

در فایل:

text
bot/features/router.py

اضافه کنید:

python
from bot.features.public.profile.router import router as profile_router

و بعد:

python
main_router.include_router(profile_router)

نمونه کامل:

python
from bot.core.router import Router

from bot.features.public.start.router import router as start_router
from bot.features.public.help.router import router as help_router
from bot.features.public.register.router import router as register_router
from bot.features.public.profile.router import router as profile_router


main_router = Router()

main_router.include_router(start_router)
main_router.include_router(help_router)
main_router.include_router(register_router)
main_router.include_router(profile_router)


@main_router.fallback()
async def fallback_handler(ctx):
await ctx.reply(
"متوجه پیام شما نشدم.\n\n"
"برای شروع از دستور /start استفاده کن."
)

---

# ارسال عکس

برای ارسال عکس، باید متد `send_photo` را به client و messenger اضافه کنید.

---

## مرحله 1: اضافه کردن به `bot/core/client.py`

داخل کلاس `BaleClient`:

python
async def send_photo(
self,
chat_id: int,
photo: str,
caption: str | None = None,
reply_markup: dict | None = None,
) -> dict:
payload = {
"chat_id": chat_id,
"photo": photo,
}

if caption is not None:
payload["caption"] = caption

if reply_markup is not None:
payload["reply_markup"] = reply_markup

data = await self.request("sendPhoto", payload)
return data.get("result", {})

در این حالت `photo` می‌تواند یکی از این‌ها باشد:

text
file_id
URL

مثال:

python
photo="https://example.com/image.jpg"

---

## مرحله 2: اضافه کردن به `bot/core/messenger.py`

داخل کلاس `Messenger`:

python
async def send_photo(
self,
chat_id: int,
photo: str,
caption: str | None = None,
reply_markup: dict | None = None,
) -> dict:
return await self.client.send_photo(
chat_id=chat_id,
photo=photo,
caption=caption,
reply_markup=reply_markup,
)

---

## مرحله 3: اضافه کردن helper به Context

داخل فایل:

text
bot/core/state/context.py

داخل کلاس `Context`:

python
async def reply_photo(
self,
photo: str,
caption: str | None = None,
reply_markup: dict | None = None,
) -> None:
await self.messenger.send_photo(
chat_id=self.chat_id,
photo=photo,
caption=caption,
reply_markup=reply_markup,
)

---

## استفاده در handler

python
from bot.core.state.context import Context


async def send_sample_photo_handler(ctx: Context) -> None:
await ctx.reply_photo(
photo="https://example.com/image.jpg",
caption="این یک عکس نمونه است."
)

router:

python
router.command("/photo")(send_sample_photo_handler)

---

# ارسال فایل یا Document

برای ارسال فایل، متد `sendDocument` را اضافه کنید.

---

## مرحله 1: اضافه کردن به `bot/core/client.py`

python
async def send_document(
self,
chat_id: int,
document: str,
caption: str | None = None,
reply_markup: dict | None = None,
) -> dict:
payload = {
"chat_id": chat_id,
"document": document,
}

if caption is not None:
payload["caption"] = caption

if reply_markup is not None:
payload["reply_markup"] = reply_markup

data = await self.request("sendDocument", payload)
return data.get("result", {})

---

## مرحله 2: اضافه کردن به `bot/core/messenger.py`

python
async def send_document(
self,
chat_id: int,
document: str,
caption: str | None = None,
reply_markup: dict | None = None,
) -> dict:
return await self.client.send_document(
chat_id=chat_id,
document=document,
caption=caption,
reply_markup=reply_markup,
)

---

## مرحله 3: اضافه کردن به Context

در کلاس `Context`:

python
async def reply_document(
self,
document: str,
caption: str | None = None,
reply_markup: dict | None = None,
) -> None:
await self.messenger.send_document(
chat_id=self.chat_id,
document=document,
caption=caption,
reply_markup=reply_markup,
)

---

## استفاده در handler

python
async def send_file_handler(ctx: Context) -> None:
await ctx.reply_document(
document="https://example.com/sample.pdf",
caption="فایل نمونه"
)

router:

python
router.command("/file")(send_file_handler)

---

# ارسال عکس یا فایل از مسیر local

در نسخه ساده، ارسال با URL یا `file_id` راحت‌تر است.

اگر بخواهید از فایل local ارسال کنید، باید درخواست multipart بزنید. برای این کار می‌توانید در `BaleClient` یک متد جدا اضافه کنید.

نمونه پایه برای آپلود فایل:

python
async def request_multipart(
self,
method: str,
data: dict,
files: dict,
) -> dict:
url = self._method_url(method)

async with httpx.AsyncClient(timeout=self.timeout) as client:
response = await client.post(url, data=data, files=files)
response.raise_for_status()
result = response.json()

if not result.get("ok", False):
description = result.get("description", "Unknown Bale API error")
raise RuntimeError(f"Bale API error in {method}: {description}")

return result

نمونه ارسال عکس local:

python
async def send_photo_file(
self,
chat_id: int,
file_path: str,
caption: str | None = None,
) -> dict:
data = {
"chat_id": str(chat_id),
}

if caption:
data["caption"] = caption

with open(file_path, "rb") as file:
files = {
"photo": file,
}

result = await self.request_multipart(
"sendPhoto",
data=data,
files=files,
)

return result.get("result", {})

---

# ساخت feature برای ارسال رسانه

مثلاً feature زیر را بسازید:

text
bot/features/public/media/
├── handlers.py
└── router.py

## `handlers.py`

python
from bot.core.state.context import Context


async def photo_handler(ctx: Context) -> None:
await ctx.reply_photo(
photo="https://example.com/image.jpg",
caption="عکس نمونه"
)


async def file_handler(ctx: Context) -> None:
await ctx.reply_document(
document="https://example.com/sample.pdf",
caption="فایل نمونه"
)

## `router.py`

python
from bot.core.router import Router
from bot.features.public.media.handlers import (
photo_handler,
file_handler,
)


router = Router()

router.command("/photo")(photo_handler)
router.command("/file")(file_handler)

router.text("ارسال عکس")(photo_handler)
router.text("ارسال فایل")(file_handler)

بعد در `bot/features/router.py`:

python
from bot.features.public.media.router import router as media_router

main_router.include_router(media_router)

---

# مثال منوی اصلی کامل

## `start/handlers.py`

python
from bot.core.state.context import Context
from bot.utils.keyboards import reply_keyboard


async def start_handler(ctx: Context) -> None:
await ctx.finish()

keyboard = reply_keyboard([
["ثبت‌نام"],
["پروفایل", "راهنما"],
["ارسال عکس", "ارسال فایل"],
])

await ctx.reply(
"سلام 👋\n"
"به ربات هم‌خوان خوش آمدی.\n\n"
"یکی از گزینه‌های زیر را انتخاب کن:",
reply_markup=keyboard,
)

---

# ترتیب resolve شدن routeها

در این فریم‌ورک، routeها به این ترتیب بررسی می‌شوند:

1. state فعلی کاربر
2. command
3. text
4. fallback

یعنی اگر کاربر داخل state ثبت‌نام باشد، اول handler مربوط به همان state اجرا می‌شود.

مثلاً اگر state کاربر این باشد:

text
register:age

هر پیامی بفرستد، اول این route بررسی می‌شود:

python
router.state(REGISTER_AGE)(register_age_handler)

---

# نکته مهم درباره command در state

اگر کاربر وسط ثبت‌نام `/start` بفرستد، چون state اولویت دارد، ممکن است به handler همان state برود.

اگر می‌خواهید commandهایی مثل `/start` همیشه اولویت داشته باشند، باید logic فایل `bot/core/router.py` را تغییر دهید.

مثلاً ترتیب را این‌طور کنید:

1. command
2. state
3. text
4. fallback

در متد `resolve`:

python
async def resolve(self, ctx: Context) -> Optional[Handler]:
if ctx.message.command:
for route in self.routes:
if route.command == ctx.message.command:
return route.handler

current_state = await ctx.get_state()

if current_state is not None:
for route in self.routes:
if route.state == current_state:
return route.handler

for route in self.routes:
if route.text is not None and route.text == ctx.text:
return route.handler

for route in self.routes:
if route.fallback:
return route.handler

return None

برای اکثر ربات‌ها این حالت بهتر است.

---

# فعال‌سازی Redis برای state

به صورت پیش‌فرض state داخل حافظه RAM ذخیره می‌شود.

یعنی اگر ربات restart شود، state کاربران پاک می‌شود.

برای ذخیره دائمی‌تر، Redis را فعال کنید.

در `.env`:

env
USE_REDIS=true
REDIS_URL=redis://localhost:6379/0

اجرای Redis با Docker:

bash
docker run -p 6379:6379 redis:7

---

# ساخت Middleware جدید

Middleware قبل از handler اجرا می‌شود.

مثلاً یک middleware برای log کردن پیام‌ها:

python
from bot.core.state.context import Context


class LoggingMiddleware:
async def __call__(self, ctx: Context, handler):
print(f"User {ctx.user_id}: {ctx.text}")
await handler(ctx)

ثبت در `run_bot.py`:

python
dispatcher.add_middleware(LoggingMiddleware())

---

# ساخت Rate Limit Middleware ساده

python
import time
from bot.core.state.context import Context


class RateLimitMiddleware:
def __init__(self, seconds: int = 1):
self.seconds = seconds
self.users = {}

async def __call__(self, ctx: Context, handler):
now = time.time()
last_time = self.users.get(ctx.user_id, 0)

if now - last_time < self.seconds:
await ctx.reply("لطفاً کمی آرام‌تر پیام ارسال کن.")
return

self.users[ctx.user_id] = now
await handler(ctx)

ثبت:

python
dispatcher.add_middleware(RateLimitMiddleware(seconds=1))

---

# خطاهای رایج

## خطای import

اگر خطای import گرفتید، مطمئن شوید از ریشه پروژه اجرا می‌کنید:

bash
python -m bot.run_bot

---

## خطای token

اگر پیام مربوط به authorization یا token گرفتید، مقدار زیر را چک کنید:

env
BALE_BOT_TOKEN=...

---

## ربات پیام می‌گیرد ولی جواب نمی‌دهد

موارد زیر را بررسی کنید:

1. آیا route مربوطه ثبت شده؟
2. آیا router مربوطه در `bot/features/router.py` include شده؟
3. آیا متن دکمه دقیقاً با `router.text` یکی است؟
4. آیا کاربر در state دیگری گیر نکرده؟
5. آیا fallback فعال است؟

---

# چک‌لیست اضافه کردن قابلیت جدید

برای اضافه کردن هر قابلیت جدید:

1. یک پوشه در `bot/features/public/` بسازید.
2. فایل `handlers.py` بسازید.
3. فایل `router.py` بسازید.
4. handlerها را در router ثبت کنید.
5. router آن feature را در `bot/features/router.py` include کنید.
6. اگر دکمه نیاز دارید، در منوی `/start` اضافه کنید.
7. اگر فرآیند چندمرحله‌ای است، state تعریف کنید.
8. اگر data موقت نیاز دارید، از `ctx.update_data` استفاده کنید.

---

# نمونه کامل route مرکزی

python
from bot.core.router import Router

from bot.features.public.start.router import router as start_router
from bot.features.public.help.router import router as help_router
from bot.features.public.register.router import router as register_router
from bot.features.public.profile.router import router as profile_router
from bot.features.public.media.router import router as media_router


main_router = Router()

main_router.include_router(start_router)
main_router.include_router(help_router)
main_router.include_router(register_router)
main_router.include_router(profile_router)
main_router.include_router(media_router)


@main_router.fallback()
async def fallback_handler(ctx):
await ctx.reply(
"متوجه پیام شما نشدم.\n\n"
"برای شروع از دستور /start استفاده کن."
)

---

# دستورات نمونه ربات

بعد از اجرای ربات، می‌توانید این‌ها را تست کنید:

text
/start
/help
/register
/profile
/photo
/file

و دکمه‌ها:

text
ثبت‌نام
راهنما
پروفایل
ارسال عکس
ارسال فایل

---

# توسعه‌های پیشنهادی بعدی

برای حرفه‌ای‌تر شدن فریم‌ورک می‌توانید این موارد را اضافه کنید:

1. پشتیبانی از `callback_query`
2. پشتیبانی از `contact`
3. پشتیبانی از `location`
4. پشتیبانی از `voice`
5. پشتیبانی از `video`
6. error handler مرکزی
7. dependency injection ساده
8. اتصال به PostgreSQL
9. سیستم auth برای کاربران
10. پنل ادمین
11. تست با `pytest`

---

# جمع‌بندی

این پروژه یک پایه سبک و قابل توسعه برای ساخت ربات بله است.

برای اضافه کردن قابلیت جدید، کافی است feature جدید بسازید، handlerها را بنویسید، router تعریف کنید و آن را در router اصلی include کنید.

برای دکمه‌ها از `reply_keyboard` و `inline_keyboard` استفاده کنید.

برای فرآیندهای چندمرحله‌ای از `State` و متدهای زیر استفاده کنید:

python
await ctx.set_state(...)
await ctx.get_state()
await ctx.update_data(...)
await ctx.get_data()
await ctx.finish()

برای ارسال پیام:

python
await ctx.reply("متن")

برای ارسال عکس:

python
await ctx.reply_photo("URL_OR_FILE_ID")

برای ارسال فایل:

python
await ctx.reply_document("URL_OR_FILE_ID")
