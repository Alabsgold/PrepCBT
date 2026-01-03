import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')

def list_models():
    url = "https://generativelanguage.googleapis.com/v1beta/models"
    params = {'key': api_key}
    
    print(f"Listing models from {url}...")
    try:
        response = requests.get(url, params=params, timeout=30)
        print(f"Status: {response.status_code}")
        with open("models_out.txt", "w", encoding="utf-8") as f:
            if response.status_code == 200:
                models = response.json().get('models', [])
                for m in models:
                    if 'generateContent' in m.get('supportedGenerationMethods', []):
                        line = f"- {m['name']}"
                        print(line)
                        f.write(line + "\n")
            else:
                print(f"Error: {response.text}")
                f.write(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    list_models()
