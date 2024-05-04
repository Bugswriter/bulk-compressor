import json
import base64
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Function to load API key from environment variables
def load_api_key():
    return os.getenv("OPENAI_KEY")

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Function to send request to OpenAI API
def send_openai_request(image_path):
    # OpenAI API Key
    api_key = load_api_key()

    # Getting the base64 string
    base64_image = encode_image(image_path)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4-turbo",
        "messages": [
            {"role": "system",
             "content": "Camera titled means the camera is rotated by few degree from it's usual position such that the image orientation is rotated away by roughly 40 degreees, camera tempering means an object or anything is infront of the camera which is hiding it's view"},
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "provide the datetime, the text in image, is the camera tilted, is the camera tampered, are there people in the image as json text"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                            "detail": "low"
                        },
                    }
                ]
            }
        ],
        "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    return response

# Function to extract content from response and parse it as JSON
def extract_json_content(response):
    res = response.json()
    content = res['choices'][0]['message']['content']
    content = content.replace('```json', '')
    content = content.replace('```', '')
    content = content.strip()
    return json.loads(content)

# Main function to get JSON response from image path
def openai_frame_process(image_path):
    response = send_openai_request(image_path)
    return extract_json_content(response)
