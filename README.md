# 🧙‍♂️ Lord of the Pings

_A beacon was lit, and the agent answered._

**Lord of the Pings** is a lightweight, battle-hardened network monitoring agent forged to watch over your servers like the Eye of Sauron (but with better intentions). It pings configured endpoints, logs uptime and latency, and reports its findings to a Flask-powered web dashboard in real time.

---

## ✨ Features

- 🌐 ICMP ping health checks with latency tracking
- 📦 SQLite-backed storage for all servers, logs, and last known status
- 🧭 Live dashboard UI with ✅ / ❌ indicators to show who still walks in the land of the living
- ⚙️ Agent that checks regularly and sleeps lightly
- 📜 Rotating log files worthy of the archives of Minas Tirith
- 🔩 Designed to scale and evolve—API-ready, alert-capable, and open to elvish enhancements
- 🎨 Modern, responsive UI with improved user experience
- 🛡️ Robust error handling and logging
- 📊 Real-time status updates
- 🔒 Input validation and sanitization
- 📈 Performance-optimized database queries

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

### 3. Environment Configuration

Create a `.env` file (copy from `.env.example`):
```env
FLASK_SECRET_KEY=you-shall-not-pass-this-to-version-control
FLASK_ENV=development
DATABASE_URL=sqlite:///lord_of_the_pings.db
LOG_LEVEL=INFO
```

### 4. Initialize Database

```bash
python -m db.init_db
```

### 5. Start Flask UI

```bash
flask run
```
The beacon will shine at http://localhost:5000

## Running the Agent

To summon the agent to roam the lands and check for life:
```bash
python agent/agent.py
```
You can pause or resume it via the dashboard.

## 🚀 Quick Start

1. Install dependencies: `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and configure
3. Initialize database: `python -m db.init_db`
4. Start the web server: `flask run`
5. In a separate terminal, start the agent: `python agent/agent.py`

## 🛠️ Features

### Core Functionality
- **Real-time Monitoring**: Continuous ping monitoring with configurable intervals
- **Alert System**: Automatic alerts for downtime and recovery events
- **Historical Logging**: Complete ping history with latency tracking
- **Responsive UI**: Modern, mobile-friendly dashboard

### Advanced Features
- **Agent Management**: Start/stop agent from dashboard
- **Server Management**: Add/edit/delete servers with validation
- **Real-time Updates**: Live status updates without page refresh
- **Error Handling**: Robust error handling and logging
- **API Endpoints**: RESTful API for programmatic access
- **Form Validation**: Client and server-side validation
- **Database Indexing**: Optimized queries for performance

## 📊 Models

- **Server**: Describes each host with IP, name, and ping interval
- **PingResult**: The most recent ping success/failure
- **PingLog**: Historical log of all ping attempts
- **AlertLog**: Record of alerts (downtime, recovery, etc.)
- **AppSetting**: Application-wide settings

## 🛡️ Security

- Flask secret key for session security
- Input validation and sanitization
- Secure database connections
- CSRF protection
- Form validation with WTForms

## 📈 Performance

- Efficient database queries with proper indexing
- Optimized ping intervals
- Asynchronous agent operations
- Memory-efficient logging
- Database connection pooling

## 🧪 Development

### Running Tests
```bash
python -m pytest tests/ -v
```

### Code Style
- PEP8 compliant
- Type hints where appropriate
- Comprehensive docstrings
- Unit and integration tests

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License
MIT License (see LICENSE)

## 🎉 Credits
Crafted by Cody Poe, while finding new reasons to bang my head on a desk. Special thanks to the open source community for inspiration and tools.

---

**May your servers always respond, and your pings never timeout!** 🧙‍♂️
