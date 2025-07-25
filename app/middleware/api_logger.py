from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response
from app.db.database import SessionLocal
from app.db.models import APIKey, APIUsageLog
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)

class APILogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        db = SessionLocal()
        try:
            api_key_value = request.headers.get("api_key")
            api_key_obj = None
            if api_key_value:
                api_key_obj = db.query(APIKey).filter(APIKey.key == api_key_value).first()

            response: Response = await call_next(request)

            # Log hanya jika API key valid
            if api_key_obj:
                usage_log = APIUsageLog(
                    api_key_id=api_key_obj.id,
                    endpoint=request.url.path,
                    method=request.method,
                    status_code=response.status_code,
                    timestamp=datetime.utcnow()
                )
                db.add(usage_log)
                db.commit()

            return response
        except Exception as e:
            logger.exception("Error in API usage logging middleware")
            return Response("Internal server error", status_code=500)
        finally:
            db.close()
