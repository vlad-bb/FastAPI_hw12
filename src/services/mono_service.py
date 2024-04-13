import json

import requests

from src.conf import config

CREATE_INVOICE_PATH = 'https://api.monobank.ua/api/merchant/invoice/create'
HEADERS = {"X-Token": config.MONO_TOKEN}
RATE_USD = 39.5
WEBHOOK_URL = f"{config.WEBHOOK_URL}/payment/apply_shop"
"""

"""


def create_invoice(total_price: float, products: list[dict]):
    """Функція для стровення інвойсу"""
    print(f"Start create_invoice")
    order_basket = []
    for product in products:
        item = {
            "name": product.get("title"),
            "qty": 1,
            "sum": int(product.get("price") * RATE_USD * 100),
            "icon": "string",
            "unit": "шт.",
            "code": "d21da1c47f3c45fca10a10c32518bdeb",
            "barcode": "string",
            "header": "string",
            "footer": "string",
            "tax": [],
            "uktzed": "string",
            "discounts": [
                {
                    "type": "DISCOUNT",
                    "mode": "PERCENT",
                    "value": "10"
                }]}
        order_basket.append(item)

    body = {
        "amount": 100,  # int(total_price * RATE_USD * 100), # todo this is real price from web shop
        "ccy": 980,
        "merchantPaymInfo": {
            "reference": "123",
            "destination": "Order from Telegram Bot",
            "comment": "Покупка Apple",
            "customerEmails": [],
            "basketOrder": order_basket},
        "redirectUrl": "https://t.me/table_trans_4_bot",
        "webHookUrl": WEBHOOK_URL,
        "validity": 3600,
        "paymentType": "debit"
    }
    response = requests.post(url=CREATE_INVOICE_PATH, headers=HEADERS, data=json.dumps(body))
    print(f"{response.status_code=}")
    print(response.json())
    return response.json()


async def set_webhook():
    url = "https://api.monobank.ua/personal/webhook"
    headers = {
        "X-Token": config.MONO_TOKEN
    }
    data = {"webHookUrl": WEBHOOK_URL}
    json_data = json.dumps(data)  # Перетворюємо словник на рядок JSON
    response = requests.post(url=url, headers=headers, data=json_data)
    print(f"{response.status_code=}")

    return {"ok": True}
