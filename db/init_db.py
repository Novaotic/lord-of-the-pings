import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models import Base, create_indexes_if_not_exist

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Database URL - can be overridden by environment variable
DB_URL = os.getenv('DATABASE_URL', 'sqlite:///lord_of_the_pings.db')

def init_db():
    """Initialize the database and create tables."""
    try:
        engine = create_engine(DB_URL, echo=False)  # Set echo=False for production
        Base.metadata.create_all(engine)  # Create all tables defined in models
        create_indexes_if_not_exist()  # Create indexes if they don't exist
        logging.info("Database initialized and tables created successfully.")
        Session = sessionmaker(bind=engine)
        return Session()  # Return a new session for use
    except Exception as e:
        logging.error(f"Failed to initialize database: {e}")
        raise

if __name__ == "__main__":
    try:
        init_db()  # Run the initialization if this script is executed directly
        print("Database initialization completed successfully.")
    except Exception as e:
        print(f"Database initialization failed: {e}")
        exit(1)
