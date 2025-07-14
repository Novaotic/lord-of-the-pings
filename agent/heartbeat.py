import platform
import subprocess
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def ping_host(ip_address, retries=2):
    """
    Attempts to ping a host. Retries if it fails.

    Returns:
        dict: { "success": bool, "response_time": float or None }
    """
    for attempt in range(1 + retries):
        result = _single_ping(ip_address)
        if result["success"]:
            if attempt > 0:
                logging.info(f"Success on attempt #{attempt}!")
            return result
    return result  # Final failed attempt

def _single_ping(ip_address):
    """Perform a single ping attempt."""
    param = "-n" if platform.system().lower() == "windows" else "-c"
    cmd = ["ping", param, "1", ip_address]

    try:
        start = time.time()
        subprocess.check_output(cmd, stderr=subprocess.STDOUT, timeout=3)
        duration = (time.time() - start) * 1000
        return {"success": True, "response_time": round(duration, 2)}
    except subprocess.TimeoutExpired:
        logging.warning(f"Ping to {ip_address} timed out")
        return {"success": False, "response_time": None}
    except Exception as e:
        logging.error(f"Error pinging {ip_address}: {e}")
        return {"success": False, "response_time": None}
