from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Index
)
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Server(Base):
    """Represents a server to be monitored."""
    __tablename__ = "servers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    ip_address = Column(String, nullable=False, index=True)
    location = Column(String, nullable=True)
    ping_interval = Column(Integer, default=60)  # in seconds
    last_ping_time = Column(DateTime, nullable=True, index=True)  # Last successful ping time
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    ping_result = relationship("PingResult", back_populates="server", uselist=False, cascade="all, delete-orphan")
    alerts = relationship("AlertLog", back_populates="server", cascade="all, delete-orphan")
    ping_logs = relationship("PingLog", back_populates="server", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Server(name={self.name}, ip={self.ip_address}, active={self.is_active})>"

class PingResult(Base):
    """Stores the most recent ping result for a server."""
    __tablename__ = "ping_result"

    id = Column(Integer, primary_key=True)
    server_id = Column(Integer, ForeignKey("servers.id"), nullable=False, unique=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    is_successful = Column(Boolean, index=True)
    latency_ms = Column(Float)

    server = relationship("Server", back_populates="ping_result", uselist=False)

    def __repr__(self):
        return f"<PingResult(server={self.server_id}, success={self.is_successful}, latency={self.latency_ms})>"
    
class AlertLog(Base):
    """Logs alerts for server events (downtime, recovery, etc.)."""
    __tablename__ = "alert_logs"

    id = Column(Integer, primary_key=True)
    server_id = Column(Integer, ForeignKey("servers.id"), nullable=False, index=True)
    alert_type = Column(String, index=True)  # e.g., "offline", "recovery"
    message = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    server = relationship("Server", back_populates="alerts")

    def __repr__(self):
        return f"<AlertLog(server={self.server_id}, type={self.alert_type}, time={self.timestamp})>"

class PingLog(Base):
    """Historical log of all ping attempts."""
    __tablename__ = "ping_logs"

    id = Column(Integer, primary_key=True)
    server_id = Column(Integer, ForeignKey("servers.id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    response_time = Column(Float)
    success = Column(Boolean, default=False, index=True)

    server = relationship("Server", back_populates="ping_logs")
    
    def __repr__(self):
        return f"<PingLog(server={self.server_id}, time={self.timestamp}, success={self.success}, response_time={self.response_time})>"
    
class AppSetting(Base):
    """Application-wide settings."""
    __tablename__ = "app_settings"

    key = Column(String, primary_key=True)
    value = Column(String, nullable=False)

    def __repr__(self):
        return f"<AppSettings(key={self.key}, value={self.value})>"

# Add indexes for better performance (only if they don't exist)
from sqlalchemy import text

# Create indexes only if they don't exist
def create_indexes_if_not_exist():
    from sqlalchemy import create_engine
    from db.init_db import DB_URL
    
    engine = create_engine(DB_URL)
    
    # Check if indexes exist before creating
    with engine.connect() as conn:
        # Server table indexes
        if not conn.execute(text("SELECT name FROM sqlite_master WHERE type='index' AND name='ix_servers_name'")).fetchone():
            conn.execute(text("CREATE INDEX ix_servers_name ON servers (name)"))
        
        if not conn.execute(text("SELECT name FROM sqlite_master WHERE type='index' AND name='ix_servers_ip_address'")).fetchone():
            conn.execute(text("CREATE INDEX ix_servers_ip_address ON servers (ip_address)"))
        
        if not conn.execute(text("SELECT name FROM sqlite_master WHERE type='index' AND name='ix_servers_is_active'")).fetchone():
            conn.execute(text("CREATE INDEX ix_servers_is_active ON servers (is_active)"))
        
        # PingResult table indexes
        if not conn.execute(text("SELECT name FROM sqlite_master WHERE type='index' AND name='ix_ping_result_server_id'")).fetchone():
            conn.execute(text("CREATE INDEX ix_ping_result_server_id ON ping_result (server_id)"))
        
        if not conn.execute(text("SELECT name FROM sqlite_master WHERE type='index' AND name='ix_ping_result_is_successful'")).fetchone():
            conn.execute(text("CREATE INDEX ix_ping_result_is_successful ON ping_result (is_successful)"))
        
        # AlertLog table indexes
        if not conn.execute(text("SELECT name FROM sqlite_master WHERE type='index' AND name='ix_alert_logs_server_id'")).fetchone():
            conn.execute(text("CREATE INDEX ix_alert_logs_server_id ON alert_logs (server_id)"))
        
        if not conn.execute(text("SELECT name FROM sqlite_master WHERE type='index' AND name='ix_alert_logs_alert_type'")).fetchone():
            conn.execute(text("CREATE INDEX ix_alert_logs_alert_type ON alert_logs (alert_type)"))
        
        # PingLog table indexes
        if not conn.execute(text("SELECT name FROM sqlite_master WHERE type='index' AND name='ix_ping_logs_server_id'")).fetchone():
            conn.execute(text("CREATE INDEX ix_ping_logs_server_id ON ping_logs (server_id)"))
        
        if not conn.execute(text("SELECT name FROM sqlite_master WHERE type='index' AND name='ix_ping_logs_success'")).fetchone():
            conn.execute(text("CREATE INDEX ix_ping_logs_success ON ping_logs (success)"))
