import os
from datetime import datetime

from sqlalchemy import Column, Date, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

DB_CONNECTION_STRING = os.getenv("DB_CONNECTION_STRING")

if not DB_CONNECTION_STRING:
    raise EnvironmentError(
        "The environment variable DB_CONNECTION_STRING is not set. Please set it before running the application."
    )

# Define SQLAlchemy base model
Base = declarative_base()


# Define table models
class UsersCities(Base):
    __tablename__ = "users_cities"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    city = Column(String(254))
