from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.deps import get_current_user
from app.db.models import user as UserModel
from app.schema import UpdateProfile

router = APIRouter()


@router.get("/me")
def get_current_user_info(current_user: UserModel = Depends(get_current_user)):
    return JSONResponse(
        status_code=200,
        content={
            "status": "success",
            "data": {
                "user_id": current_user.id,
                "email": current_user.email,
                "name": current_user.name,
                "nickname": current_user.nickname
            }
        }
    )


@router.patch("/update-profile")
def update_profile(
    profile: UpdateProfile,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    update_data = profile.dict(exclude_unset=True)

    # Validasi nickname jika ingin diubah
    if "nickname" in update_data:
        new_nickname = update_data["nickname"]
        if new_nickname != current_user.nickname:
            existing = db.query(UserModel).filter(
                UserModel.nickname == new_nickname,
                UserModel.id != current_user.id
            ).first()
            if existing:
                raise HTTPException(status_code=400, detail="Nickname already in use")
            current_user.nickname = new_nickname

    # Update name jika ada
    if "name" in update_data:
        current_user.name = update_data["name"]

    db.commit()
    db.refresh(current_user)

    return JSONResponse(
        status_code=200,
        content={
            "status": "success",
            "message": "Profile updated",
            "data": {
                "user_id": current_user.id,
                "name": current_user.name,
                "nickname": current_user.nickname,
                "email": current_user.email
            }
        }
    )

@router.delete("/delete")
def delete_account(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    db.delete(current_user)
    db.commit()
    return JSONResponse(
        status_code=200,
        content={
            "status": "success",
            "message": "Account deleted"
        }
    )
