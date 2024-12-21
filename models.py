# models.py
from sqlalchemy import Column, BigInteger, String, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=True)
    username = Column(String, nullable=True)
    variant_number = Column(Integer, default=0)  

    def __repr__(self):
        return (f"<User(id={self.id}, user_id={self.user_id}, first_name={self.first_name}, "
                f"last_name={self.last_name}, username={self.username}, variant_number={self.variant_number})>")
