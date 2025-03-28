import os
import json
import logging
import openai
from openai import AzureOpenAI
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

from backend.utils.validation import validate_medical_data, remove_empty_elements

system_prompt = """Extract medical details into JSON with STRICT structure:
TOKEN PRESERVATION RULES:
1. Use medical abbreviations (HTN=hypertension, DM=diabetes)
2. Omit null/empty fields
3. Use ISO8601 dates (YYYY-MM-DD)
{
  "patient_id": "string",
  "date": "YYYY-MM-DD",
  "patient_info": {
    "age": integer,
    "gender": "male/female/other",
    "medical_history": ["hypertension", "diabetes"]
  },
  "current_condition": {
    "symptoms": ["nausea", "fever"],
    "pain": {
      "level": 0-10,
      "type": "string",
      "location": "string"
    },
    "vitals": {
      "temperature_c": float,
      "heart_rate": integer
    }
  },
  "treatment": {
    "medications": [
      {
        "name": "Ciprofloxacin",
        "dose": "500mg",
        "frequency": "q12h",
        "duration": "7d"
      }
    ],
    "recommendations": ["ultrasound", "follow-up"]
  }
}"""

@retry(
    retry=retry_if_exception_type((openai.APIError, openai.APITimeoutError, openai.RateLimitError)),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    stop=stop_after_attempt(5)
)
def summarize_text(transcript: str) -> dict:
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        api_version="2024-02-01",
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": transcript}
    ]

    logging.info(f"[TOKEN COUNT] Input text has {len(transcript.split())} tokens")
    logging.info(f"[GPT REQUEST] Transcript (first 100 chars): {transcript[:100]}")

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        response_format={"type": "json_object"},
        max_tokens=300,
        temperature=0.3
    )

    try:
        summary = json.loads(response.choices[0].message.content)
    except Exception as e:
        raise ValueError(f"Failed to parse JSON output: {str(e)}")

    is_valid, validation_msg = validate_medical_data(summary)
    if not is_valid:
        raise ValueError(validation_msg)

    return remove_empty_elements(summary)
