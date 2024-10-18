import os
import requests
import base64
import json
from parse_pdf import get_text_from_pdf

filepath = '04 - Data Transformer/Examples/QT-20-Hitachi2_Rev0.pdf'

text = get_text_from_pdf(filepath)
print(f"Extracted text: {text}")

# Configuration
with open("credentials.json", "r") as f:
    credentials = json.load(f)

ENDPOINT = credentials["endpoint"]
API_KEY = credentials["api_key"]
headers = {
    "Content-Type": "application/json",
    "api-key": API_KEY,
}

SYSTEM_PROMPT = ("You are an expert finder of key information from text."
                 " You always reply just with the information, no explanations.")
USER_PROMPT = f"""
Find these informations from the text. Don't give any explanations, fill only the places indicated with "___".
 {text} 
Qty: ___
Suppliers Currency: ___
Price of the offer: ___

Rated power [kVA]: ___
total secondary rated power [kVA]: ___
"""

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
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": USER_PROMPT

                }
            ]
        }
    ],
    "temperature": 0.1,
    "top_p": 0.95,
    "max_tokens": 100
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

    # Parse the response
    response_data = response.json()

    # Extract the text from the response
    if 'choices' in response_data and len(response_data['choices']) > 0:
        assistant_message = response_data['choices'][0]['message']['content']
        print("Assistant:", assistant_message)
    else:
        print("No response found in the data.")




if __name__ == '__main__':
    main()