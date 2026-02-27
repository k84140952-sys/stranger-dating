import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from supabase import create_client, Client
import uuid
from datetime import datetime

# Vercel env vars (no .env file needed)
load_dotenv()

app = Flask(__name__)
CORS(app)

# Supabase
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/')
def home():
    return jsonify({
        'message': 'Stranger Dating API - LIVE! ??',
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

@app.route('/log', methods=['POST'])
def log():
    data = request.json
    supabase.table('logs').insert({
        'id': str(uuid.uuid4()),
        'data': data
    }).execute()
    return jsonify({'status': 'logged'})

# VERCEL REQUIRED: handler at TOP LEVEL
def handler(request):
    from werkzeug.wrappers import Request
    req = Request(request.environ)
    response = app(req.environ, req.start_response)
    return response([b""])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)
