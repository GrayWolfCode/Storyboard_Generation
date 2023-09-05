from flask import Flask, jsonify, request
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, storage
import json
import time
import requests
import io
import os
import base64
from PIL import Image, PngImagePlugin
 
app = Flask(__name__)
CORS(app)
URL = 'https://22b8932ccde1a9d745.gradio.live'
 
# Load environment variables
PROJECT_ID = os.environ.get('PROJECT_ID')
PRIVATE_KEY_ID = os.environ.get('PRIVATE_KEY_ID')
PRIVATE_KEY = os.environ.get('PRIVATE_KEY').replace('\\n', '\n')
CLIENT_EMAIL = os.environ.get('CLIENT_EMAIL')
CLIENT_ID = os.environ.get('CLIENT_ID')
AUTH_URI = os.environ.get('AUTH_URI')
TOKEN_URI = os.environ.get('TOKEN_URI')
AUTH_PROVIDER_CERT_URL = os.environ.get('AUTH_PROVIDER_CERT_URL')
CLIENT_CERT_URL = os.environ.get(' ')
 
# Create the credentials object
cred = credentials.Certificate({
 "type": "service_account",
 "project_id": PROJECT_ID,
 "private_key_id": PRIVATE_KEY_ID,
 "private_key": PRIVATE_KEY,
 "client_email": CLIENT_EMAIL,
 "client_id": CLIENT_ID,
 "auth_uri": AUTH_URI,
 "token_uri": TOKEN_URI,
 "auth_provider_x509_cert_url": AUTH_PROVIDER_CERT_URL,
 "client_x509_cert_url": CLIENT_CERT_URL
})
 
firebase_admin.initialize_app(
 cred, {'storageBucket': 'storyboard-739ee.appspot.com'})
 
 
def upload_to_firebase(file_name):
 bucket = storage.bucket()
 blob = bucket.blob(file_name)
 blob.upload_from_filename(file_name)
 blob.make_public()
 return blob.public_url
 
 
@app.route('/generate-images', methods=['POST'])
def generate_images():
 # Assuming you'll send the prompts as a list in a JSON payload.
 input = request.json.get('prompts')
 prompts2 = input.split('#')
 if not prompts2:
 return jsonify({"error": "No prompts provided."}), 400
 
 prompts = [prompt + '' for prompt in prompts2]
 image_urls = []
 
