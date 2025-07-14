import os
import logging
import sys
import pathlib

# Add the parent directory to the Python path
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from flask import Flask, render_template, redirect, request, url_for, flash, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField, SubmitField
from wtforms.validators import DataRequired, IPAddress, NumberRange
from sqlalchemy.orm import joinedload
from db.init_db import init_db
from db.utils import get_setting, set_setting
from db.models import Server, AlertLog
from dotenv import load_dotenv
from datetime import datetime, timedelta
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "you-shall-not-pass-this-to-version-control")

# Form classes for validation
class AddServerForm(FlaskForm):
    name = StringField('Server Name', validators=[DataRequired()])
    ip_address = StringField('IP Address', validators=[DataRequired(), IPAddress()])
    ping_interval = IntegerField('Ping Interval (seconds)', validators=[DataRequired(), NumberRange(min=1, max=3600)])
    is_active = BooleanField('Active')
    submit = SubmitField('Add Server')

class EditServerForm(FlaskForm):
    name = StringField('Server Name', validators=[DataRequired()])
    ip_address = StringField('IP Address', validators=[DataRequired(), IPAddress()])
    ping_interval = IntegerField('Ping Interval (seconds)', validators=[DataRequired(), NumberRange(min=1, max=3600)])
    is_active = BooleanField('Active')
    submit = SubmitField('Update Server')

@app.route('/')
def home():
    try:
        session = init_db()
        servers = (
            session.query(Server)
            .options(
                joinedload(Server.ping_result),
                joinedload(Server.ping_logs),
                joinedload(Server.alerts)
            )
            .all()
        )
        alerts = session.query(AlertLog).order_by(AlertLog.timestamp.desc()).limit(10).all()
        
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
        
        return render_template('home.html', servers=servers, alerts=alerts, 
                             agent_status=agent_status, status_color=status_color)
    except Exception as e:
        logging.error(f"Error in home route: {e}")
        flash("An error occurred while loading the dashboard", "error")
        return render_template('home.html', servers=[], alerts=[], agent_status="unknown", status_color="offline")

@app.route("/add-server", methods=["GET", "POST"])
def add_server():
    form = AddServerForm()
    
    if form.validate_on_submit():
        try:
            session = init_db()
            new_server = Server(
                name=form.name.data,
                ip_address=form.ip_address.data,
                ping_interval=form.ping_interval.data,
                is_active=form.is_active.data
            )
            session.add(new_server)
            session.commit()
            flash(f"Server '{form.name.data}' added successfully!", "success")
            return redirect(url_for('home'))
        except Exception as e:
            logging.error(f"Error adding server: {e}")
            flash("An error occurred while adding the server", "error")
    
    return render_template('add_server.html', form=form)

@app.route("/edit-server/<int:server_id>", methods=["GET", "POST"])
def edit_server(server_id):
    session = init_db()
    server = session.query(Server).get(server_id)
    
    if not server:
        flash("Server not found!", "error")
        return redirect(url_for('home'))
    
    form = EditServerForm(obj=server)
    
    if form.validate_on_submit():
        try:
            server.name = form.name.data
            server.ip_address = form.ip_address.data
            server.ping_interval = form.ping_interval.data
            server.is_active = form.is_active.data
            session.commit()
            flash(f"Server '{server.name}' updated successfully!", "success")
            return redirect(url_for('home'))
        except Exception as e:
            logging.error(f"Error updating server: {e}")
            flash("An error occurred while updating the server", "error")
    
    return render_template('edit_server.html', form=form, server=server)

@app.route("/delete-server/<int:server_id>", methods=["POST"])
def delete_server(server_id):
    try:
        session = init_db()
        server = session.query(Server).get(server_id)
        
        if not server:
            flash("Server not found!", "error")
        else:
            session.delete(server)
            session.commit()
            flash(f"Server '{server.name}' deleted successfully!", "success")
    except Exception as e:
        logging.error(f"Error deleting server: {e}")
        flash("An error occurred while deleting the server", "error")
    
    return redirect(url_for('home'))

@app.route("/toggle-agent", methods=["POST"])
def toggle_agent():
    try:
        current_status = get_setting("agent_status", "running")
        new_status = "paused" if current_status == "running" else "running"
        set_setting("agent_status", new_status)
        flash(f"Agent status changed to {new_status}", "success")
    except Exception as e:
        logging.error(f"Error toggling agent: {e}")
        flash("An error occurred while changing agent status", "error")
    
    return redirect(url_for('home'))

@app.route("/settings", methods=["GET", "POST"])
def settings():
    if request.method == "POST":
        try:
            set_setting("agent_status", request.form.get("agent_status"))
            set_setting("ping_interval", request.form.get("ping_interval"))
            flash("Settings updated successfully!", "success")
            return redirect(url_for('settings'))
        except Exception as e:
            logging.error(f"Error updating settings: {e}")
            flash("An error occurred while updating settings", "error")
    
    return render_template('settings.html',
                         agent_status=get_setting("agent_status", "running"),
                         ping_interval=get_setting("ping_interval", 60))

@app.route("/agent_status")
def agent_status_partial():
    try:
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
    except Exception as e:
        logging.error(f"Error in agent_status_partial: {e}")
        return render_template("partials/agent_status.html", agent_status="unknown", status_color="offline")

@app.route("/api/servers", methods=["GET"])
def api_servers():
    """API endpoint to get all servers."""
    try:
        session = init_db()
        servers = session.query(Server).all()
        servers_data = []
        for server in servers:
            servers_data.append({
                'id': server.id,
                'name': server.name,
                'ip_address': server.ip_address,
                'is_active': server.is_active,
                'ping_interval': server.ping_interval
            })
        return jsonify(servers_data)
    except Exception as e:
        logging.error(f"Error in API endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
