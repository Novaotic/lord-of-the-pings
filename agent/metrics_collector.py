import logging
from datetime import datetime
from db.models import PingLog, Server, AlertLog
from db.init_db import init_db
from agent.heartbeat import ping_host

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def log_ping_for_server(server):
    """Pings a server and logs the result into PingLog."""
    try:
        session = init_db()
        result = ping_host(server.ip_address)

        ping_log = PingLog(
            server_id=server.id,
            timestamp=datetime.utcnow(),
            response_time=result["response_time"],
            success=result["success"]
        )

        session.add(ping_log)
        session.commit()
        logging.info(f"📡 Logged: {ping_log}")

        if should_trigger_downtime_alert(session, server.id):
            alert = AlertLog(
                server_id=server.id,
                alert_type="downtime",
                message="Server failed 3 consecutive pings."
            )
            session.add(alert)
            session.commit()
            logging.info(f"🚨 Alert triggered: {alert}")

        if should_trigger_recovery_alert(session, server.id):
            alert = AlertLog(
                server_id=server.id,
                alert_type="recovery",
                message="Server recovered after downtime."
            )
            session.add(alert)
            session.commit()
            logging.info(f"✅ Recovery alert triggered: {alert}")
    except Exception as e:
        logging.error(f"Error in log_ping_for_server: {e}")

def should_trigger_downtime_alert(session, server_id, window=3):
    """
    Checks if the last `window` logs were all failures.
    """
    try:
        logs = (
            session.query(PingLog)
            .filter_by(server_id=server_id)
            .order_by(PingLog.timestamp.desc())
            .limit(window)
            .all()
        )
        return len(logs) == window and all(not log.success for log in logs)
    except Exception as e:
        logging.error(f"Error in should_trigger_downtime_alert: {e}")
        return False

def should_trigger_recovery_alert(session, server_id):
    """
    Triggers recovery alert if the most recent ping is successful,
    and at least 3 previous logs were failures.
    """
    try:
        logs = (
            session.query(PingLog)
            .filter_by(server_id=server_id)
            .order_by(PingLog.timestamp.desc())
            .limit(4)
            .all()
        )

        if len(logs) < 4:
            return False

        return (
            logs[0].success and        # most recent ping succeeded
            all(not log.success for log in logs[1:])  # previous 3 were failures
        )
    except Exception as e:
        logging.error(f"Error in should_trigger_recovery_alert: {e}")
        return False
