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
audio_config = speechsdk.audio.AudioOutputConfig(filename="test_audio.wav")
synthesizer = speechsdk.SpeechSynthesizer(
    speech_config=speech_config,
    audio_config=audio_config
)
result = synthesizer.speak_text_async("Patient ID 4321, date 2024-03-28. "
                                    "55-year-old male with hypertension and high cholesterol presented with chest tightness "
                                    "and shortness of breath. Pain level 5/10. Vitals stable with normal EKG. "
                                    "Clear lungs on exam. Likely angina versus anxiety. "
                                    "Starting aspirin 81mg daily, continuing blood pressure meds. "
                                    "Will do stress test in 48 hours and see cardiology next week.").get()
if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
    print(f"[✓] Neural audio saved to sample_data/test_audio.wav")
else:
    print(f"[✗] Synthesis failed:", result.error_details)