from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timezone
import os
import json

app = Flask(__name__)
CORS(app)

# ==============================
# GLOBALS
# ==============================
EVENTS = []  # in-memory events for live view
MAX_EVENTS = 10000
SERVER_START = datetime.now(timezone.utc)
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

def now():
    return datetime.now(timezone.utc)

def get_today_file():
    """Returns the JSON file path for today."""
    return os.path.join(DATA_DIR, f"{datetime.now().date()}.json")

def save_event(event):
    """Append an event to today's file."""
    today_file = get_today_file()
    if os.path.exists(today_file):
        with open(today_file, "r") as f:
            events = json.load(f)
    else:
        events = []
    events.append(event)
    with open(today_file, "w") as f:
        json.dump(events, f)

# ==============================
# ESP32 → POST STATE (ALL MACHINES)
# ==============================
@app.route("/api/machine_state", methods=["POST"])
def receive_state():
    data = request.get_json(force=True)
    state = int(data.get("state", 0))
    machine_id = str(data.get("machine_id", "UNKNOWN"))
    ts = now().timestamp()

    event = {"ts": ts, "state": state, "machine_id": machine_id}

    # Save to memory for live view
    EVENTS.append(event)
    if len(EVENTS) > MAX_EVENTS:
        EVENTS.pop(0)

    # Save to today's JSON file
    save_event(event)

    print(f"[ESP32] {machine_id} -> {state}")
    return jsonify({"ok": True})

# ==============================
# FRONTEND → LIVE HISTORY (PER MACHINE)
# ==============================
@app.route("/api/machine_state/history/<machine_id>")
def history_live(machine_id):
    now_ts = now().timestamp()

    # Filter only this machine
    machine_events = [e for e in EVENTS if e["machine_id"] == machine_id]

    # Extend last state to "now" for live view
    if machine_events:
        last = machine_events[-1]
        machine_events = machine_events.copy()
        machine_events.append({
            "ts": now_ts,
            "state": last["state"],
            "machine_id": machine_id,
            "live": True
        })

    return jsonify({
        "server_start": SERVER_START.timestamp(),
        "machine_id": machine_id,
        "events": machine_events
    })

# ==============================
# FRONTEND → HISTORY FOR A SPECIFIC DAY
# ==============================
@app.route("/api/machine_state/history/<machine_id>/<date_str>")
def history_day(machine_id, date_str):
    """
    Returns events for a specific machine and specific day.
    date_str format: YYYY-MM-DD
    """
    day_file = os.path.join(DATA_DIR, f"{date_str}.json")
    if os.path.exists(day_file):
        with open(day_file, "r") as f:
            all_events = json.load(f)
        # Filter by machine
        machine_events = [e for e in all_events if e["machine_id"] == machine_id]
    else:
        machine_events = []

    return jsonify({
        "server_start": SERVER_START.timestamp(),
        "machine_id": machine_id,
        "events": machine_events
    })

# ==============================
# DEBUG (OPTIONAL)
# ==============================
@app.route("/debug/<machine_id>/<int:state>")
def debug(machine_id, state):
    event = {"ts": now().timestamp(), "state": state, "machine_id": machine_id}
    EVENTS.append(event)
    save_event(event)
    return jsonify({"forced": state, "machine": machine_id})

# ==============================
# RUN
# ==============================
if __name__ == "__main__":
    print("🚀 Flask running on 0.0.0.0:5000")
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
        use_reloader=False
    )
