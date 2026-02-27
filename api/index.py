import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from supabase import create_client
import uuid
from datetime import datetime

load_dotenv()

app = Flask(__name__)
CORS(app)

# Supabase (add env vars in Vercel dashboard)
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
if supabase_url and supabase_key:
    from supabase import create_client
    supabase = create_client(supabase_url, supabase_key)
else:
    supabase = None

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'message': 'Stranger Dating API - LIVE ON VERCEL! ??',
        'supabase': bool(supabase)
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'})

@app.route('/log', methods=['POST'])
def log_event():
    if not supabase:
        return jsonify({'error': 'Supabase not configured'}), 500
    
    data = request.get_json()
    result = supabase.table('logs').insert({
        'id': str(uuid.uuid4()),
        'data': data,
        'created_at': datetime.utcnow()
    }).execute()
    
    return jsonify({'status': 'logged', 'result': result})

# VERCEL OFFICIAL WSGI HANDLER
def handler(request):
    """Handle Vercel requests with Flask WSGI"""
    from werkzeug.wrappers import Request as WerkzeugRequest
    
    # Convert Vercel request to WSGI
    environ = request.environ
    req = WerkzeugRequest(environ)
    
    # Call Flask app
    def start_response(status, headers):
        pass  # Werkzeug handles this
    
    response = app(environ, start_response)
    return [b'']  # Vercel expects list of bytes

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 3000)))
