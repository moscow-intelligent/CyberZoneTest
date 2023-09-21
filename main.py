from datetime import date

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base, User, Booking

DATABASE_URL = 'localhost:5432'

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


@app.post("/register")
def create_user(name: str, password: str):
    session = Session()
    user = User(username=name, password=password, created_at=date.today())
    session.add(user)
    session.commit()
    session.close()

    return JSONResponse(
        status_code=200, content={"status_code": 200, "message": "user registered"}
    )


@app.delete("/delete/{user_id}")
def delete_user(user_id: int):
    session = Session()
    user = session.query(User).get(user_id)
    if not user:
        return JSONResponse(
            status_code=404, content={"status_code": 404, "message": "user not found"}
        )
    session.delete(user)
    session.commit()
    session.close()


@app.exception_handler(Exception)
def exception_handler(request, exc):
    json_resp = get_default_error_response()
    return json_resp


def get_default_error_response(status_code=500, message="Internal Server Error"):
    return JSONResponse(
        status_code=status_code,
        content={"status_code": status_code, "message": message},
    )
