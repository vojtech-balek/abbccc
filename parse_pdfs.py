import json
from parse_pdf import get_text_from_pdf, yield_pdfs_paths
from pydantic import BaseModel
from openai import AzureOpenAI
from typing import Optional
import pandas as pd


"""
Tady nadefinuj, jak to ma vypadat:
"""

class TransformerInfo(BaseModel):
    date: Optional[str] = None
    quantity: Optional[int] = None
    suppliers_currency: Optional[str] = None
    transformer_unit_price: Optional[int] = None
    dry_or_oil: Optional[str] = None
    rated_power_kVA: Optional[float] = None
    primary_winding: Optional[str] = None
    secondary_winding: Optional[str] = None
    no_load_losses: Optional[float] = None
    full_load_losses_75: Optional[float] = None
    full_load_losses_120: Optional[float] = None
    rated_volt_primary_side: Optional[float] = None


class NumberTransformers(BaseModel):
    types_of_transformers_offered: float

#filepath = '04 - Data Transformer/Examples/QT-20-Hitachi2_Rev0.pdf'

#filepath = '04 - Data Transformer/Examples/2022 08 03 SGB Ang SGB4 R00.pdf'

# filepath = '04 - Data Transformer/Examples/QT-22-Hitachi9_Rev0.pdf'

# filepath = '04 - Data Transformer/Examples/QUOTATION Sonmez2.pdf'

# filepath = '04 - Data Transformer/Examples/RDOSea3A.pdf'



# Define prompts
system = "You are an expert finder of key information from text."

def get_extract_prompt(transformer_number:int, text):
    user_extract = (f"Extract the requested information from the offer."
                    f"There could be offered multiple different transformers. Extract information about transformer "
                    f"number {transformer_number}. Make sure to follow the restrictions-convert to correct units."
                    f"Additional restrictions:"
                    f""" 
                        quantity: explains how many transformer units number {transformer_number} are being sold."
                        dry_or_oil (choose "Dry", "Oil"),
                        suppliers_currency: (EUR, CZK..),
                        transformer_unit_price: price of the specified transformer,
                        rated_power_kVA (units kVA),
                        primary_winding (choose "Aluminium", "Copper"),
                        secondary_winding (choose "Aluminium", "Copper"),
                        no_load_loss (units: W),
                        full_load_loss_75 (units: W): Full Load Loss at 75°C,
                        full_load_loss_120 (units: W): Full Load Loss at 120°C,
                        rated_volt_primary_side (units: kV)
                    """
                    f"\\n Offer text: \\n {text}")

    return user_extract


def get_user_count_prompt(text):
    return (f"What is the number of different types of transformer units offered for sale in the report?"
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
    df_list = []

    # Example usage
    for file_path, filename in yield_pdfs_paths("04 - Data Transformer/Data"):
        if filename.endswith(".pdf"):
            text = get_text_from_pdf(file_path)
        else:
            text = get_text_from_docx(file_path)


        print(f"PDF: {file_path}")
        print(f"Extracted text: {text[:100]}")

        result = main(system, get_user_count_prompt(text), structure=NumberTransformers)
        number_of_transformers = int(result.get("types_of_transformers_offered", 0))

        for i in range(1, number_of_transformers+1):
            results_dict = main(system, get_extract_prompt(i, text=text), structure=TransformerInfo)
            df_list.append(pd.DataFrame([results_dict]))

    # Concatenate all DataFrames into one DataFrame
    df = pd.concat(df_list, ignore_index=True)

    df.to_csv("transformer_data2.csv", index=False, encoding="utf-8")
    print("Data saved to transformer_data.csv")