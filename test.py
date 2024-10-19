import base64

with open("04 - Data Transformer/Data/Virginia Transformer CORP/Budgetory 15.45 MVA_ABB.docx", 'rb') as file:
    enc = base64.b64encode(file.read()).decode('utf-8')

with open("encoded.txt", "w") as encoded_file:
    encoded_file.write(enc)