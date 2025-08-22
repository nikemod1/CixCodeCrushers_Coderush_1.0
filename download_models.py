"""
This script downloads pre-trained models used for emotion and depression detection.
Run this script before starting the application to ensure all models are available.
"""

import os
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline

# Create models directory if it doesn't exist
MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')
os.makedirs(MODEL_DIR, exist_ok=True)

def download_text_emotion_model():
    """Download and save text emotion model"""
    print("Downloading text emotion model...")
    
    # Create model directory
    model_dir = os.path.join(MODEL_DIR, 'genz_emotion_model')
    os.makedirs(model_dir, exist_ok=True)
    
    try:
        # If you have a custom fine-tuned model, you would load it from your drive
        # For this example, we'll use a pre-trained model from Hugging Face
        model = AutoModelForSequenceClassification.from_pretrained("bhadresh-savani/distilbert-base-uncased-emotion")
        tokenizer = AutoTokenizer.from_pretrained("bhadresh-savani/distilbert-base-uncased-emotion")
        
        # Save the model and tokenizer
        model.save_pretrained(model_dir)
        tokenizer.save_pretrained(model_dir)
        
        print(f"Text emotion model saved to {model_dir}")
    except Exception as e:
        print(f"Error downloading text emotion model: {e}")

def download_facial_emotion_model():
    """Download and cache facial emotion detection model"""
    print("Downloading facial emotion detection model...")
    
    try:
        # This will download and cache the model
        _ = pipeline(
            task="image-classification",
            model="dima806/facial_emotions_image_detection"
        )
        print("Facial emotion model downloaded and cached")
    except Exception as e:
        print(f"Error downloading facial emotion model: {e}")

def download_speech_recognition_model():
    """Download and cache speech recognition model"""
    print("Downloading speech recognition model...")
    
    try:
        # This will download and cache the model
        _ = pipeline("automatic-speech-recognition", 
                   model="facebook/wav2vec2-large-960h")
        print("Speech recognition model downloaded and cached")
    except Exception as e:
        print(f"Error downloading speech recognition model: {e}")

if __name__ == "__main__":
    print("Starting model downloads...")
    
    # Check if CUDA is available
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    
    # Download models
    download_text_emotion_model()
    download_facial_emotion_model()
    download_speech_recognition_model()
    
    print("All models downloaded successfully!")
