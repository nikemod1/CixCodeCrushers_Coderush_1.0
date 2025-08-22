"""
Test script for speech recognition functionality.
This script tests the audio transcription capabilities for the audio chat feature.
"""

import speech_recognition as sr
import os
import sys

def test_audio_transcription(audio_file=None):
    """Test the speech recognition on an audio file or microphone"""
    recognizer = sr.Recognizer()
    
    if audio_file and os.path.exists(audio_file):
        print(f"Testing transcription on file: {audio_file}")
        try:
            with sr.AudioFile(audio_file) as source:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data)
                print(f"Transcription: {text}")
                return True
        except Exception as e:
            print(f"Error transcribing file: {e}")
            return False
    else:
        print("No audio file provided or file doesn't exist. Testing microphone...")
        try:
            with sr.Microphone() as source:
                print("Speak now (or press Ctrl+C to exit)...")
                recognizer.adjust_for_ambient_noise(source)
                audio_data = recognizer.listen(source, timeout=5)
                print("Processing speech...")
                text = recognizer.recognize_google(audio_data)
                print(f"Transcription: {text}")
                return True
        except sr.WaitTimeoutError:
            print("No speech detected within timeout")
            return False
        except sr.UnknownValueError:
            print("Speech could not be understood")
            return False
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service: {e}")
            return False
        except Exception as e:
            print(f"Error during microphone transcription: {e}")
            return False

if __name__ == "__main__":
    # If an audio file path is provided as argument, use it
    audio_file = sys.argv[1] if len(sys.argv) > 1 else None
    success = test_audio_transcription(audio_file)
    
    if success:
        print("\nSpeech recognition test successful!")
    else:
        print("\nSpeech recognition test failed. Check errors above.")
        print("Make sure you have the following packages installed:")
        print("- SpeechRecognition==3.10.0")
        print("- PyAudio==0.2.13")
