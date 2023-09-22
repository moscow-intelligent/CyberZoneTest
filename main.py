from datetime import date
from typing import Optional

from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from utils import *
from models import Base, User, Booking

DATABASE_URL = 'postgresql://postgres:123@localhost/cyberapi'
reuseable_oauth = OAuth2PasswordBearer(
    tokenUrl="/login",
    scheme_name="JWT"
)

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)


def recreate_database():
    # Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


recreate_database()

app = FastAPI()


@app.get("/")
def root():
    return {"message": "API online"}


@app.post("/register", summary="Register a new user")
def create_user(name: str, password: str):
    """
    Create a new user and register them in the system.

    Parameters:
        name (str): The name of the user.
        password (str): The password of the user.

    Returns:
        JSONResponse: A JSON response with a status code and a message indicating that the user has been successfully registered.
    """
    session = Session()
    existing_user = session.query(User).filter_by(username=name).first()
    if existing_user:
        session.close()
        return JSONResponse(
            status_code=400, content={"status_code": 400, "message": "user already exists"}
        )
    user = User(username=name, password=get_hashed_password(password), created_at=date.today(), updated_at=date.today())
    session.add(user)
    session.commit()
    session.close()

    return JSONResponse(
        status_code=200, content={"status_code": 200, "message": "user registered",
                                  "user_id": session.query(User).filter_by(username=name).first().id}
    )


@app.post("/refresh_token", summary="Refresh JWT access token")
def refresh_token(token: str):
    token = decodeJWT(token)
    if not token:
        return JSONResponse(
            status_code=400, content={"status_code": 400, "message": "Invalid token"}
        )
    if token['exp'] < time.time():
        return JSONResponse(
            status_code=400, content={"status_code": 400, "message": "Token expired"}
        )
    session = Session()
    user = session.query(User).filter_by(username=token['sub']['refresh_for']).first()
    session.close()
    if not user:
        return JSONResponse(
            status_code=400, content={"status_code": 400, "message": "User not found"}
        )
    return JSONResponse(
        status_code=200, content={"status_code": 200, "message": "Token refreshed",
                                  "access_token": create_access_token(user.username),
                                  "refresh_token": create_refresh_token(user.username)}
    )


@app.post('/login', summary="Get JWT access token for the specified user")
def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    session = Session()
    user = session.query(User).filter_by(username=form_data.username).first()
    if not user:
        return JSONResponse(
            status_code=400, content={"status_code": 400, "message": "Incorrect login details"}
        )
    hashed_passwd = user.password
    if not verify_password(form_data.password, hashed_passwd):
        return JSONResponse(
            status_code=400, content={"status_code": 400, "message": "Incorrect login details"}
        )
    return JSONResponse(
        status_code=200, content={"status_code": 200, "message": "Logged in",
                                  "access_token": create_access_token(user.username),
                                  "refresh_token": create_refresh_token(user.username)}
    )


@app.get("/get_current_user", dependencies=[Depends(JWTBearer())], summary="Get current user data")
async def get_current_user(request: Request):
    username = decodeJWT(request.headers.get("Authorization").split(' ')[1])['sub']
    session = Session()
    user = session.query(User).filter_by(username=username).first()
    session.close()
    return JSONResponse(
        status_code=200, content={"status_code": 200, "message": "user data",
                                  "user": {"id": user.id,
                                           "username": user.username,
                                           "created_at": str(user.created_at),
                                           "modified_at": str(user.updated_at)}}
    )


@app.delete("/delete_user", dependencies=[Depends(JWTBearer())], summary="Delete user")
def delete_user(request: Request):
    session = Session()
    user = session.query(User).filter_by(
        username=decodeJWT(request.headers.get("Authorization").split(' ')[1])['sub']).first()
    if not user:
        return JSONResponse(
            status_code=400, content={"status_code": 400, "message": "user not found"}
        )
    session.delete(user)
    session.commit()
    session.close()
    return JSONResponse(
        status_code=200, content={"status_code": 200, "message": "user deleted"}
    )


from datetime import datetime


@app.post("/create_booking", dependencies=[Depends(JWTBearer())], summary="Create booking")
def create_booking(request: Request, start_time: str, end_time: str, comment: Optional[str] = None):
    session = Session()
    user = session.query(User).filter_by(
        username=decodeJWT(request.headers.get("Authorization").split(' ')[1])['sub']).first()
    if not user:
        return JSONResponse(
            status_code=400, content={"status_code": 400, "message": "user not found"}
        )

    try:
        start_datetime = datetime.strptime(start_time, "%d-%m-%Y %H:%M:%S")
        end_datetime = datetime.strptime(end_time, "%d-%m-%Y %H:%M:%S")
    except ValueError:
        return JSONResponse(
            status_code=400, content={"status_code": 400, "message": "invalid time format"}
        )
    booking = Booking(user_id=user.id, start_time=start_datetime, end_time=end_datetime, comment=comment)
    session.add(booking)
    session.commit()
    session.close()
    return JSONResponse(
        status_code=200,
        content={"status_code": 200, "message": "booking created", "booking_id": booking.id, "user_id": booking.user_id}
    )


@app.exception_handler(Exception)
def exception_handler(request, exc):
    json_resp = get_default_error_response()
    return json_resp


def get_default_error_response(status_code=500, message="Internal Server Error"):
    return JSONResponse(
        status_code=status_code,
        content={"status_code": status_code, "message": message},
    )
