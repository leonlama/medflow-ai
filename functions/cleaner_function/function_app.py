import sys
import os
import sys
from pathlib import Path

backend_path = Path(__file__).resolve().parents[2] / "backend"
import logging

if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))
    logging.info(f"[DEBUG] Inserted backend path: {backend_path}")

logging.info(f"[DEBUG] PYTHONPATH = {os.environ.get('PYTHONPATH')}")

from pathlib import Path
import logging
import traceback
import json
import io
import tempfile
from datetime import datetime

import azure.functions as func
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
import azure.cognitiveservices.speech as speechsdk
from openai import AzureOpenAI
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

from backend.api.transcription import transcribe_audio
from backend.api.summarization import summarize_text
from backend.shared.form_cleaner import clean_form_data
from backend.utils.validation import (
    validate_medical_data,
    remove_empty_elements,
    MedicalJSONEncoder
)

# Define schema for medical data validation
MEDICAL_SCHEMA = {
    "type": "object",
    "required": ["patient_id", "date", "treatment"],
    "properties": {
        "patient_id": {"type": "string", "pattern": "^[A-Z0-9-]+$"},
        "date": {"type": "string", "format": "date"},
        "treatment": {
            "type": "object", 
            "required": ["medications"],
            "properties": {
                "medications": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "required": ["name", "dose", "frequency", "duration"],
                        "properties": {
                            "name": {"type": "string"},
                            "dose": {"type": "string"},
                            "frequency": {"type": "string"},
                            "duration": {"type": "string"}
                        }
                    }
                }
            }
        }
    }
}

def validate_medical_data(data: dict) -> tuple:
    try:
        jsonschema.validate(data, MEDICAL_SCHEMA)
        return True, None
    except jsonschema.ValidationError as e:
        return False, f"Validation failed: {e.message} at {'.'.join(str(p) for p in e.path)}"
    except Exception as e:
        return False, f"Unexpected validation error: {str(e)}"

def remove_empty_elements(d):
    """Recursively remove empty values"""
    if not isinstance(d, dict):
        return d
    return {k: remove_empty_elements(v) 
            for k, v in d.items() 
            if v not in [None, "", [], {}]}

class MedicalJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.function_name(name="CleanReport")
@app.route(route="clean", methods=["POST"])
def clean_data_func(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("[DEBUG] CLEAN endpoint hit")
    logging.info(f"[DEBUG] Method: {req.method}")
    logging.info(f"[DEBUG] Headers: {req.headers}")
    logging.info(f"[DEBUG] Files: {req.files}")
    logging.info(f"[DEBUG] Params: {req.params}")
    try:
        file = req.files.get('pdf')
        if not file:
            return func.HttpResponse("No file uploaded", status_code=400)

        # Analyze PDF in memory
        document_analysis_client = DocumentAnalysisClient(
            endpoint=os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"],
            credential=AzureKeyCredential(os.environ["AZURE_FORM_RECOGNIZER_KEY"])
        )

        poller = document_analysis_client.begin_analyze_document(
            "prebuilt-layout",
            file.stream.read()
        )
        result = poller.result()

        structured_data = {
            "tables": [
                {
                    "row_count": table.row_count,
                    "column_count": table.column_count,
                    "cells": [cell.content for cell in table.cells]
                } for table in result.tables
            ],
            "content": result.content
        }

        return func.HttpResponse(json.dumps(structured_data), mimetype="application/json")

    except Exception as e:
        logging.error(f"CleanData Error: {str(e)}\n{traceback.format_exc()}")
        return func.HttpResponse(f"ERROR: {str(e)}", status_code=500)

@app.function_name(name="TranscribeAudio") 
@app.route(route="transcribe", methods=["POST"])
def transcribe_audio(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Get raw audio bytes from request body
        audio_bytes = req.get_body() #check if allows .mp3 aswell. 
        
        if not audio_bytes:
            return func.HttpResponse("No audio data received", status_code=400)

        # Configure Speech SDK
        speech_config = speechsdk.SpeechConfig(
            subscription=os.environ["AZURE_SPEECH_KEY"],
            region=os.environ["AZURE_SPEECH_REGION"]
        )
        speech_config.speech_recognition_language = "en-US"

        # Process audio bytes directly
        audio_stream = speechsdk.audio.PushAudioInputStream()
        audio_config = speechsdk.audio.AudioConfig(stream=audio_stream)
        
        # Write audio data to stream
        audio_stream.write(audio_bytes)
        audio_stream.close()

        # Recognize speech
        recognizer = speechsdk.SpeechRecognizer(speech_config, audio_config)
        result = recognizer.recognize_once()

        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            return func.HttpResponse(
                json.dumps({"transcript": result.text}),
                mimetype="application/json"
            )
        elif result.reason == speechsdk.ResultReason.NoMatch:
            return func.HttpResponse("No speech detected", status_code=400)
        else:
            return func.HttpResponse("Transcription failed", status_code=500)

    except Exception as e:
        logging.error(f"TranscribeAudio Error: {str(e)}")
        return func.HttpResponse(f"ERROR: {str(e)}", status_code=500)

@app.function_name(name="Summarize")
@app.route(route="summarize", methods=["POST"])
def summarize_report(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # decode JSON data
        body_bytes = req.get_body() #check if /summarize expects json. change to "str" if better token usage.
        try:
            decoded_body = body_bytes.decode('utf-8')
        except UnicodeDecodeError:
            decoded_body = body_bytes.decode('latin-1')
            
        try:
            transcript = json.loads(decoded_body).get('text')
        except json.JSONDecodeError as e:
            logging.error(f"JSON parsing failed: {str(e)}")
            return func.HttpResponse("Invalid JSON format", status_code=400)

        if not transcript:
            return func.HttpResponse("No text provided", status_code=400)

        # Get accurate token count using tiktoken
        enc = tiktoken.encoding_for_model("gpt-4")
        token_count = len(enc.encode(transcript))
        logging.info(f"[TOKEN COUNT] Input text has {token_count} tokens")

        # Cap text if needed
        if token_count > 800:
            logging.warning(f"Input too long ({token_count} tokens). Truncating...")
            truncated_tokens = enc.encode(transcript)[:800]
            transcript = enc.decode(truncated_tokens)
            logging.info(f"Truncated to {len(enc.encode(transcript))} tokens")

        # Azure OpenAI Client initialize
        client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_KEY"),
            api_version="2024-02-01",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )

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
            retry=retry_if_exception_type((
                openai.APIError,        # Handles 500-range errors
                openai.APITimeoutError,  # Handles timeout errors
                openai.RateLimitError    # Handles 429 errors
            )),
            wait=wait_exponential(multiplier=1, min=2, max=30),
            stop=stop_after_attempt(5)
        )
        def summarize_with_retry(client, messages):
            try:
                return client.chat.completions.create(
                    model="gpt-4o",
                    messages=messages,
                    response_format={"type": "json_object"},
                    max_tokens=800,
                    temperature=0.3  # More deterministic output
                )
            except openai.APIStatusError as e:
                logging.error(f"OpenAI API error: {e.status_code} {e.message}")
                raise

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": transcript}
        ]
        
        logging.info(f"[GPT REQUEST] Transcript (first 100 chars): {transcript[:100]}")
        response = summarize_with_retry(client, messages)
        
        summary = json.loads(response.choices[0].message.content)
        
        # Log raw GPT output
        logging.info("[GPT RAW OUTPUT] " + json.dumps(summary, indent=2))

        # Add fallback empty medications array if missing
        if "treatment" in summary and "medications" not in summary["treatment"]:
            logging.warning("Adding fallback medication field to avoid schema error")
            summary["treatment"]["medications"] = []
        
        # Enhanced validation
        is_valid, validation_msg = validate_medical_data(summary)
        if not is_valid:
            logging.warning(f"[VALIDATION] Failed: {validation_msg}")
            return func.HttpResponse(
                json.dumps({
                    "error": "Invalid structure. Please ensure medication details are included.",
                    "details": validation_msg,
                    "raw_output": summary
                }, cls=MedicalJSONEncoder),
                mimetype="application/json",
                status_code=422
            )
            
        # Clean null values
        cleaned_summary = remove_empty_elements(summary)
        
        return func.HttpResponse(
            json.dumps(cleaned_summary, cls=MedicalJSONEncoder),
            mimetype="application/json"
        )

    except ValueError as e:
        logging.error(f"Validation error: {str(e)}")
        return func.HttpResponse(f"Validation error: {str(e)}", status_code=422)
        
    except openai.APIStatusError as e:
        logging.error(f"OpenAI API error: {e.status_code} {e.message}")
        return func.HttpResponse(f"AI service error: {e.message}", status_code=503)
        
    except Exception as e:
        error_msg = f"Full error: {str(e)}\nTranscript: {transcript[:200] if transcript else 'None'}"
        logging.error(error_msg)
        return func.HttpResponse(f"ERROR: {str(e)}", status_code=500)