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

class NumberTransformers(BaseModel):
    types_of_transformers_offered: float

#filepath = '04 - Data Transformer/Examples/QT-20-Hitachi2_Rev0.pdf'

#filepath = '04 - Data Transformer/Examples/2022 08 03 SGB Ang SGB4 R00.pdf'

# filepath = '04 - Data Transformer/Examples/QT-22-Hitachi9_Rev0.pdf'

#filepath = '04 - Data Transformer/Examples/QUOTATION Sonmez2.pdf'

filepath = '04 - Data Transformer/Examples/RDOSea3A.pdf'



text = get_text_from_pdf(filepath)
print(f"Extracted text: {text}")

# Define prompts
system = "You are an expert finder of key information from text."

def get_extract_prompt(transformer_number:int):
    user_extract = (f"Extract the requested information from the offer."
                    f"There could be offered multiple different transformers. Extract information about transformer "
                    f"number {transformer_number}."
                       f"Quantity explains how many transformer units number {transformer_number} are being sold."
                       f"Offer text: \\n {text}")

    return user_extract

user_count = (f"What is the number of different types of transformer units offered for sale in the report?"
              f"Report: {text}")



def get_credentials():
    with open("credentials.json", "r") as f:
        return json.load(f)


def initialize_client(credentials):
    return AzureOpenAI(
        azure_endpoint=credentials["endpoint"],
        api_key=credentials["api_key"],
        api_version="2024-08-01-preview"
    )


def main(system_prompt, user_prompt, structure):
    credentials = get_credentials()
    client = initialize_client(credentials)

    # Make the API call
    completion = client.beta.chat.completions.parse(
        model="MODEL_DEPLOYMENT_NAME",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format=structure,
    )

    # Access the parsed response
    transformer_info = completion.choices[0].message.parsed

    # Print the structured response
    print("\nExtracted Information:")
    print(json.dumps(transformer_info.model_dump(), indent=2))

    return transformer_info.model_dump()



if __name__ == '__main__':
    result = main(system, user_count, structure=NumberTransformers)
    number_of_transformers = int(result.get("types_of_transformers_offered", 0))
    for i in range(1, number_of_transformers+1):
        main(system, get_extract_prompt(i), structure=TransformerInfo)