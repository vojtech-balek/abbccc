from pydantic import BaseModel
from openai import AzureOpenAI

import os
import json


# Configuration
with open("credentials.json", "r") as f:
    credentials = json.load(f)


client = AzureOpenAI(
  azure_endpoint = credentials["endpoint"],
  api_key=credentials["api_key"],
  api_version="2024-08-01-preview"
)


class CalendarEvent(BaseModel):
    name: str
    date: str
    participants: list[str]


    completion = client.beta.chat.completions.parse(
        model="MODEL_DEPLOYMENT_NAME", # replace with the model deployment name of your gpt-4o 2024-08-06 deployment
        messages=[
            {"role": "system", "content": "Extract the event information."},
            {"role": "user", "content": "Alice and Bob are going to a science fair on Friday."},
        ],
        response_format=CalendarEvent,
    )

event = completion.choices[0].message.parsed

print(event)
print(completion.model_dump_json(indent=2))