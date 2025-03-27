import os
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Fetch credentials
speech_key = os.getenv("AZURE_SPEECH_KEY")
speech_region = os.getenv("AZURE_SPEECH_REGION")

# Validate credentials before initializing
if not speech_key or not speech_region:
    raise ValueError("Missing AZURE_SPEECH_KEY or AZURE_SPEECH_REGION in .env!")

# Initialize SpeechConfig
speech_config = speechsdk.SpeechConfig(
    subscription=speech_key,
    region=speech_region
)
speech_config.speech_synthesis_voice_name = "en-US-JennyNeural"

# Generate audio
audio_config = speechsdk.audio.AudioOutputConfig(filename="sample_data/test_audio.wav")
synthesizer = speechsdk.SpeechSynthesizer(
    speech_config=speech_config,
    audio_config=audio_config
)

result = synthesizer.speak_text_async("Hello MedFlow AI, this is a test audio generated from Azure!").get()
if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
    print(f"[✓] Neural audio saved to sample_data/test_audio.wav")
else:
    print(f"[✗] Synthesis failed:", result.error_details)