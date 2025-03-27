import os, sys, logging, traceback, json, io, tempfile
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import azure.functions as func
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
import azure.cognitiveservices.speech as speechsdk

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.function_name(name="CleanData")
@app.route(route="clean", methods=["POST"])
def clean_data_func(req: func.HttpRequest) -> func.HttpResponse:
    try:
        file = req.files.get('file')
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
    temp_audio_path = None
    try:
        file = req.files.get("file")
        if not file:
            return func.HttpResponse("No audio file uploaded", status_code=400)

        # Save and close temp file fully
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav", mode="wb") as tmp:
            tmp.write(file.read())
            temp_audio_path = tmp.name

        # Delay ensures Windows releases file lock
        import time; time.sleep(0.5)

        speech_config = speechsdk.SpeechConfig(
            subscription=os.environ["AZURE_SPEECH_KEY"],
            region=os.environ["AZURE_SPEECH_REGION"]
        )
        speech_config.speech_recognition_language = "en-US"

        audio_config = speechsdk.audio.AudioConfig(filename=temp_audio_path)
        recognizer = speechsdk.SpeechRecognizer(speech_config, audio_config)

        result = recognizer.recognize_once_async().get()

        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            return func.HttpResponse(
                json.dumps({"transcript": result.text}),
                mimetype="application/json"
            )
        elif result.reason == speechsdk.ResultReason.NoMatch:
            return func.HttpResponse("No speech could be recognized", status_code=400)
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            return func.HttpResponse(
                f"Speech Recognition canceled: {cancellation_details.reason} {cancellation_details.error_details}",
                status_code=500
            )

    except Exception as e:
        logging.error(f"TranscribeAudio Error: {str(e)}\n{traceback.format_exc()}")
        return func.HttpResponse(f"ERROR: {str(e)}", status_code=500)

    finally:
        # Remove only after everything is done
        if temp_audio_path and os.path.exists(temp_audio_path):
            for attempt in range(3):
                try:
                    os.remove(temp_audio_path)
                    break  # success
                except PermissionError as e:
                    logging.warning(f"Attempt {attempt+1}: Could not delete temp file yet, retrying...")
                    time.sleep(0.5)
                except Exception as e:
                    logging.warning(f"Unexpected error while deleting temp file: {e}")
                    break