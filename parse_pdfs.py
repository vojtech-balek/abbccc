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
    # Commercial part
    quantity: Optional[int] = None
    suppliers_currency: Optional[str] = None
    transformer_unit_price: Optional[int] = None
    discount: Optional[float] = None
    cost_more: Optional[int] = None
    incoterm: Optional[str] = None
    incoterm_place: Optional[str] = None
    packing: Optional[str] = None
    packing_costs: Optional[int] = None
    transportation_extra_costs: Optional[int] = None
    lead_time: Optional[int] = None
    ### Transformer General and Enviromental info
    dry_or_oil: Optional[str] = None
    application: Optional[str] = None
    standard: Optional[str] = None
    application_field: Optional[str] = None
    design_temperature: Optional[str] = None
    altitude: Optional[str] = None
    zone_of_installation: Optional[str] = None
    protection_class: Optional[str] = None
    corrosion_class: Optional[str] = None
    color_RAL: Optional[str] = None
    total_weight: Optional[int] = None
    dim_length: Optional[int] = None
    dim_height: Optional[int] = None
    #Technical data
    rated_power_kVA: Optional[int] = None
    derated_power_kVA: Optional[int] = None
    secondary_rated_power_kVA: Optional[int] = None
    reactor_power_kVAr: Optional[int] = None
    cooling_system: Optional[str] = None
    primary_winding_material: Optional[str] = None
    secondary_winding_material: Optional[str] = None
    num_of_windings: Optional[int] = None
    frequency: Optional[int] = None
    rated_volt_primary_side: Optional[float] = None
    rated_voltage_secondary_side: Optional[float] = None
    uk_impedance: Optional[str] = None
    vector_group: Optional[str] = None
    no_load_loss: Optional[int] = None
    full_load_loss_75: Optional[float] = None
    full_load_loss_120: Optional[float] = None
    noise_level: Optional[str] = None
    tap_changer: Optional[str] = None
    tap_range: Optional[str] = None
    design_transformer_type: Optional[str] = None
    k_factor: Optional[float] = None







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
                        suppliers_currency: (EUR, CZK..),
                        transformer_unit_price: price of the specified transformer,
                        discount: mention of discounts applied to the offer from the manufacturer,
                        cost_more: list of costs of other products besides the transformer (e.g. "1200 + 2000 + 3000"),
                        incoterm: abbreviation of the incoterm used in the offer (e.g. FCA, EXW), 
                        incoterm_place: geographical place of the incotermm,
                        packing: any specification of the packaging,
                        packing_costs: 0 if included, price otherwise,
                        transportation_extra_costs: 0 if included, price otherwise,
                        lead_time: weeks,
                        
                        dry_or_oil: choose ("Dry", "Oil"),
                        application: choose ("Distribution", "Rectifier"),
                        standard: choose ("IEC", "IEEE", other standards),
                        application_field: choose ("Indoor", "Outdoor"),
                        design_temperature: maximal temperature (e.g. "max 40°C"), 
                        altitude: maximal altitude above sea level (e.g. "max 1000 m. a. s. l."),
                        zone_of_installation: choose ("Seismic", "Safe", "Ex"),
                        protection_class: IP rating (e.g. IP55), 
                        corrosion_class: choose corrosion class (e.g. C2),
                        color_RAL: RAL code of coloring of the transformer, 
                        total_weight: total weight in Kg,
                        dim_length: length of the transformer in mm, 
                        dim_height: height of the transformer in mm, 
                        rated_power_kVA: rated power in  kVA,
                        derated_power_kVA: derated power in kVA,
                        secondary_rated_power_kVA: secondary rated power in kVA, 
                        reactor_power_kVAr: reactor power in kVAr, 
                        cooling_system: specification of the cooling system ("AN", "AF", "ONAN", ...),
                        primary_winding: material of primary winding, (choose "Aluminium", "Copper"),
                        secondary_winding: material of primary winding, (choose "Aluminium", "Copper"),
                        num_of_windings: number of windings, 
                        frequency: transformer frequency in Hz,
                        rated_volt_primary_side: rated voltage for the primary side in kV, 
                        rated_voltage_secondary_side: rated voltage for the secondary side in kV, 
                        uk_impedance: Uk (Impedance) #1 in percent,
                        vector_group: select vector group,
                        no_load_loss: loss at 0 load in W,
                        full_load_loss_75: Full Load Loss at 75°C in W,
                        full_load_loss_120: Full Load Loss at 120°C in W,
                        noise_level: level of noise in dB (t.b.c. if not mentioned), 
                        tap_changer: choose ("OCTC", "NLTC", "OTHER", "NONE"),
                        tap_range: Tap Range e.g. +/- 2.5%,
                        design_transformer_type: type of transformer design (e.g. RESIBLOC),
                        k_factor: k-factor
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
    for pdf_path in yield_pdfs_paths("04 - Data Transformer/Data"):

        text = get_text_from_pdf(pdf_path)
        print(f"PDF: {pdf_path}")
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