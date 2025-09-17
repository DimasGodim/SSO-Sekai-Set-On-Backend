from fastapi import APIRouter, Header
from fastapi.responses import JSONResponse

from data.act.base import (
    get_user,
    edit_user,
    delete_user,
    information_api_key
)

from app.schema.post.user import UpdateProfile
from app.schema.response.success import success as success_response
from app.deps.security import verification_access_token

router = APIRouter()

@router.get("/detail")
async def get_profile(access_token: str = Header(...)):
    mail = verification_access_token(access_token)
    user = await get_user(mail)
    api_key = await information_api_key(mail)
    response = {**user, **api_key}

    return JSONResponse(content=success_response(data=response), status_code=200)

@router.put("/edit")
async def edit_profile(data: UpdateProfile, access_token: str = Header(...)):
    mail = verification_access_token(access_token)
    result = await edit_user(mail, data)
    return JSONResponse(content=success_response(data=result, pesan="Profile Edit Success"), status_code=200)

@router.delete("/delete")
async def delete_profile(access_token: str = Header(...)):
    mail = verification_access_token(access_token)
    await delete_user(mail)
    return JSONResponse(content=success_response(data={"email": mail}, pesan="User Deleted Successfully"), status_code=200)