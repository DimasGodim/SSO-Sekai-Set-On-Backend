from fastapi  import APIRouter, Response, Request
from fastapi.responses import JSONResponse

import secrets

from app.schema.post.auth import (
    signup as signup_schema,
    signin as signin_schema,
    verification as verification_schema,
)

from app.service.mail import send_verivication_code

from app.schema.response.success import success as success_response

from data.act.base import (
    signup as signup_act_db,
    cek_user as cek_user_act_db,
    verification as verification_act_db,
    save_refersh_token as save_refresh_token_act_db,
    delete_refersh_token as delete_refresh_token_act_db,

)

from app.deps.security import verify_password, create_access_token

router = APIRouter()

@router.post("/signup")
async def signup(data: signup_schema):
    verification_code: str = secrets.token_hex(3)
    result = await signup_act_db(data=data, verification_code=verification_code)
    send_verivication_code(target_email=data.email, verification_code=verification_code)
    return JSONResponse(status_code=200, content=success_response(data=result, pesan="User registered successfully, please check your email for the verification code."))

@router.patch("/verification")
async def verification(data: verification_schema):
    result = await verification_act_db(data=data)
    return JSONResponse(status_code=200, content=success_response(data=result, pesan="User verified successfully."))

@router.post("/signin")
async def signin(data: signin_schema, response: Response):
    result = await cek_user_act_db(identification=data.identification)
    verify_password(plain_password=data.password, hashed_password=result["hashed_password"])
    refresh_token = secrets.token_hex(32)
    await save_refresh_token_act_db(token=refresh_token, email=result["email"])
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=60 * 60 * 24 * 7, 
        path="/"
    )
    result.pop("hashed_password", None)
    access_token = create_access_token(email=result["email"])
    response_data = {
    **result,
    "access_token": f"Bearer {access_token}"
    }
    return JSONResponse(status_code=200, content=success_response(data=response_data, pesan="User signed in successfully."))

@router.delete("/signout")
async def signout(response: Response, email, request: Request):
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        await delete_refresh_token_act_db(token=refresh_token, email=email)

    response.delete_cookie("refresh_token")

    return JSONResponse(
        status_code=200,
        content={
            "status": "success",
            "message": "Logged out successfully"
        }
    )
