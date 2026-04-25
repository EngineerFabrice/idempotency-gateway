from fastapi import FastAPI
from app.api.payment import router as payment_router

app = FastAPI(
    title="Idempotency Gateway",
    version="1.0.0"
)

app.include_router(payment_router)


@app.get("/")
def health():
    return {"status": "Idempotency Gateway running 🚀"}