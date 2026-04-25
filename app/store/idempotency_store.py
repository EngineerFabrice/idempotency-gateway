import asyncio


class IdempotencyStore:

    def __init__(self):
        self.data = {}
        self.lock = asyncio.Lock()

    async def get_or_create(self, key, payload_hash):
        async with self.lock:
            if key not in self.data:
                self.data[key] = {
                    "payload_hash": payload_hash,
                    "status": "new",
                    "response": None,
                    "status_code": None,
                    "event": asyncio.Event()
                }

            return self.data[key]

    async def mark_processing(self, key):
        async with self.lock:
            self.data[key]["status"] = "processing"

    async def save_result(self, key, response, status_code):
        async with self.lock:
            entry = self.data[key]
            entry["response"] = response
            entry["status_code"] = status_code
            entry["status"] = "completed"
            entry["event"].set()