import os
from datetime import datetime
import uuid

from sqlalchemy import Column, Date, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

from sqlalchemy.dialects.postgresql import UUID  # for PostgreSQL UUID support


DB_CONNECTION_STRING = os.getenv("DB_CONNECTION_STRING")

if not DB_CONNECTION_STRING:
    raise EnvironmentError(
        "The environment variable DB_CONNECTION_STRING is not set. Please set it before running the application."
    )

# Define SQLAlchemy base model
Base = declarative_base()


# Create an engine
engine = create_engine(DB_CONNECTION_STRING)

# Create a configured "Session" class
Session = sessionmaker(bind=engine)

# Create a session
session = Session()


# Define table models
class UsersCities(Base):
    __tablename__ = "users_cities"
    __table_args__ = {"schema": "public"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    city = Column(String(254))


# Function to add a new row
def add_user_city(user_id: str, city: str):
    try:
        # Ensure user_id is a valid UUID
        user_id = uuid.UUID(user_id)

        # Create a new UsersCities instance
        new_entry = UsersCities(user_id=user_id, city=city)
        # Add the entry to the session
        session.add(new_entry)
        # Commit the session to persist the changes
        session.commit()
        print(f"Added user {user_id} with city {city}")
    except ValueError:
        print(f"Invalid UUID: {user_id}")
    except Exception as e:
        session.rollback()
        print(f"Error adding user city: {e}")
    finally:
        session.close()


# Function to delete a row by id
def delete_user_city_by_id(city_id: str):
    try:
        # Ensure city_id is a valid UUID
        city_id = uuid.UUID(city_id)

        # Query for the entry with the given ID
        entry_to_delete = session.query(UsersCities).filter_by(id=city_id).first()
        if entry_to_delete:
            # Delete the entry from the session
            session.delete(entry_to_delete)
            # Commit the session to persist the changes
            session.commit()
            print(f"Deleted user city with ID {city_id}")
        else:
            print(f"No entry found with ID {city_id}")
    except ValueError:
        print(f"Invalid UUID: {city_id}")
    except Exception as e:
        session.rollback()
        print(f"Error deleting user city: {e}")
    finally:
        session.close()