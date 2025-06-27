# 🧙‍♂️ Lord of the Pings

_A beacon was lit, and the agent answered._

**Lord of the Pings** is a lightweight, battle-hardened network monitoring agent forged to watch over your servers like the Eye of Sauron (but with better intentions). It pings configured endpoints, logs uptime and latency, and reports its findings to a Flask-powered web dashboard in real time. Currently it is far from finished, but the base is here.

---

## ✨ Features

- 🌐 ICMP ping health checks with latency tracking
- 📦 SQLite-backed storage for all servers, logs, and last known status
- 🧭 Live dashboard UI with ✅ / ❌ indicators to show who still walks in the land of the living
- ⚙️ Agent that checks regularly and sleeps lightly
- 📜 Rotating log files worthy of the archives of Minas Tirith
- 🔩 Designed to scale and evolve—API-ready, alert-capable, and open to elvish enhancements

---

## 🧱 Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourname/lord-of-the-pings.git
cd lord-of-the-pings
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Enviroment Configuration

Create a .env file:
```env
FLASK_SECRET_KEY=you-shall-not-pass-this-to-version-control
```

### 4. Start Flask UI

```bash
flask run
```
The beacon will shine at http://localhost:5000

## Running the Agent

To summon the agent to roam the lands and check for life:
```bash
python agent/agent.py
```
You can pause or resume it via internal settings.

## Models

* Server: Describes each host
* PingResult: The most recent ping success/failure
* PingLog: A log full of pings, success and failure
* AlertLog: A record of alerts (Not currently fully implemented.)

## License
MIT License (see LICENSE)

## Credits
Crafted by me, Cody Poe, while finding new resons to bang my head on a desk.