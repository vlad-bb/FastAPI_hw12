from fastapi import APIRouter, Depends, HTTPException, status, Path, Query

from src.schemas.web_shop import PaymentRequest, PaymentResponse
from typing import Dict, Any

from src.services.tg_service import get_user_id_by_invoice_id, bot, WEB_APP_URL, types, InlineKeyboardMarkup

router = APIRouter(prefix="/payment", tags=["payment"])


@router.post("/apply_shop", response_model=PaymentResponse, status_code=status.HTTP_200_OK)
async def get_data_from_mono(body: Dict[Any, Any]):
    print(f"Start POST get_data_from_mono")
    print(f"{body=}")
    print(body.get("status"))
    if body.get("status") == "success":
        invoiceId = body.get("invoiceId")
        user_id = get_user_id_by_invoice_id(invoiceId)
        info = f"Thank you for your order\nPlease fill for form for delivery"
        inline_button = types.InlineKeyboardButton(
            text='Add delivery info', web_app=types.WebAppInfo(url=f'{WEB_APP_URL}/form?userId={user_id}'))
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[inline_button]])
        await bot.send_message(chat_id=user_id, text=info, reply_markup=keyboard)
    return {"ok": True}


@router.get("/apply_shop", response_model=PaymentResponse, status_code=status.HTTP_200_OK)
async def get_data_from_mono():
    print(f"Start GET get_data_from_mono")
    # print(f"{body=}")
    return {"ok": True}
