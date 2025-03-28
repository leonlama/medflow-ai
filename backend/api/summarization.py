import os
import json
import logging
import openai
from openai import AzureOpenAI
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

from backend.utils.validation import validate_medical_data, remove_empty_elements

from backend.shared.summarization_utils import summarize_text

system_prompt = """Extract medical info into strict JSON with:
- Abbreviations (HTN, DM)
- ISO8601 dates
- No null/empty fields
- Use structure:
{ "patient_id": "...", "date": "...", "patient_info": {...}, "treatment": {...} }

If medication is mentioned, it must appear under treatment.medications.
Each entry must include: name, dose, frequency, duration. If unsure, use "unknown" as value.
Omit entire object if no meds prescribed.
Always extract prescribed medications accurately into 'treatment.medications'
"""

@retry(
    retry=retry_if_exception_type((openai.APIError, openai.APITimeoutError, openai.RateLimitError)),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    stop=stop_after_attempt(5)
)
def summarize_report(transcript: str) -> dict:
    return summarize_text(transcript)
