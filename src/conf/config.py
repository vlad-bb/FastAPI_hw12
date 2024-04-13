from dotenv import dotenv_values

regdata = dotenv_values(".env")

ENGINE = regdata["ENGINE"]
USER = regdata["USER"]
PASSWORD = regdata["PASSWORD"]
DB_NAME = regdata["DB_NAME"]
HOST = regdata["HOST"]
PORT = regdata["PORT"]
TG_TOKEN = regdata["TG_TOKEN"]
WEBHOOK_URL = regdata["WEBHOOK_URL"]
WEBAPP_URL = regdata["WEBAPP_URL"]
MONO_TOKEN = regdata["MONO_TOKEN"]


class Config:
    DB_URL = f"{ENGINE}://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}"


config = Config()
