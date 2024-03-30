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

from src.handlers.oauth_handler import on_auth
from src.conf.oauth_config import oauth2_config
from src.database.db import get_db
from src.routes import contacts
from src.routes import auth
from src.services.auth import auth_service
from jose import jwt
from src.repository.users import get_user_by_email

app = FastAPI()

app.mount("/static", StaticFiles(directory="src/static"), name="static")
templates = Jinja2Templates(directory="src/templates")

app.include_router(auth.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")
app.include_router(oauth2_router)

app.add_middleware(OAuth2Middleware, config=oauth2_config, callback=on_auth)


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



if __name__ == "__main__":
    uvicorn.run('main:app', host="0.0.0.0", port=8000, reload=True)
