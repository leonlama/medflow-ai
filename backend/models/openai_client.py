import os
import logging
import json
from openai import AzureOpenAI, APIStatusError, APIError, RateLimitError, APITimeoutError
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type


client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version="2024-02-01",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)


@retry(
    retry=retry_if_exception_type((APIError, RateLimitError, APITimeoutError)),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    stop=stop_after_attempt(5)
)
def summarize_medical_transcript(transcript: str, system_prompt: str, max_tokens: int = 300) -> dict:
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": transcript}
    ]
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            response_format={"type": "json_object"},
            max_tokens=max_tokens,
            temperature=0.3
        )
        return json.loads(response.choices[0].message.content)
    except APIStatusError as e:
        logging.error(f"OpenAI API error: {e.status_code} {e.message}")
        raise
