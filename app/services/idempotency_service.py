import asyncio
from app.store.idempotency_store import IdempotencyStore
from app.utils.hash_utils import hash_payload

PROCESSING_DELAY = 2


class IdempotencyService:
    def __init__(self):
        self.store = IdempotencyStore()

    async def process_request(self, key: str, payload: dict):

        payload_hash = hash_payload(payload)

        entry = await self.store.get_or_create(key, payload_hash)

        # ❌ same key but different payload
        if entry["payload_hash"] != payload_hash:
            return (
                {"detail": "Idempotency key already used for a different request body."},
                422,
                False
            )

        # ✅ already completed
        if entry["status"] == "completed":
            return entry["response"], entry["status_code"], True

        # ⏳ in progress (race condition handling)
        if entry["status"] == "processing":
            await entry["event"].wait()
            final = self.store.data[key]
            return final["response"], final["status_code"], True

        # 🚀 first request
        await self.store.mark_processing(key)

        await asyncio.sleep(PROCESSING_DELAY)

        amount = payload["amount"]
        currency = payload["currency"]

        response = {
            "status": f"Charged {amount} {currency}"
        }

        await self.store.save_result(key, response, 201)

        return response, 201, False