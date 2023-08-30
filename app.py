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
URL = 'https://464d9ef8f4677c49a6.gradio.live'

# Load environment variables
PROJECT_ID = os.environ.get('PROJECT_ID')
PRIVATE_KEY_ID = os.environ.get('PRIVATE_KEY_ID')
PRIVATE_KEY = os.environ.get('PRIVATE_KEY').replace('\\n', '\n')
CLIENT_EMAIL = os.environ.get('CLIENT_EMAIL')
CLIENT_ID = os.environ.get('CLIENT_ID')
AUTH_URI = os.environ.get('AUTH_URI')
TOKEN_URI = os.environ.get('TOKEN_URI')
AUTH_PROVIDER_CERT_URL = os.environ.get('AUTH_PROVIDER_CERT_URL')
CLIENT_CERT_URL = os.environ.get('CLIENT_CERT_URL')

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

    prompts = [prompt + ', wikihow illustration' for prompt in prompts2]
    image_urls = []

    for index, prompt in enumerate(prompts):
        payload = {
            "prompt": prompt,
            "steps": 15,
            "width": "768",
            "height": "512"
        }
        response = requests.post(url=f'{URL}/sdapi/v1/txt2img', json=payload)

        if response.status_code == 200:
            print(f'Successful for prompt {index + 1}!')
            r = response.json()

            for i in r['images']:
                image = Image.open(io.BytesIO(
                    base64.b64decode(i.split(",", 1)[0])))
                png_payload = {"image": "data:image/png;base64," + i}
                response2 = requests.post(
                    url=f'{URL}/sdapi/v1/png-info', json=png_payload)

                pnginfo = PngImagePlugin.PngInfo()
                pnginfo.add_text("parameters", response2.json().get("info"))
                file_name = f'output_{index + 1}_{int(time.time())}.png'
                image.save(file_name, pnginfo=pnginfo)
                image_url = upload_to_firebase(file_name)
                print(f"Image URL for prompt {index + 1}: {image_url}")
                image_urls.append(image_url)

    return jsonify({"image_urls": image_urls})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
