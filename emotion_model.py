"""
Emotion Detection Model for Mental Health Companion
This module provides functionality to detect emotions from different modalities:
- Text: Using a fine-tuned language model
- Image: Using facial emotion detection
- Audio: Using speech-to-text followed by emotion analysis
"""

import os
import sys

# Define model directory
MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')
os.makedirs(MODEL_DIR, exist_ok=True)

# Try to import torch with fallback
try:
    import torch
    # Check if CUDA is available, otherwise use CPU
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device set to use {device}")
except ImportError:
    print("Warning: PyTorch not available. Using dummy implementation.")
    device = "cpu"
    class DummyTorch:
        def __getattr__(self, name):
            return lambda *args, **kwargs: None
    torch = DummyTorch()

class EmotionDetector:
    def __init__(self):
        """Initialize the emotion detection models"""
        self.text_model = None
        self.text_tokenizer = None
        self.text_pipeline = None
        
        self.audio_pipeline = None
        self.image_pipeline = None
        
        # Load models
        try:
            self.load_models()
        except Exception as e:
            print(f"Error loading models: {e}")
    
    def load_models(self):
        """Load the pre-trained models"""
        try:
            # Try to import transformers with fallbacks
            try:
                from transformers import (
                    AutoModelForSequenceClassification, 
                    AutoTokenizer, 
                    pipeline
                )
                transformers_available = True
            except ImportError:
                print("Warning: Transformers library not available. Using dummy implementation.")
                transformers_available = False
                
                # Create dummy classes
                class DummyModel:
                    @staticmethod
                    def from_pretrained(*args, **kwargs):
                        return DummyModel()
                        
                class DummyTokenizer:
                    @staticmethod
                    def from_pretrained(*args, **kwargs):
                        return DummyTokenizer()
                        
                class DummyPipeline:
                    def __init__(self, *args, **kwargs):
                        pass
                        
                    def __call__(self, text):
                        if isinstance(text, str):
                            return [{"label": "neutral", "score": 0.5}]
                        return {"label": "neutral", "score": 0.5}
                
                # Create dummy functions
                def dummy_pipeline(*args, **kwargs):
                    return DummyPipeline()
                    
                # Assign dummy classes
                AutoModelForSequenceClassification = DummyModel
                AutoTokenizer = DummyTokenizer
                pipeline = dummy_pipeline
            
            if transformers_available:
                # Text emotion model
                # Check if model is available locally, otherwise use a default model
                text_model_path = os.path.join(MODEL_DIR, 'genz_emotion_model')
                if os.path.exists(text_model_path):
                    self.text_model = AutoModelForSequenceClassification.from_pretrained(text_model_path)
                    self.text_tokenizer = AutoTokenizer.from_pretrained(text_model_path)
                else:
                    # Use a default model from Hugging Face
                    self.text_model = AutoModelForSequenceClassification.from_pretrained("bhadresh-savani/distilbert-base-uncased-emotion")
                    self.text_tokenizer = AutoTokenizer.from_pretrained("bhadresh-savani/distilbert-base-uncased-emotion")
                
                self.text_pipeline = pipeline("text-classification", 
                                            model=self.text_model, 
                                            tokenizer=self.text_tokenizer,
                                            device=device)
                
                # Load other models only if required packages are available
                try:
                    # Audio emotion model (speech -> text -> emotion)
                    self.audio_pipeline = pipeline("automatic-speech-recognition", 
                                                model="facebook/wav2vec2-large-960h",
                                                device=device)
                except Exception as e:
                    print(f"Warning: Audio pipeline not available. {e}")
                    self.audio_pipeline = None
                
                try:
                    # Image model for facial emotion detection
                    self.image_pipeline = pipeline(
                        task="image-classification",
                        model="dima806/facial_emotions_image_detection",
                        device=device
                    )
                except Exception as e:
                    print(f"Warning: Image pipeline not available. {e}")
                    self.image_pipeline = None
                
                print("Emotion detection models loaded successfully")
            else:
                # Create dummy pipelines when transformers is not available
                self.text_pipeline = pipeline("text-classification")
                self.image_pipeline = pipeline("image-classification")
                self.audio_pipeline = None
                print("Using dummy emotion detection models")
                
        except Exception as e:
            print(f"Error loading models: {e}")
            # Fall back to simple dummy pipelines
            self.text_pipeline = lambda text: [{"label": "neutral", "score": 0.5}]
            self.image_pipeline = lambda image: [{"label": "neutral", "score": 0.5}]
            self.audio_pipeline = None
    
    def detect_from_text(self, text):
        """Detect emotion from text input"""
        if not self.text_pipeline:
            return {"label": "unknown", "score": 0.0}
        
        try:
            result = self.text_pipeline(text)[0]
            return result
        except Exception as e:
            print(f"Error in text emotion detection: {e}")
            return {"label": "unknown", "score": 0.0}
    
    def detect_from_audio(self, audio_path):
        """Detect emotion from audio input"""
        if not self.audio_pipeline or not self.text_pipeline:
            return {"label": "unknown", "score": 0.0}
        
        try:
            # Convert speech to text
            transcription = self.audio_pipeline(audio_path)
            text = transcription["text"]
            
            # Use text pipeline to get emotion
            emotion = self.text_pipeline(text)[0]
            return emotion
        except Exception as e:
            print(f"Error in audio emotion detection: {e}")
            return {"label": "unknown", "score": 0.0}
    
    def detect_from_image(self, image_path):
        """Detect emotion from image input"""
        if not self.image_pipeline:
            return {"label": "unknown", "score": 0.0}
        
        try:
            # Import here to handle missing dependencies gracefully
            from PIL import Image
            image = Image.open(image_path)
            result = self.image_pipeline(image)[0]
            return result
        except Exception as e:
            print(f"Error in image emotion detection: {e}")
            return {"label": "unknown", "score": 0.0}
    
    def fuse_emotions(self, text_emotion=None, audio_emotion=None, image_emotion=None):
        """Combine emotions from different modalities"""
        fused = {}

        # Text + Image
        if text_emotion and image_emotion and not audio_emotion:
            text_w, image_w = 0.7, 0.3
            if text_emotion['label'] == image_emotion['label']:
                fused['label'] = text_emotion['label']
                fused['score'] = text_emotion['score']*text_w + image_emotion['score']*image_w
            else:
                fused['label'] = text_emotion['label'] if text_emotion['score']*text_w >= image_emotion['score']*image_w else image_emotion['label']
                fused['score'] = max(text_emotion['score']*text_w, image_emotion['score']*image_w)

        # Audio + Image
        elif audio_emotion and image_emotion and not text_emotion:
            audio_w, image_w = 0.6, 0.4
            if audio_emotion['label'] == image_emotion['label']:
                fused['label'] = audio_emotion['label']
                fused['score'] = audio_emotion['score']*audio_w + image_emotion['score']*image_w
            else:
                fused['label'] = audio_emotion['label'] if audio_emotion['score']*audio_w >= image_emotion['score']*image_w else image_emotion['label']
                fused['score'] = max(audio_emotion['score']*audio_w, image_emotion['score']*image_w)

        # Text + Audio + Image
        elif text_emotion and audio_emotion and image_emotion:
            text_w, audio_w, image_w = 0.5, 0.3, 0.2
            scores = {
                text_emotion['label']: text_emotion['score']*text_w,
                audio_emotion['label']: audio_emotion['score']*audio_w,
                image_emotion['label']: image_emotion['score']*image_w
            }
            fused_label = max(scores, key=scores.get)
            fused['label'] = fused_label
            fused['score'] = scores[fused_label]

        # Only one input available
        else:
            if text_emotion:
                fused = text_emotion
            elif audio_emotion:
                fused = audio_emotion
            elif image_emotion:
                fused = image_emotion
            else:
                fused = {"label": "unknown", "score": 0.0}

        return fused
    
    def analyze_activity_image(self, image_path):
        """Analyze an activity image and detect emotional state"""
        try:
            return self.detect_from_image(image_path)
        except Exception as e:
            print(f"Error analyzing activity image: {e}")
            return {"label": "unknown", "score": 0.0}
    
    def detect_depression(self, text=None, audio_path=None, image_path=None):
        """
        Detect signs of depression from available inputs
        Returns a dictionary with depression_score and emotional_state
        """
        text_em = None
        audio_em = None
        image_em = None
        
        # Get emotions from available modalities
        if text:
            try:
                text_em = self.detect_from_text(text)
            except Exception as e:
                print(f"Error detecting text emotion: {e}")
        
        if audio_path and os.path.exists(audio_path):
            try:
                audio_em = self.detect_from_audio(audio_path)
            except Exception as e:
                print(f"Error detecting audio emotion: {e}")
            
        if image_path and os.path.exists(image_path):
            try:
                image_em = self.detect_from_image(image_path)
            except Exception as e:
                print(f"Error detecting image emotion: {e}")
        
        # Fuse emotions
        fused_emotion = self.fuse_emotions(text_em, audio_em, image_em)
        
        # Map emotions to depression indicators
        depression_indicators = {
            "sadness": 0.8,
            "fear": 0.6,
            "anger": 0.4,
            "disgust": 0.5,
            "neutral": 0.2,
            "joy": 0.0,
            "surprise": 0.1,
            # Add any other emotions your model might output
        }
        
        # Get depression score based on the emotion
        label = fused_emotion.get('label', 'unknown').lower()
        depression_score = depression_indicators.get(label, 0.3) * fused_emotion.get('score', 0.5)
        
        return {
            "emotional_state": fused_emotion,
            "depression_score": round(depression_score, 2),
            "depression_level": self._classify_depression_level(depression_score)
        }
    
    def _classify_depression_level(self, score):
        """Classify depression level based on score"""
        if score < 0.3:
            return "low"
        elif score < 0.6:
            return "moderate"
        else:
            return "high"

# Create a singleton instance
emotion_detector = EmotionDetector()
