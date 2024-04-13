import json

import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Request, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_oauth2.exceptions import OAuth2Error
from starlette.responses import RedirectResponse
from fastapi_oauth2.middleware import OAuth2Middleware
from fastapi_oauth2.router import router as oauth2_router
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from src.handlers.oauth_handler import on_auth
from src.conf.oauth_config import oauth2_config
from src.conf import config
from src.database.db import get_db
from src.routes import contacts
from src.routes import auth, payment
from src.schemas.web_shop import ShopData
from src.services.auth import auth_service
from jose import jwt
from src.repository.users import get_user_by_email
from src.services.mono_service import create_invoice, set_webhook
from src.services.tg_service import get_current_chat_id, bot, types, dp, InlineKeyboardButton, WEB_APP_URL, \
    InlineKeyboardMarkup, save_users_invoice

WEBHOOK_PATH = f"/bot/{config.TG_TOKEN}"
WEBHOOK_URL = f"{config.WEBHOOK_URL}{WEBHOOK_PATH}"
print(f"WEBHOOK_URL: {WEBHOOK_URL}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await bot.set_webhook(url=WEBHOOK_URL)
    await set_webhook()

    yield
    await bot.delete_webhook()


app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="src/static"), name="static")
templates = Jinja2Templates(directory="src/templates")

app.include_router(auth.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")
app.include_router(oauth2_router)
app.include_router(payment.router)

app.add_middleware(OAuth2Middleware, config=oauth2_config, callback=on_auth)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)


@app.exception_handler(OAuth2Error)
async def error_handler(request: Request, e: OAuth2Error):
    print("An error occurred in OAuth2Middleware", e)
    return RedirectResponse(url="/", status_code=303)


@app.get("/", response_class=HTMLResponse)
async def root(request: Request, token: str = Query(None)):
    username = ''
    avatar = ""
    # print(f"{request.user=}")
    # print(token)
    if token:
        payload = jwt.decode(token, auth_service.SECRET_KEY, algorithms=[auth_service.ALGORITHM])
        if payload["scope"] == "access_token":
            email = payload["sub"]
            # print(f"{email}")
            user = await get_user_by_email(email, db=await get_db())
            # print(f"{user}")
            username = user.username
            avatar = user.avatar
        request["user"]["is_authenticated"] = False
    return templates.TemplateResponse(name="index.html", context={
        "json": json,
        "request": request,
        "username": username,
        "avatar": avatar
    })


@app.get("/hello")
def index():
    return {"message": "🔱 Contacts Application 🔱"}


@app.get("/api/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    try:
        # Make request
        result = await db.execute(text("SELECT 1"))
        result = result.fetchone()
        if result is None:
            raise HTTPException(
                status_code=500, detail="Database is not configured correctly"
            )
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")


@app.post("/web-data")
async def handle_web_data(request: ShopData):
    print("Start func handle_web_data")
    data = request
    print('Data:', data)

    products = data.products
    total_price = data.totalPrice

    chat_id = get_current_chat_id()  # извлекаем chat_id из глобальной переменной
    print(f"Chat ID: {chat_id}")
    product_details = ', '.join(
        f"{product['title']} ({product['description']}) for {product['price']}$" for product in products)
    message_text = f'''
    Congratulations 🎉🎉🎉
    Your order has been created successfully.
    Total Price: {total_price}$,
    Products: {product_details}
    '''
    payment_info = create_invoice(total_price=total_price, products=products)
    invoiceId = payment_info.get("invoiceId")
    save_users_invoice(invoiceId=invoiceId, user_id=int(chat_id))
    inline_button = InlineKeyboardButton(text='Pay Here', url=payment_info.get("pageUrl"))
                                         # web_app=types.WebAppInfo(url=payment_info.get("pageUrl"))) # not open in telegram browser
    inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[[inline_button]])
    await bot.send_message(chat_id, message_text, reply_markup=inline_keyboard)


@app.post(WEBHOOK_PATH)
async def bot_webhook(update: dict):
    telegram_update = types.Update(**update)
    await dp.feed_update(bot=bot, update=telegram_update)


if __name__ == "__main__":
    uvicorn.run('main:app', host="0.0.0.0", port=8000, reload=True)
