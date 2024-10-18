import json
from parse_pdf import get_text_from_pdf
from pydantic import BaseModel
from openai import AzureOpenAI


"""
Tady nadefinuj, jak to ma vypadat:
"""
class TransformerInfo(BaseModel):
    quantity: float
    suppliers_currency: str
    price_of_offer: float
    rated_power_kVA: float
    dry_or_oil: str

filepath = '04 - Data Transformer/Examples/QT-20-Hitachi2_Rev0.pdf'
text = get_text_from_pdf(filepath)
print(f"Extracted text: {text}")

# Define prompts
system_prompt = "You are an expert finder of key information from text. Extract the requested information in the specified format."
user_prompt = f"Extract the following information from this text: {text}"



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
    # Initialize client
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