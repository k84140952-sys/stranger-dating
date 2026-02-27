# api/index.py - VERCEL READY
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from supabase import create_client, Client
import uuid

# Load from Vercel Environment Variables (no .env needed)
load_dotenv()

# Your app
app = Flask(__name__)
CORS(app)

SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/')
def home():
    return jsonify({"message": "Stranger Dating API - LIVE! 🚀"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

# Vercel handler (REQUIRED)
def handler(request):
    from werkzeug.serving import run_simple
    from werkzeug.wsgi import DispatcherMiddleware
    return run_simple('0.0.0.0', 3000, app)

if __name__ == '__main__':
    app.run(debug=True)