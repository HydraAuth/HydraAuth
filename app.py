from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import requests
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Admin login credentials
ADMIN_USERNAME = "RTX"
ADMIN_PASSWORD = "3050"

# JSONBin Config
JSONBIN_API_KEY = "$2a$10$1hGEnwMBNYMxDDpusWcYwuD/BD4GDq9oyvg/1DdqhkuubiuEanqgq"
BIN_ID = "6857a2818960c979a5aee560"

HEADERS = {
    "Content-Type": "application/json",
    "X-Master-Key": JSONBIN_API_KEY
}

def load_data():
    try:
        res = requests.get(f"https://api.jsonbin.io/v3/b/{BIN_ID}/latest", headers=HEADERS)
        if res.status_code == 200:
            return res.json().get("record", {})
        return {}
    except Exception as e:
        print("Load Error:", e)
        return {}

def save_data(data):
    try:
        res = requests.put(f"https://api.jsonbin.io/v3/b/{BIN_ID}", headers=HEADERS, json=data)
        return res.status_code == 200
    except Exception as e:
        print("Save Error:", e)
        return False

@app.route("/create_app", methods=["POST"])
def create_app():
    data = load_data()
    app_name = request.form.get("app_name", "").strip()
    if not app_name:
        return jsonify({"status": "error", "message": "App name required"})

    if app_name in data:
        return jsonify({"status": "error", "message": "Application already exists"})

    data[app_name] = []

    if save_data(data):
        return jsonify({"status": "success", "message": "Application created!"})
    return jsonify({"status": "error", "message": "Failed to create app"})

@app.route("/add_user", methods=["POST"])
def add_user():
    data = load_data()
    category = request.form["category"]
    username = request.form["username"]
    password = request.form["password"]
    expiry = request.form["expiry"]

    if category not in data:
        return jsonify({"status": "error", "message": "Invalid application"})

    if any(u["Username"] == username for u in data[category]):
        return jsonify({"status": "error", "message": "Username already exists"})

    data[category].append({
        "Username": username,
        "Password": password,
        "HWID": None,
        "Status": "Active",
        "Expiry": expiry,
        "CreatedAt": datetime.today().strftime("%Y-%m-%d"),
        "Messages": []
    })

    if save_data(data):
        return jsonify({"status": "success", "message": "User added successfully"})
    return jsonify({"status": "error", "message": "Failed to add user"})

@app.route("/delete_user", methods=["POST"])
def delete_user():
    data = load_data()
    category = request.form["category"]
    username = request.form["username"]

    if category not in data:
        return jsonify({"status": "error", "message": "Invalid application"})

    original_len = len(data[category])
    data[category] = [u for u in data[category] if u["Username"] != username]

    if len(data[category]) == original_len:
        return jsonify({"status": "error", "message": "User not found"})

    if save_data(data):
        return jsonify({"status": "success", "message": "User deleted"})
    return jsonify({"status": "error", "message": "Failed to delete user"})

@app.route("/pause_user", methods=["POST"])
def pause_user():
    data = load_data()
    category = request.form["category"]
    username = request.form["username"]
    action = request.form["action"]

    if category not in data:
        return jsonify({"status": "error", "message": "Invalid application"})

    for user in data[category]:
        if user["Username"] == username:
            user["HWID"] = None if action == "pause" else ""
            user["Status"] = "Paused" if action == "pause" else "Active"
            if save_data(data):
                return jsonify({"status": "success", "message": f"User {action}d"})
            return jsonify({"status": "error", "message": "Failed to update user"})

    return jsonify({"status": "error", "message": "User not found"})

@app.route("/reset_hwid", methods=["POST"])
def reset_hwid():
    data = load_data()
    category = request.form["category"]
    username = request.form["username"]

    if category not in data:
        return jsonify({"status": "error", "message": "Invalid application"})

    for user in data[category]:
        if user["Username"] == username:
            user["HWID"] = ""
            if save_data(data):
                return jsonify({"status": "success", "message": f"HWID reset for {username}"})
            return jsonify({"status": "error", "message": "Failed to reset HWID"})

    return jsonify({"status": "error", "message": "User not found"})

@app.route("/info_user", methods=["POST"])
def info_user():
    data = load_data()
    category = request.form["category"]
    username = request.form["username"]

    if category not in data:
        return jsonify({"status": "error", "message": "Invalid application"})

    for user in data[category]:
        if user["Username"] == username:
            return jsonify({"status": "success", "data": user})

    return jsonify({"status": "error", "message": "User not found"})

@app.route("/get_users", methods=["POST"])
def get_users():
    data = load_data()
    category = request.form["category"]
    return jsonify(data.get(category, []))

@app.route("/send_message", methods=["POST"])
def send_message():
    data = load_data()
    category = request.form["category"]
    username = request.form["username"]
    message = request.form["message"]

    if not message.strip():
        return jsonify({"status": "error", "message": "Message cannot be empty"})

    if category not in data:
        return jsonify({"status": "error", "message": "Invalid application"})

    for user in data[category]:
        if user["Username"] == username:
            if "Messages" not in user:
                user["Messages"] = []
            user["Messages"].append({
                "Text": message,
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            if save_data(data):
                return jsonify({"status": "success", "message": "Message sent"})
            return jsonify({"status": "error", "message": "Failed to send message"})

    return jsonify({"status": "error", "message": "User not found"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)