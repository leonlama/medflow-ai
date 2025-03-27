import os, sys, logging, traceback, json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import azure.functions as func
import azure.cognitiveservices.speech as speechsdk
from src.cleaner.cleaner import clean_data

from src.parser.extract import extract_tables, extract_csv 

app = func.FunctionApp()

@app.function_name(name="CleanData")
@app.route(route="CleanData", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def clean_data_func(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = req.get_json()
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        input_path = os.path.normpath(os.path.join(base, body.get("input_path")))

        # Determine intermediate JSON path
        parsed_dir = os.path.join(base, "parsed_data")
        os.makedirs(parsed_dir, exist_ok=True)
        json_path = os.path.join(parsed_dir, os.path.basename(input_path).rsplit(".", 1)[0] + ".json")

        if input_path.lower().endswith(".pdf"):
            extract_tables(input_path, json_path)
        elif input_path.lower().endswith(".csv"):
            extract_csv(input_path, json_path)
        else:
            return func.HttpResponse("Unsupported file type", status_code=400)

        df = clean_data(json_path)
        return func.HttpResponse(df.to_json(orient="records"), mimetype="application/json")

    except Exception as e:
        tb = traceback.format_exc()
        logging.error(tb)
        return func.HttpResponse(f"ERROR: {e}\n\n{tb}", status_code=500)

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
