import os
import requests
import base64
import json

# Configuration
with open("credentials.json", "r") as f:
    credentials = json.load(f)

ENDPOINT = credentials["endpoint"]
API_KEY = credentials["api_key"]
headers = {
    "Content-Type": "application/json",
    "api-key": API_KEY,
}



SYSTEM_PROMPT = ""
USER_PROMPT = ""
# Payload for the request
payload = {
    "messages": [
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT
                }
            ]
        }
    ],
    "temperature": 0.7,
    "top_p": 0.95,
    "max_tokens": 800
}



def main():
    # Send request
    try:
        response = requests.post(ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
    except requests.RequestException as e:
        raise SystemExit(f"Failed to make the request. Error: {e}")

    # Handle the response as needed (e.g., print or process)
    print(response.json())


if __name__ == '__main__':
    main()