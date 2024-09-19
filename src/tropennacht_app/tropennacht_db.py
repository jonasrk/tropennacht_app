import os
import uuid

from sqlalchemy import Column, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

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


# Function to delete a row by id and user_id (to ensure user ownership)
def delete_user_city_by_id(user_id: str, city_id: str):
    try:
        # Ensure both user_id and city_id are valid UUIDs
        user_id = uuid.UUID(user_id)
        city_id = uuid.UUID(city_id)

        # Query for the entry with the given city_id and user_id
        entry_to_delete = (
            session.query(UsersCities).filter_by(id=city_id, user_id=user_id).first()
        )

        if entry_to_delete:
            # Delete the entry from the session
            session.delete(entry_to_delete)
            # Commit the session to persist the changes
            session.commit()
            print(f"Deleted city with ID {city_id} for user {user_id}")
        else:
            print(f"No entry found for user {user_id} with city ID {city_id}")
    except ValueError:
        print(f"Invalid UUID: {user_id} or {city_id}")
    except Exception as e:
        session.rollback()
        print(f"Error deleting city: {e}")
    finally:
        session.close()


# Function to get all cities (id and name) for a user
def get_cities_for_user(user_id: str):
    try:
        # Ensure user_id is a valid UUID
        user_id = uuid.UUID(user_id)

        # Query all cities associated with the given user_id, including both id and city
        cities = (
            session.query(UsersCities.id, UsersCities.city)
            .filter_by(user_id=user_id)
            .all()
        )

        if cities:
            # Create a list of dictionaries with both id and city name
            city_list = [{"id": str(city.id), "city": city.city} for city in cities]
            print(f"Cities for user {user_id}: {city_list}")
            return city_list
        else:
            print(f"No cities found for user {user_id}")
            return []
    except ValueError:
        print(f"Invalid UUID: {user_id}")
        return []
    except Exception as e:
        session.rollback()
        print(f"Error fetching cities for user {user_id}: {e}")
        return []
    finally:
        session.close()
