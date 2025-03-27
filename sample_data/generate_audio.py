import pyttsx3
import os

# Ensure output directory exists
os.makedirs("sample_data", exist_ok=True)

engine = pyttsx3.init()
text = "Hello MedFlow AI. This is a voice test."
output = "sample_data/test_audio.wav"
engine.save_to_file(text, output)
engine.runAndWait()

print(f"[x] Generated audio at {output}")
