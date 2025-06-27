from db.init_db import init_db
from db.models import Server, AppSetting, PingLog, PingResult
from db.utils import set_setting
from agent.metrics_collector import log_ping_for_server
from datetime import datetime, timedelta
import time
import logging
from logging.handlers import RotatingFileHandler
import os
import subprocess

# Ensure logs directory exists
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

# Format
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

def run_once(): # This function is called once to ping all active servers for debugging purposes
    session = init_db()
    servers = session.query(Server).filter_by(is_active=True).all()

    if not servers:
        logging.info("⚠️ No active servers to ping.")
        return

    logging.info(f"📡 Pinging {len(servers)} servers...")
    for server in servers:
        log_ping_for_server(server)

def ping_host(ip_address):
    try:
        result = subprocess.run(
            ["ping", "-n", "1", "-w", "2000", ip_address],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )

        stdout = result.stdout.lower()

        # On Windows, success usually includes "reply from"
        success = result.returncode == 0 and "reply from" in stdout

        print(f"🔧 ping_host for {ip_address}:\n  returncode={result.returncode}\n  success={success}\n  stdout={stdout}\n  stderr={result.stderr}")
        return success
    except Exception as e:
        print(f"⚠️ ping_host exception: {e}")
        return False


def run_loop():
    try:
        while True:
            set_setting("agent_last_seen", datetime.utcnow().isoformat())
            session = init_db()

            if should_agent_pause(session):
                session.close()
                time.sleep(5)
                continue

            now = datetime.utcnow()
            servers = session.query(Server).filter_by(is_active=True).all()

            for server in servers:
                try:
                    interval = server.ping_interval or 60
                    due_time = (server.last_ping_time or datetime.min) + timedelta(seconds=interval)
                    print(f"⏳ {server.name}: now={now}, due={due_time}, last_ping={server.last_ping_time}")
                    if now >= due_time:
                        logging.info(f"📡 Pinging {server.name} @ {server.ip_address}")

                        # Track ping time
                        start_time = time.time()
                        is_up = ping_host(server.ip_address)
                        print(f"🎯 Ping returned: {is_up} for {server.name}")
                        response_time = round((time.time() - start_time) * 1000)  # milliseconds

                        # Save to PingLog
                        log = PingLog(server_id=server.id, success=is_up, timestamp=now)
                        server.last_ping_time = now
                        session.add(log)

                        # Update or create PingResult (ONLY when we’ve just pinged)
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

                        logging.info(f"📝 PingResult updated for {server.name}: {'✅' if is_up else '❌'}")

                except Exception as e:
                    logging.error(f"❌ Error pinging {server.name}: {e}")

            session.close()
            time.sleep(5)



    except KeyboardInterrupt:
        logging.info("👋 Agent terminated by user.")

def should_agent_pause(session):
    setting = session.query(AppSetting).filter_by(key="agent_status").first()
    print(f"Agent pause check: {setting.key} = {setting.value}") if setting else print("No agent_status setting found.")
    return setting and setting.value == "paused"

if __name__ == "__main__":
    run_loop()