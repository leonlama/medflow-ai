import os, sys, logging, json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import azure.functions as func
import azure.cognitiveservices.speech as speechsdk
from src.cleaner.cleaner import clean_data

app = func.FunctionApp()

@app.function_name(name="CleanData")
@app.route(route="CleanData", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def clean_data_func(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("CleanData HTTP trigger received")
    try:
        body = req.get_json()
        df = clean_data(body.get("input_path"))
        return func.HttpResponse(df.to_json(orient="records"), mimetype="application/json")
    except Exception as e:
        logging.error(f"Cleaning failed: {e}")
        return func.HttpResponse(str(e), status_code=500)

@app.function_name(name="TranscribeAudio") 
@app.route(route="TranscribeAudio", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def transcribe_audio(req: func.HttpRequest) -> func.HttpResponse:
    body = req.get_json()
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    audio_path = os.path.normpath(os.path.join(base_dir, body.get("audio_path")))
    speech_config = speechsdk.SpeechConfig(subscription=os.getenv("AZURE_SPEECH_KEY"), region=os.getenv("AZURE_SPEECH_REGION"))
    recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=speechsdk.AudioConfig(filename=audio_path))
    result = recognizer.recognize_once()
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return func.HttpResponse(json.dumps({"transcript": result.text}), mimetype="application/json")
    return func.HttpResponse("Transcription failed", status_code=500)
