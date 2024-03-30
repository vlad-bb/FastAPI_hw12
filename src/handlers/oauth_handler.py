from fastapi_oauth2.middleware import Auth
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.entity.models import User
from src.repository.users import get_user_by_email, create_user
from src.services.auth import auth_service


async def on_auth(auth: Auth, user: User):
    # perform a check for user existence in
    # the database and create if not exists
    print(f"{auth=} {user=} {type(user)=}")
    db_user = await get_user_by_email(user.email, db=await get_db())
    if not db_user:
        password = auth_service.get_password_hash(user.identity)
        body = {"username": user.name, "email": user.email, "password": password}
        avatar = user.avatar_url if user.avatar_url else user.picture
        new_user = await create_user(body=body, db=await get_db(), avatar=avatar)
