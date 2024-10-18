import json
from parse_pdf import get_text_from_pdf
from pydantic import BaseModel
from openai import AzureOpenAI
from typing import Optional


"""
Tady nadefinuj, jak to ma vypadat:
"""

class TransformerInfo(BaseModel):
    quantity: float
    suppliers_currency: str
    transformer_unit_price: float
    rated_power_kVA: Optional[float] = None
    dry_or_oil: str


#filepath = '04 - Data Transformer/Examples/QT-20-Hitachi2_Rev0.pdf'

#filepath = '04 - Data Transformer/Examples/2022 08 03 SGB Ang SGB4 R00.pdf'

filepath = '04 - Data Transformer/Examples/QT-22-Hitachi9_Rev0.pdf'

# filepath = '04 - Data Transformer/Examples/QUOTATION Sonmez2.pdf'


text = get_text_from_pdf(filepath)
print(f"Extracted text: {text}")

# Define prompts
system_prompt = "You are an expert finder of key information from text."
user_prompt = (f"Extract the requested information from the offer about transformers."
               f"Each offer is selling transformer units. Quantity explains how many transformer units are being sold."
               f"Be careful, the offers may contain information about it's subcomponents as well."
               f"The unit price refers to the price for one transformer unit."
               f"Offer text: \\n {text}")



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

    return transformer_info



if __name__ == '__main__':
    main()