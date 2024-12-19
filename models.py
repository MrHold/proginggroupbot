# models.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, index=True, nullable=False)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    variant_number = Column(Integer, default=0)  # Дефолтное значение, например, 0

    def __repr__(self):
        return f"<User(user_id={self.user_id}, username={self.username}, variant_number={self.variant_number})>"
