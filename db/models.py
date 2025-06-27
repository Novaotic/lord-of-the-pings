from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Float, ForeignKey
)
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Server(Base):
    __tablename__ = "servers"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    ip_address = Column(String, nullable=False)
    location = Column(String, nullable=True)
    ping_interval = Column(Integer, default=60)  # in seconds
    last_ping_time = Column(DateTime, nullable=True)  # Last successful ping time
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships

    ping_result = relationship("PingResult", back_populates="server", uselist=False, cascade="all, delete-orphan")
    alerts = relationship("AlertLog", back_populates="server", cascade="all, delete-orphan")
    ping_logs = relationship("PingLog", back_populates="server", cascade="all, delete-orphan")
    

    def __repr__(self):
        return f"<Server(name={self.name}, ip={self.ip_address}, active={self.is_active})>"

class PingResult(Base):
    __tablename__ = "ping_result"

    id = Column(Integer, primary_key=True)
    server_id = Column(Integer, ForeignKey("servers.id"), nullable=False, unique=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_successful = Column(Boolean)
    latency_ms = Column(Float)

    server = relationship("Server", back_populates="ping_result", uselist=False)

    def __repr__(self):
        return f"<PingResult(server={self.server_id}, success={self.is_successful}, latency={self.latency_ms})>"
    
class AlertLog(Base):
    __tablename__ = "alert_logs"

    id = Column(Integer, primary_key=True)
    server_id = Column(Integer, ForeignKey("servers.id"), nullable=False)
    alert_type = Column(String)  # e.g., "offline", "recovery"
    message = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

    server = relationship("Server", back_populates="alerts")

    def __repr__(self):
        return f"<AlertLog(server={self.server_id}, type={self.alert_type}, time={self.timestamp})>"

class PingLog(Base):
    __tablename__ = "ping_logs"

    id = Column(Integer, primary_key=True)
    server_id = Column(Integer, ForeignKey("servers.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    response_time = Column(Float)
    success = Column(Boolean, default=False)

    server = relationship("Server", back_populates="ping_logs")
    
    def __repr__(self):
        return f"<PingLog(server={self.server_id}, time={self.timestamp}, success={self.success}, response_time={self.response_time})>"
    
class AppSetting(Base):
    __tablename__ = "app_settings"

    key = Column(String, primary_key=True)
    value = Column(String, nullable=False)

    def __repr__(self):
        return f"<AppSettings(key={self.key}, value={self.value})>"