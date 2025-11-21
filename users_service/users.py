from fastapi import FastAPI, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from database import engine, SessionLocal
from .models import Base, UserDB
from .schemas import UserCreate, UserRead, UserUpdate

app = FastAPI()
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/api/users", response_model=list[UserRead])
def list_users(db: Session = Depends(get_db)):
    stmt = select(UserDB).order_by(UserDB.id)
    result = db.execute(stmt)
    users = result.scalars().all()
    return users


@app.get("/api/users/{user_id}", response_model=UserRead)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(UserDB, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/api/users", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def add_user(payload: UserCreate, db: Session = Depends(get_db)):
    user = UserDB(**payload.model_dump())
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="User already exists")
    return user

@app.put("/api/users/{user_id}", response_model=UserRead)
def replace_user(user_id: int, payload: UserCreate, db: Session = Depends(get_db)):
    user = db.get(UserDB, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.name = payload.name
    user.email = payload.email
    user.age = payload.age
    user.student_id = payload.student_id

    try:
        db.commit()
        sb.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="User update Failed")
    return user

@app.delete("/api/users/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db)) -> Response:
    user = db.get(UserDB, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete_user
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.patch("/api/users/{user_id}", response_model=UserRead)
def patch_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    user = db.get(UserDB, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Only update fields that are provided
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(user, field, value)

    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="User patch failed")
    return user