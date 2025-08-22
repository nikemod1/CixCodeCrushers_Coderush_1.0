# Mental Health Companion

A Flask-based web application designed to help users monitor and improve their mental health through activity tracking and emotion analysis.

## Features

- **User Authentication System**
  - Registration and login functionality
  - Secure password hashing with Flask-Bcrypt
  - User session management

- **Activity Monitoring**
  - Captures photos using the user's webcam at regular intervals
  - Stores activity images for later review
  - Tracks user activity over time

- **Emotion Analysis**
  - Analyzes images for facial emotions
  - Processes text input to detect emotional states
  - Combines multiple data sources for more accurate assessment

- **Depression Detection**
  - Uses a multi-modal approach to detect signs of depression
  - Analyzes facial expressions, text content, and user behavior
  - Provides depression risk assessment and recommendations

- **AI-Powered Chat Support**
  - Integration with Ollama for intelligent, context-aware conversations
  - Real-time emotion analysis during chat sessions
  - Background monitoring for continuous emotional assessment
  - Personalized wellness tips based on detected emotional state

- **Data Visualization**
  - Charts showing emotional state and depression trends over time
  - Visual indicators of current mental health status
  - User-friendly interface for monitoring progress

## Technical Stack

- **Backend**: Flask (Python)
- **Database**: MongoDB
- **Authentication**: Flask-Bcrypt
- **AI/ML**: Transformers, PyTorch
- **Frontend**: HTML, Tailwind CSS, JavaScript

## Installation

1. Clone the repository
2. Install required packages:
   ```
   pip install -r requirements.txt
   ```
3. Install Ollama (for AI chat capabilities):
   - Download from [ollama.com](https://ollama.com/download)
   - After installation, run:
     ```
     python setup_ollama.py
     ```
   - This will help you select and download a suitable language model for the chat feature
   
4. Make sure you have a MongoDB instance running
5. Run the application:
   ```
   python app.py
   ```

## Usage

1. Register a new account
2. Log in to access your dashboard
3. Use the activity monitoring feature to track your daily activities
4. Complete daily check-ins to record your emotional state
5. View your mental health trends and depression risk assessment

## AI Models

The application uses several pre-trained models:
- Text emotion detection (distilbert-base-uncased-emotion)
- Facial emotion detection (facial_emotions_image_detection)
- Speech-to-text conversion (wav2vec2-large-960h)
- Conversational AI (llama3, llama3.2, phi3, or other models via Ollama)

## Ollama Integration

The chat functionality is powered by Ollama, which provides local large language model inference:

- **Recommended Models**: llama3, llama3.2, phi3, or deepseek-v2
- **Model Selection**: Run `python setup_ollama.py` to select and download your preferred model
- **Fallback System**: The application includes a robust fallback system that provides rule-based responses if Ollama is not available
- **Privacy**: All chat interactions are processed locally on your machine, ensuring privacy

To install Ollama and set up the models:
1. Download Ollama from [ollama.com](https://ollama.com/download)
2. Run `python setup_ollama.py` to download and configure your preferred model
3. Restart the application

## Privacy and Data Security

- All user data is stored securely in MongoDB
- Passwords are hashed using bcrypt
- Activity images are stored locally on the server
- Emotion analysis is performed locally

## Future Enhancements

- Integration with wearable devices for physiological data
- Advanced chatbot for mental health support
- Personalized meditation and mindfulness exercises
- Integration with professional mental health services
