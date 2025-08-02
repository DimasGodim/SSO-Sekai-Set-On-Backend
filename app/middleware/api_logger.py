from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response
from app.db.database import SessionLocal
from app.db.models import APIKey, APIUsageLog
from datetime import datetime
import time
import logging

logger = logging.getLogger(__name__)

class APILogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        db = SessionLocal()
        start_time = time.perf_counter()  # ⏱️ Mulai timing

        try:
            api_key_value = request.headers.get("api-key")
            api_key_obj = None
            if api_key_value:
                api_key_obj = db.query(APIKey).filter(APIKey.key == api_key_value).first()

            response: Response = await call_next(request)

            process_time = time.perf_counter() - start_time  # ⏱️ Hitung waktu respons

            # Log hanya jika API key valid
            if api_key_obj:
                usage_log = APIUsageLog(
                    api_key_id=api_key_obj.id,
                    endpoint=request.url.path,
                    method=request.method,
                    status_code=response.status_code,
                    timestamp=datetime.utcnow(),
                    response_time=round(process_time * 1000, 2)
                )
                db.add(usage_log)
                db.commit()

            return response

        except Exception as e:
            logger.exception("Error in API usage logging middleware")
            return Response("Internal server error", status_code=500)
        finally:
            db.close()
''