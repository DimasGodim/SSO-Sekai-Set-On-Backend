import asyncio
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response
from datetime import datetime, timezone
import time
import logging

from data.act.base import save_log_api_key
from app.schema.post.apikey import ApiKeySaveLog

logger = logging.getLogger(__name__)

class APILogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        response: Response = await call_next(request)

        try:
            api_key_header = request.headers.get("api-key")
            print(">> api-key header =", api_key_header)  # debug print

            if api_key_header and api_key_header.startswith("ApiKey "):
                api_key_value = api_key_header[len("ApiKey "):]

                process_time = time.perf_counter() - start_time

                usage_log = ApiKeySaveLog(
                    key=api_key_value,
                    endpoint=request.url.path,
                    method=request.method,
                    status_code=response.status_code,
                    timestamp=datetime.now(timezone.utc),
                    response_time=round(process_time * 1000, 2)
                )

                print(">> usage_log =", usage_log.model_dump())  # debug print
                await save_log_api_key(data=usage_log)
                print("api log saved")

        except Exception as e:
            logger.exception("Error in API usage logging middleware")
            print(f"Error in API usage logging middleware: {e}")

        return response
