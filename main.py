from datetime import date
from typing import Optional
from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from utils import *
from models import Base, User, Booking

DATABASE_URL = 'postgresql://cyberuser:cyberpassword@db/cyberapi'
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
async def create_user(name: str, password: str):
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
async def refresh_token(token: str):
    """
    Refresh JWT access token.

    This function takes a JWT token as input and refreshes it. It first decodes the token using the `decodeJWT` function. If the token is invalid, it returns a `JSONResponse` with a status code of 400 and a message indicating that the token is invalid.

    Next, it checks if the token has expired by comparing the expiration time (`exp`) with the current time. If the token has expired, it returns a `JSONResponse` with a status code of 400 and a message indicating that the token has expired.

    If the token is valid and has not expired, it retrieves the user associated with the token from the database using the `username` stored in the token. If no user is found, it returns a `JSONResponse` with a status code of 400 and a message indicating that the user was not found.

    Finally, if the token is valid, has not expired, and the user is found, it returns a `JSONResponse` with a status code of 200 and a message indicating that the token has been refreshed. It also includes the new access token and refresh token in the response.

    Parameters:
    - `token` (str): The JWT token to be refreshed.

    Returns:
    - `JSONResponse`: The response containing the status code, message, access token, and refresh token.
    """
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
async def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Get JWT access token for the specified user.

    Args:
        form_data (OAuth2PasswordRequestForm, optional): The form data containing the username and password for login. Defaults to Depends().

    Returns:
        JSONResponse: The response containing the access token and refresh token if the login is successful, or an error message if the login details are incorrect.
    """
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
    """
    Get current user data.

    Args:
        request (Request): The request object.

    Returns:
        JSONResponse: The JSON response containing the current user data.

    Dependencies:
        JWTBearer: The dependency function that validates the JWT token in the request header.

    Summary:
        Get current user data.
    """
    username = decodeJWT(request.headers.get("Authorization").split(' ')[1])['sub']
    session = Session()
    user = session.query(User).filter_by(username=username).first()
    if not user:
        return JSONResponse(
            status_code=400, content={"status_code": 400, "message": "user not found"}
        )
    session.close()
    return JSONResponse(
        status_code=200, content={"status_code": 200, "message": "user data",
                                  "user": {"id": user.id,
                                           "username": user.username,
                                           "created_at": str(user.created_at),
                                           "modified_at": str(user.updated_at)}}
    )


@app.delete("/delete_user", dependencies=[Depends(JWTBearer())], summary="Delete user")
async def delete_user(request: Request):
    """
    Delete user.

    Parameters:
        - request (Request): The HTTP request object.

    Returns:
        - JSONResponse: The HTTP response object.
    """
    session = Session()
    user = session.query(User).filter_by(
        username=decodeJWT(request.headers.get("Authorization").split(' ')[1])['sub']).first()
    if not user:
        return JSONResponse(
            status_code=400, content={"status_code": 400, "message": "user not found"}
        )
    session.delete(user)
    session.query(Booking).filter_by(user_id=user.id).delete()
    session.commit()
    session.close()
    return JSONResponse(
        status_code=200, content={"status_code": 200, "message": "user deleted"}
    )


@app.post("/create_booking", dependencies=[Depends(JWTBearer())], summary="Create booking")
async def create_booking(request: Request, start_time: str, end_time: str,
                         comment: Optional[str] = None) -> JSONResponse:
    """
    Create a booking with the given start time, end time, and optional comment.

    Parameters:
        - request (Request): The incoming request object.
        - start_time (str): The start time of the booking in the format "%d-%m-%Y %H:%M:%S".
        - end_time (str): The end time of the booking in the format "%d-%m-%Y %H:%M:%S".
        - comment (Optional[str]): An optional comment for the booking.

    Returns:
        - JSONResponse: The response containing the status code, message, booking ID, and user ID.
          If the user is not found, the status code will be 400 and the message will be "user not found".
          If the time format is invalid, the status code will be 400 and the message will be "invalid time format".
          If the booking is created successfully, the status code will be 200 and the message will be "booking created",
          along with the booking ID and user ID.
    """
    session = Session()
    user = session.query(User).filter_by(
        username=decodeJWT(request.headers.get("Authorization").split(' ')[1])['sub']
    ).first()

    if not user:
        return JSONResponse(
            status_code=400,
            content={"status_code": 400, "message": "user not found"}
        )

    try:
        start_datetime = datetime.strptime(start_time, "%d-%m-%Y %H:%M:%S")
        end_datetime = datetime.strptime(end_time, "%d-%m-%Y %H:%M:%S")
    except ValueError:
        return JSONResponse(
            status_code=400,
            content={"status_code": 400, "message": "invalid time format"}
        )

    if start_datetime > end_datetime:
        return JSONResponse(
            status_code=400,
            content={"status_code": 400, "message": "invalid time range"}
        )

    booking = session.query(Booking).filter_by(
        user_id=user.id,
        start_time=start_datetime,
        end_time=end_datetime,
    ).first()

    if booking:
        return JSONResponse(
            status_code=400,
            content={"status_code": 400, "message": "booking already exists"}
        )

    new_booking = Booking(
        user_id=user.id,
        start_time=start_datetime,
        end_time=end_datetime,
        comment=comment
    )
    session.add(new_booking)
    session.commit()
    session.refresh(new_booking)
    booking_id = new_booking.id
    session.close()

    return JSONResponse(
        status_code=200,
        content={
            "status_code": 200,
            "message": "booking created",
            "booking_id": new_booking.id
        }
    )


@app.patch("/update_user", dependencies=[Depends(JWTBearer())], summary="Update user")
async def update_user_information(request: Request, name: Optional[str] = None, password: Optional[str] = None):
    """
    Update user information.

    Parameters:
        - request (Request): The HTTP request object.
        - name (Optional[str]): The new name of the user.
        - password (Optional[str]): The new password of the user.

    Returns:
        - JSONResponse: The HTTP response object.
    """
    session = Session()
    user = session.query(User).filter_by(
        username=decodeJWT(request.headers.get("Authorization").split(' ')[1])['sub']).first()
    if not user:
        return JSONResponse(
            status_code=404, content={"status_code": 404, "message": "user not found"}
        )
    if name:
        user.username = name
    if password:
        user.password = get_hashed_password(password)
    user.updated_at = date.today()
    name = user.username
    session.commit()
    session.close()
    return JSONResponse(
        status_code=200, content={"status_code": 200, "message": "user updated",
                                  "access_token": create_access_token(name),
                                  "refresh_token": create_refresh_token(name)}
    )


@app.delete("/remove_booking/{booking_id}", dependencies=[Depends(JWTBearer())], summary="Delete booking")
async def remove_booking(request: Request, booking_id: int):
    session = Session()
    user = session.query(User).filter_by(
        username=decodeJWT(request.headers.get("Authorization").split(' ')[1])['sub']).first()
    if not user:
        return JSONResponse(
            status_code=404, content={"status_code": 404, "message": "user not found"}
        )
    booking = session.query(Booking).filter_by(
        user_id=user.id,
        id=booking_id,
    ).first()
    if not booking:
        return JSONResponse(
            status_code=404, content={"status_code": 404, "message": "booking not found"}
        )
    session.delete(booking)
    session.commit()
    session.close()
    return JSONResponse(
        status_code=200, content={"status_code": 200, "message": "booking deleted"}
    )


@app.get("/get_bookings", dependencies=[Depends(JWTBearer())], summary="Get all bookings for the authenticated user")
async def get_bookings(request: Request):
    session = Session()
    user = session.query(User).filter_by(
        username=decodeJWT(request.headers.get("Authorization").split(' ')[1])['sub']).first()
    if not user:
        return JSONResponse(
            status_code=400, content={"status_code": 400, "message": "user not found"}
        )
    bookings = session.query(Booking).filter_by(user_id=user.id).all()
    session.close()
    return JSONResponse(
        status_code=200, content={"status_code": 200, "message": "bookings retrieved",
                                  "bookings": [booking.to_json() for booking in bookings]}
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
