from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.services.idempotency_service import IdempotencyService

router = APIRouter()
service = IdempotencyService()


# ✅ REQUEST BODY MODEL (THIS FIXES SWAGGER UI)
class PaymentRequest(BaseModel):
    amount: int
    currency: str


@router.post("/process-payment")
async def process_payment(
    request: PaymentRequest,
    idempotency_key: str = Header(None)
):
    if not idempotency_key:
        raise HTTPException(status_code=400, detail="Missing Idempotency-Key")

    body = request.model_dump()

    response, status_code, cache_hit = await service.process_request(
        key=idempotency_key,
        payload=body
    )

    return JSONResponse(
        content=response,
        status_code=status_code,
        headers={"X-Cache-Hit": str(cache_hit).lower()}
    )