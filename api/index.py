from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client
import os
import uuid
from datetime import datetime

app = Flask(__name__)
CORS(app)

supabase_url = os.environ.get('SUPABASE_URL')
supabase_key = os.environ.get('SUPABASE_KEY')
supabase = create_client(supabase_url, supabase_key)

@app.route('/')
def home():
    return jsonify({'message': 'Stranger Dating LIVE! ??'})

@app.route('/log', methods=['POST'])
def log():
    data = request.json
    # TODO: supabase insert when DB ready
    return jsonify({'status': 'logged'})

# VERCEL handler FIRST - NO imports above this
def handler(request):
    """Vercel Python Runtime Handler"""
    from flask.wrappers import Request as FlaskRequest
    from werkzeug.wrappers import Response
    
    flask_request = FlaskRequest(request.environ)
    response = app(flask_request.environ, flask_request.start_response)
    return Response(response)

if __name__ == '__main__':
    app.run()
