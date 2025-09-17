from fastapi import APIRouter, Header
from fastapi.responses import JSONResponse

from app.schema.post.apikey import ApikeyCreate as apikey_create_schema
from app.schema.response.success import success as success_response

from data.act.base import (
    create_api_key,
    information_api_key,
    delete_api_key
)

from app.deps.security import verification_access_token

from app.service.mail import send_api_key_created_email
router = APIRouter()

@router.post("/create")
async def create_apikey(data: apikey_create_schema, access_token: str = Header(...)):
    mail = verification_access_token(access_token)
    result = await create_api_key(email=mail, data=data)
    send_api_key_created_email(email=mail, title=data.title, created_at=result['created_at'], key=result['key'])
    return JSONResponse(status_code=201, content=success_response(data=result, pesan="API Key created successfully."))

@router.get("/information")
async def information_apikey(access_token: str = Header(...)):
    mail = verification_access_token(access_token)
    result = await information_api_key(email=mail)
    return JSONResponse(status_code=200, content=success_response(data=result, pesan="API Key information retrieved successfully."))

@router.delete("/delete/{title}")
async def delete_apikey(title: str, access_token: str = Header(...)):
    mail = verification_access_token(access_token)
    await delete_api_key(title=title, email=mail)
    return JSONResponse(status_code=200, content=success_response(data=None, pesan="API Key deleted successfully."))