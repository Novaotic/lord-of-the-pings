import os
import logging
import subprocess
import time
import sys
import pathlib

# Add the parent directory to the Python path
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler
from db.init_db import init_db
from db.models import Server, AppSetting, PingLog, PingResult
from db.utils import set_setting
from agent.metrics_collector import log_ping_for_server

# Ensure logs directory exists
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

# Configure logging
formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# File handler
file_handler = RotatingFileHandler(
    filename=os.path.join(log_dir, "agent.log"),
    maxBytes=5 * 1024 * 1024,
    backupCount=3
)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# Get the root logger and clear existing handlers
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.handlers = []  # Clear existing handlers
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Quiet down SQLAlchemy's verbosity
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

def ping_host(ip_address):
    """Ping a host and return success status."""
    try:
        result = subprocess.run(
            ["ping", "-n", "1", "-w", "2000", ip_address],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            timeout=5
        )

        stdout = result.stdout.lower()
        # On Windows, success usually includes "reply from"
        success = result.returncode == 0 and "reply from" in stdout
        return success
    except subprocess.TimeoutExpired:
        logger.warning(f"Ping to {ip_address} timed out")
        return False
    except Exception as e:
        logger.error(f"Error pinging {ip_address}: {e}")
        return False

def run_once():
    """Run a single ping cycle for all active servers (for debugging)."""
    try:
        session = init_db()
        servers = session.query(Server).filter_by(is_active=True).all()

        if not servers:
            logger.info("⚠️ No active servers to ping.")
            return

        logger.info(f"📡 Pinging {len(servers)} servers...")
        for server in servers:
            log_ping_for_server(server)
    except Exception as e:
        logger.error(f"Error in run_once: {e}")

def should_agent_pause(session):
    """Check if the agent should pause."""
    setting = session.query(AppSetting).filter_by(key="agent_status").first()
    return setting and setting.value == "paused"

def run_loop():
    """Main agent loop that continuously pings servers and updates status."""
    try:
        while True:
            # Update heartbeat
            set_setting("agent_last_seen", datetime.utcnow().isoformat())
            session = init_db()

            # Check if agent should pause
            if should_agent_pause(session):
                session.close()
                logger.info("Agent is paused, sleeping for 5 seconds...")
                time.sleep(5)
                continue

            now = datetime.utcnow()
            servers = session.query(Server).filter_by(is_active=True).all()

            for server in servers:
                try:
                    # Check if it's time to ping this server
                    interval = server.ping_interval or 60
                    due_time = (server.last_ping_time or datetime.min) + timedelta(seconds=interval)
                    
                    if now >= due_time:
                        logger.info(f"📡 Pinging {server.name} @ {server.ip_address}")

                        # Track ping time
                        start_time = time.time()
                        is_up = ping_host(server.ip_address)
                        response_time = round((time.time() - start_time) * 1000)  # milliseconds

                        # Save to PingLog
                        log = PingLog(
                            server_id=server.id, 
                            success=is_up, 
                            timestamp=now,
                            response_time=response_time
                        )
                        server.last_ping_time = now
                        session.add(log)

                        # Update or create PingResult
                        existing = session.query(PingResult).filter_by(server_id=server.id).first()
                        if existing:
                            existing.is_successful = is_up
                            existing.latency_ms = response_time
                            existing.timestamp = datetime.utcnow()
                        else:
                            new_result = PingResult(
                                server_id=server.id,
                                is_successful=is_up,
                                latency_ms=response_time,
                                timestamp=datetime.utcnow()
                            )
                            session.add(new_result)

                        # Commit everything: PingLog + PingResult update
                        session.commit()

                        logger.info(f"📝 PingResult updated for {server.name}: {'✅' if is_up else '❌'}")

                except Exception as e:
                    logger.error(f"❌ Error pinging {server.name}: {e}")

            session.close()
            time.sleep(5)

    except KeyboardInterrupt:
        logger.info("👋 Agent terminated by user.")
    except Exception as e:
        logger.error(f"💥 Critical error in agent loop: {e}")
        # Attempt to restart the loop after a delay
        time.sleep(10)
        run_loop()  # Recursive restart

if __name__ == "__main__":
    logger.info("🚀 Starting Lord of the Pings agent...")
    run_loop()
