import os
from time import sleep

import requests
import base64
import json
from parse_pdf import get_text_from_pdf


example_list = ['QT-20-Hitachi2_Rev0.pdf', '2022 08 03 SGB Ang SGB4 R00.pdf', 'Best2 - A0R0 - BEST Technical Datasheet.PDF',
                'QT-22-Hitachi9_Rev0.pdf', 'QUOTATION Sonmez2.pdf', 'RDOSea3A.pdf', 'SGB4 Datasheet Pos.1000.pdf']

filepath = '04 - Data Transformer/Examples/'

# parsed_pdfs = dict(zip(example_list, [get_text_from_pdf(filepath+filename) for filename in example_list]))
import json
from parse_pdf import get_text_from_pdf
from pydantic import BaseModel
from openai import AzureOpenAI


class TransformerInfo(BaseModel):
    date: str
    rated_power: int
    # derated_power: int
    # secondary_rated_power: int
    primary_winding: str
    secondary_winding: str
    no_load_loss: int
    full_load_loss_75: int
    full_load_loss_120: int
    rated_volt_primary_side: float


# Configuration
with open("credentials.json", "r") as f:
    credentials = json.load(f)

ENDPOINT = credentials["endpoint"]
API_KEY = credentials["api_key"]
headers = {
    "Content-Type": "application/json",
    "api-key": API_KEY,
}

system_prompt = ("You are an expert finder of key information from text."
                 "You always reply just with the information, no explanations. Provide only one value per information."
                 "Your task is to find information regarding tranformators and transformators only. Please refrain from providing"
                 "imformation for any other type of device. Make sure your information is always correct."
                 "If the tasked information is not provided, reply with a NA value.")


def get_credentials():
    with open("credentials.json", "r") as f:
        return json.load(f)


def initialize_client(credentials):
    return AzureOpenAI(
        azure_endpoint=credentials["endpoint"],
        api_key=credentials["api_key"],
        api_version="2024-08-01-preview"
    )


def main():
    for file in example_list:
        text = get_text_from_pdf(filepath + file)
        # Initialize client
        if file == '2022 08 03 SGB Ang SGB4 R00.pdf':
            text+= get_text_from_pdf(filepath + 'SGB4 Datasheet Pos.1000.pdf')
        print(f"Now in {file}")
        user_prompt = f"""
            Find these informations from the text. Don't give any explanations, fill only the places indicated with "___".
             {text}
            Date: ___
            Rated power[kVA]: ___
            Primary winding material[Aluminium/Copper]: ___
            Secondary winding material[Aluminium/Copper]: ___
            No load losses[W]: ___
            Full Load Loss at 75°C [W]
            Full Load Loss at 120°C [W]
            Rated Voltage Primary side[kV]: ___
            """
        credentials = get_credentials()
        client = initialize_client(credentials)

        # Make the API call
        completion = client.beta.chat.completions.parse(
            model="MODEL_DEPLOYMENT_NAME",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format=TransformerInfo,
        )

        # Access the parsed response
        transformer_info = completion.choices[0].message.parsed

        # Print the structured response
        print("\nExtracted Information:")
        print(json.dumps(transformer_info.model_dump(), indent=2))

        sleep(10)
        # return transformer_info



if __name__ == '__main__':
    main()