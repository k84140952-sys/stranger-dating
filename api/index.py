from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import uuid
from datetime import datetime

load_dotenv()

app = Flask(__name__)
CORS(app)

# Supabase
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
supabase = None
if supabase_url and supabase_key:
    from supabase import create_client
    supabase = create_client(supabase_url, supabase_key)

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'message': '?? Stranger Dating API - VERCEL LIVE!',
        'timestamp': datetime.utcnow().isoformat(),
        'supabase': bool(supabase)
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'uptime': '100%'})

@app.route('/log', methods=['POST'])
def log_event():
    if not supabase:
        return jsonify({'error': 'Supabase not configured'}), 500
    
    data = request.get_json() or {}
    result = supabase.table('logs').insert({
        'id': str(uuid.uuid4()),
        'data': data,
        'created_at': datetime.utcnow()
    }).execute()
    
    return jsonify({'status': 'logged', 'id': result.data[0]['id']})

@app.route('/favicon.ico', methods=['GET'])
def favicon():
    return '', 204  # Kill favicon spam

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port, debug=False)
