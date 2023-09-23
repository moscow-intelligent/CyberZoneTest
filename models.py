from sqlalchemy import Column, Date, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)
    created_at = Column(Date)
    updated_at = Column(Date)


class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    comment = Column(String)

    def to_json(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "start_time": str(self.start_time.strftime("%d-%m-%Y %H:%M:%S")),
            "end_time": str(self.end_time.strftime("%d-%m-%Y %H:%M:%S")),
            "comment": self.comment
        }
