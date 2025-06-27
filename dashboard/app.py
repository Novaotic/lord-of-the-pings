from flask import Flask, render_template, redirect, request, url_for, flash
from sqlalchemy.orm import joinedload
from db.init_db import init_db  # Function to initialize and return a database session
from db.utils import get_setting, set_setting  # Utility functions to retrieve settings from the database
from db.models import Server, AlertLog  # Database models
from dotenv import load_dotenv  # For loading environment variables from .env file
from datetime import datetime, timedelta
import os

load_dotenv()  # Loads environment variables from a .env file in the current working directory

def get_agent_status():
    last_seen_raw = get_setting("agent_last_seen")
    agent_mode = get_setting("agent_status", "paused")

    if not last_seen_raw:
        return f"{agent_mode} (no heartbeat)"

    last_seen = datetime.fromisoformat(last_seen_raw)
    delta = datetime.utcnow() - last_seen

    if delta < timedelta(seconds=30):
        return f"{agent_mode} (heartbeat OK)"
    elif delta < timedelta(minutes=2):
        return f"{agent_mode} (heartbeat delayed)"
    else:
        return f"{agent_mode} (no recent heartbeat)"



app = Flask(__name__)  # Create a new Flask web application instance
app.secret_key = os.getenv("FLASK_SECRET_KEY")  # Set the secret key for session management and security

@app.route('/')
def home():
    print("Home route triggered")  # Debug print to indicate the home route was accessed
    session = init_db()  # Initialize a new database session
    servers = (
    session.query(Server)
    .options(
        joinedload(Server.ping_result),
        joinedload(Server.ping_logs),
        joinedload(Server.alerts)
    )
    .all()
    )  # Retrieve all servers from the database with their related ping results, logs, and alerts
 # Retrieve all servers from the database
    alerts = session.query(AlertLog).order_by(AlertLog.timestamp.desc()).limit(10).all()  # Get the 10 most recent alerts
    raw_status = get_setting("agent_status", "paused")
    last_seen_raw = get_setting("agent_last_seen")
    # Default fallback
    status_color = "paused"
    if last_seen_raw:
        last_seen = datetime.fromisoformat(last_seen_raw)
        delta = datetime.utcnow() - last_seen
        if delta < timedelta(minutes=2):
            status_color = "offline"
        else:
            status_color = raw_status # Shoulld be running or paused
    agent_status = (
        f"{raw_status} (heartbeat OK)"
        if status_color != "offline"
        else f"{raw_status} (no recent heartbeat)"
    )
    return render_template('home.html', servers=servers, alerts=alerts, agent_status=agent_status, status_color=status_color)  # Render the home page template

@app.route("/add-server", methods=["GET", "POST"])
def add_server():
    session = init_db()  # Initialize a new database session

    if request.method == "POST":  # If the form was submitted
        name = request.form.get("name")  # Get server name from form
        ip_address = request.form.get("ip_address")  # Get IP address from form
        ping_interval = request.form.get("ping_interval", 60, type=int)  # Get ping interval from form, default to 60 seconds
        is_active = bool(request.form.get("is_active"))  # Get active status from form

        new_server = Server(name=name, ip_address=ip_address, ping_interval=ping_interval, is_active=is_active)  # Create a new Server object
        session.add(new_server)  # Add the new server to the session
        session.commit()  # Commit the transaction to save the server

        flash(f"Server '{name}' added successfully!", "success")  # Show a success message
        return redirect(url_for('home'))  # Redirect to the home page
    return render_template('add_server.html')  # Render the add server form

@app.route("/edit-server/<int:server_id>", methods=["GET", "POST"])
def edit_server(server_id):
    session = init_db()  # Initialize a new database session
    server = session.query(Server).get(server_id)  # Retrieve the server by ID

    if not server:  # If the server does not exist
        flash("Server not found!", "error")  # Show an error message
        return redirect(url_for('home'))  # Redirect to the home page
    if request.method == "POST":  # If the form was submitted
        server.name = request.form.get("name")  # Update server name
        server.ip_address = request.form.get("ip_address")  # Update IP address
        server.ping_interval = request.form.get("ping_interval", 60, type=int)  # Update ping interval, default to 60 seconds
        server.is_active = bool(request.form.get("is_active"))  # Update active status

        session.commit()  # Commit the changes to the database
        flash(f"Server '{server.name}' updated successfully!", "success")  # Show a success message
        return redirect(url_for('home'))  # Redirect to the home page
    return render_template('edit_server.html', server=server)  # Render the edit server form

@app.route("/delete-server/<int:server_id>", methods=["POST"])
def delete_server(server_id):
    session = init_db()  # Initialize a new database session
    server = session.query(Server).get(server_id)  # Retrieve the server by ID

    if not server:  # If the server does not exist
        flash("Server not found!", "error")  # Show an error message
    else:
        session.delete(server)  # Delete the server from the session
        session.commit()  # Commit the transaction to remove the server
        flash(f"Server '{server.name}' deleted successfully!", "success")  # Show a success message
    return redirect(url_for('home'))

@app.route("/toggle-agent", methods=["POST"])
def toggle_agent():
    current_status = get_setting("agent_status", "running")
    new_status = "paused" if current_status == "running" else "running"
    set_setting("agent_status", new_status)
    return redirect(url_for('home'))

@app.route("/settings", methods=["GET", "POST"])
def settings():
    if request.method == "POST":
        set_setting("agent_status", request.form.get("agent_status"))
        set_setting("ping_interval", request.form.get("ping_interval"))
        flash("Settings updated successfully!", "success")
        return redirect(url_for('settings'))

    return render_template('settings.html',
                           agent_status=get_setting("agent_status", "running"),
                           ping_interval=get_setting("ping_interval", 60)) 

@app.route("/agent_status")
def agent_status_partial():
    raw_status = get_setting("agent_status", "paused")
    last_seen_raw = get_setting("agent_last_seen")

    status_color = "paused"
    if last_seen_raw:
        last_seen = datetime.fromisoformat(last_seen_raw)
        delta = datetime.utcnow() - last_seen
        if delta > timedelta(minutes=2):
            status_color = "offline"
        else:
            status_color = raw_status

    agent_status = (
        f"{raw_status} (heartbeat OK)"
        if status_color != "offline"
        else f"{raw_status} (no recent heartbeat)"
    )

    return render_template("partials/agent_status.html", agent_status=agent_status, status_color=status_color)

if __name__ == "__main__":
    app.run(debug=True)
# Run the Flask application in debug mode
