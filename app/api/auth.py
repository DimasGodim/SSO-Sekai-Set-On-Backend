from fastapi import APIRouter, HTTPException, Depends, Response, Request
from fastapi.responses import JSONResponse

from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.db.models import user, RefreshToken
from app.db.database import get_db

from app.core.security import hash_password, verify_password, create_access_token

from app.schema import UserCreate, VerificationMail, UserLogin

from app.service.mail import send_verivication_code

import secrets

router = APIRouter()


@router.post("/signup")
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(user).filter(user.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    existing_nickname = db.query(user).filter(user.nickname == user_data.nickname).first()
    if existing_nickname:
        raise HTTPException(status_code=400, detail="Nickname already in use")

    verification_code: str = secrets.token_hex(3)
    new_user = user(
        email=user_data.email,
        name=user_data.name,
        nickname=user_data.nickname,
        hashed_password=hash_password(user_data.password),
        verification_code=verification_code,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    send_verivication_code(target_email=user_data.email, verification_code=verification_code)

    return JSONResponse(
        status_code=201,
        content={
            "status": "success",
            "message": "Please check your mail for verification code",
            "data": {
                "user_id": new_user.id,
                "email": new_user.email,
                "name": new_user.name,
                "nickname": new_user.nickname
            }
        }
    )


@router.post('/verification')
def verification_mail(data: VerificationMail, db: Session = Depends(get_db)):
    user_obj = db.query(user).filter(user.email == data.email).first()
    if not user_obj:
        raise HTTPException(status_code=400, detail="Email not registered")

    if user_obj.verification_code != data.verification_code:
        raise HTTPException(status_code=400, detail="Invalid verification code")

    user_obj.activate = True
    user_obj.verification_code = None
    db.commit()

    return JSONResponse(
        status_code=200,
        content={
            "status": "success",
            "message": "Email verified successfully",
            "data": {
                "user_id": user_obj.id,
                "email": user_obj.email,
                "name": user_obj.name,
                "nickname": user_obj.nickname
            }
        }
    )


@router.post('/signin')
def signin(user_data: UserLogin, response: Response, db: Session = Depends(get_db)):
    user_obj = db.query(user).filter(
        or_(
            user.email == user_data.identification,
            user.nickname == user_data.identification,
        )
    ).first()

    if not user_obj:
        raise HTTPException(status_code=400, detail="User not found")

    if not user_obj.activate:
        raise HTTPException(status_code=403, detail="Account not activated. Please verify your email.")

    if not verify_password(user_data.password, user_obj.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid password")

    access_token = create_access_token({"sub": str(user_obj.id)})
    refresh_token = secrets.token_hex(32)

    # Simpan refresh token di DB
    db.add(RefreshToken(token=refresh_token, user_id=user_obj.id))
    db.commit()

    # Simpan refresh token di cookie (HttpOnly)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=60 * 60 * 24 * 7  # 7 hari
    )

    return JSONResponse(
        status_code=200,
        content={
            "access_token": access_token,
            "token_type": "bearer"
        }
    )



@router.post("/refresh")
def refresh_token(request: Request, db: Session = Depends(get_db)):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token found")

    token_obj = db.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()
    if not token_obj:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    new_access_token = create_access_token({"sub": str(token_obj.user_id)})

    return JSONResponse(
        status_code=200,
        content={
            "status": "success",
            "access_token": new_access_token
        }
    )


@router.post("/logout")
def logout(response: Response, request: Request, db: Session = Depends(get_db)):
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        db.query(RefreshToken).filter(RefreshToken.token == refresh_token).delete()
        db.commit()

    response.delete_cookie("refresh_token")

    return JSONResponse(
        status_code=200,
        content={
            "status": "success",
            "message": "Logged out successfully"
        }
    )
