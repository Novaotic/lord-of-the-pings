from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models import Base

# Choose SQLite for now-simple and file-based

DB_URL = "sqlite:///lord_of_the_pings.db"

def init_db():
    """Initialize the database and create tables."""
    engine = create_engine(DB_URL, echo=True)  # Set echo=True for SQL logging
    Base.metadata.create_all(engine)  # Create all tables defined in models
    print("Database initialized and tables created.")
    Session = sessionmaker(bind=engine)
    return Session()  # Return a new session for use

if __name__ == "__main__":
    init_db()  # Run the initialization if this script is executed directly