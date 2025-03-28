import os
import azure.cognitiveservices.speech as speechsdk

def transcribe_audio(audio_bytes: bytes) -> str:
    speech_config = speechsdk.SpeechConfig(
        subscription=os.environ["AZURE_SPEECH_KEY"],
        region=os.environ["AZURE_SPEECH_REGION"]
    )
    speech_config.speech_recognition_language = "en-US"

    audio_stream = speechsdk.audio.PushAudioInputStream()
    audio_config = speechsdk.audio.AudioConfig(stream=audio_stream)

    audio_stream.write(audio_bytes)
    audio_stream.close()

    recognizer = speechsdk.SpeechRecognizer(speech_config, audio_config)
    result = recognizer.recognize_once()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return result.text
    elif result.reason == speechsdk.ResultReason.NoMatch:
        raise ValueError("No speech detected.")
    else:
        raise RuntimeError("Speech recognition failed.")
