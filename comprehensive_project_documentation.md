# Mental Health Companion: Comprehensive Project Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Problem Statement](#problem-statement)
3. [Solution Overview](#solution-overview)
4. [System Architecture](#system-architecture)
5. [Tech Stack](#tech-stack)
6. [Core Components](#core-components)
7. [Implementation Details](#implementation-details)
8. [Features](#features)
   - [User Authentication System](#user-authentication-system)
   - [Emotion Analysis](#emotion-analysis)
   - [Depression Detection](#depression-detection)
   - [Chat Interface](#chat-interface)
   - [Audio Chat](#audio-chat)
   - [Depression Report Generation](#depression-report-generation)
9. [Database Schema](#database-schema)
10. [Ollama Integration](#ollama-integration)
11. [Installation and Setup](#installation-and-setup)
12. [Usage Guide](#usage-guide)
13. [Privacy and Security](#privacy-and-security)
14. [Future Enhancements](#future-enhancements)
15. [Ethical Considerations](#ethical-considerations)

## Project Overview

Mental Health Companion is an AI-powered web application that provides users with continuous emotional support and mental health monitoring. Named "Chi Chi," the assistant helps users track their emotional states, detect early signs of depression, and access personalized support. The system uses multi-modal analysis, processing text, images, and audio to provide a comprehensive understanding of the user's emotional state.

## Problem Statement

Mental health concerns are on the rise globally, with limited access to professional support services. Many individuals struggle with:

- **Limited Access**: Professional mental health services are often expensive, have long wait times, or are geographically inaccessible.
- **Continuous Monitoring**: Traditional mental health care lacks continuous monitoring between appointments.
- **Early Detection**: Depression and other mental health issues often go undetected until they become severe.
- **Privacy Concerns**: Many individuals are reluctant to seek help due to stigma and privacy concerns.
- **Self-Awareness**: People often have difficulty recognizing their own emotional patterns and triggers.

The Mental Health Companion aims to address these challenges by providing an accessible, private, and continuous support system powered by AI.

## Solution Overview

The Mental Health Companion is an AI-powered web application that provides continuous emotional support and monitoring through:

1. **Multi-Modal Emotion Analysis**: Detecting emotions from text, images, and audio inputs.
2. **Depression Risk Assessment**: Analyzing emotional patterns to estimate depression risk levels.
3. **Personalized Support**: Offering tailored coping strategies based on individual emotional states.
4. **Continuous Monitoring**: Tracking emotional trends over time to identify patterns.
5. **Private and Accessible**: Available 24/7 with secure user data protection.

## System Architecture

The system follows a modular architecture with several interconnected components:

### Core Components

1. **User Authentication System**
   - Registration with secure password hashing
   - Login/logout functionality
   - Session management

2. **Emotion Detection Module**
   - Text Analysis: Fine-tuned language model (DistilBERT) for emotion classification
   - Image Analysis: Facial emotion detection model
   - Audio Analysis: Speech-to-text conversion followed by emotion analysis
   - Multi-modal fusion for combined analysis

3. **Depression Risk Assessment**
   - Analysis of emotional patterns over time
   - Scoring algorithm based on emotional states
   - Risk level classification (Low, Moderate, High)

4. **Data Storage**
   - User profiles and authentication data
   - Emotional analysis results
   - Activity images and associated metadata
   - Depression scores and trends

5. **User Interface**
   - Responsive dashboard with emotional state visualization
   - Activity tracking with camera integration
   - Trend charts for depression risk monitoring
   - Mood journaling interface

### Data Flow

1. **User Input**
   - Text entries (journal entries, mood descriptions)
   - Images (activity photos, selfies)
   - Audio recordings for speech-to-text conversion

2. **Processing Pipeline**
   - Input validation and preprocessing
   - Model inference for emotion detection
   - Depression risk calculation
   - Result aggregation

3. **Data Storage**
   - MongoDB document storage with structured schema
   - Secure file storage for images
   - Timestamped entries for trend analysis

4. **User Feedback**
   - Visual representation of emotional states
   - Depression risk indicators
   - Historical trend charts
   - Personalized coping strategies

## Tech Stack

### Backend
- **Flask 3.0.0**: Python web framework for building the application.
- **MongoDB 4.6.1**: NoSQL database for storing user data and emotional analysis results.
- **Flask-Bcrypt**: For secure password hashing.
- **Python 3.13**: Core programming language.

### AI Components
- **Transformers**: Hugging Face library for NLP models.
- **PyTorch & TorchAudio**: Deep learning frameworks for model inference.
- **TensorFlow/Keras**: For depression risk analysis models.
- **OpenCV**: For image processing and webcam integration.
- **SpeechRecognition**: For audio transcription.
- **Ollama**: For local language model inference.

### Frontend
- **TailwindCSS**: Utility-first CSS framework for responsive design.
- **JavaScript**: For client-side interactivity.
- **HTML5**: For structure and content.
- **Chart.js**: For visualization of emotional data and depression reports.
- **MediaRecorder API**: For browser-based audio recording.
- **Font Awesome**: Icon library.

### Deployment
- **Local Development Server**: For development and testing.
- **MongoDB Atlas**: Cloud-hosted database service.

## Core Components

### Emotion Detection System

The emotion detection system is implemented in `emotion_model.py` and provides the following functionality:

1. **Text Emotion Analysis**:
   - Uses a fine-tuned DistilBERT model to classify text into emotional categories
   - Supports emotions like joy, sadness, anger, fear, etc.
   - Fallback mechanisms for graceful degradation when dependencies are missing

2. **Image Emotion Analysis**:
   - Analyzes facial expressions in images
   - Uses a pre-trained model for facial emotion detection
   - Handles error cases when image processing fails

3. **Audio Emotion Analysis**:
   - Converts speech to text using the wav2vec2 model
   - Applies text emotion analysis to the transcribed content
   - Provides robust error handling for audio processing issues

4. **Multi-Modal Fusion**:
   - Combines emotions detected from different modalities
   - Weighs contributions from text, audio, and image inputs
   - Handles cases where only a subset of modalities is available

5. **Depression Risk Assessment**:
   - Maps emotions to depression indicators with different correlation weights
   - Calculates a depression score based on emotional states
   - Classifies risk levels as low, moderate, or high

### Chat Service

The chat service is implemented in `chat_service.py` and provides:

1. **Conversation Management**:
   - Maintains conversation history for context
   - Ensures conversational continuity
   - Manages user-assistant interactions

2. **Emotional Response System**:
   - Adjusts responses based on detected emotional states
   - Provides empathetic and supportive messages
   - Tailors content to address specific emotional needs

3. **Background Monitoring**:
   - Captures webcam images at regular intervals
   - Analyzes facial expressions for emotional states
   - Updates the user's emotional profile continuously

4. **Ollama Integration**:
   - Connects to locally running language models via Ollama
   - Formats conversation history for context-aware responses
   - Provides fallback mechanisms when Ollama is unavailable

5. **Emotional Context Enhancement**:
   - Enhances AI responses with emotional context
   - Adds supportive resources for high depression risk
   - Provides tailored coping strategies based on emotional state

## Implementation Details

### Emotion Detection Models

The system uses three pre-trained models from Hugging Face:

1. **Text Emotion Model**: `bhadresh-savani/distilbert-base-uncased-emotion`
   - Classifies text into emotional categories (joy, sadness, anger, fear, etc.)
   - Fine-tuned on emotional text datasets

2. **Image Emotion Model**: `dima806/facial_emotions_image_detection`
   - Analyzes facial expressions in images
   - Detects emotions from facial features

3. **Audio Processing Model**: `facebook/wav2vec2-large-960h`
   - Converts speech to text for further analysis
   - Enables emotion detection from voice recordings

### Depression Risk Assessment

The system calculates depression risk using:

1. **Emotional State Mapping**:
   - Sadness: 0.8 correlation with depression
   - Fear: 0.6 correlation
   - Anger: 0.4 correlation
   - Joy: 0.0 correlation (inverse relationship)

2. **Temporal Analysis**:
   - Recent emotional states weighted more heavily
   - Persistence of negative emotions increases risk score
   - Calculation of moving averages for trend detection

3. **Risk Classification**:
   - Low: score < 0.3
   - Moderate: score 0.3 - 0.6
   - High: score > 0.6

## Features

### User Authentication System

The application includes a secure user authentication system with:

- User registration with email verification
- Secure login with password hashing via Flask-Bcrypt
- Session management for maintaining user state
- Account management options for users

### Emotion Analysis

The emotion analysis system provides:

- Real-time analysis of user inputs (text, images, audio)
- Multi-modal fusion for more accurate emotional assessment
- Visualization of emotional states over time
- Integration with the chat interface for dynamic response adjustment

### Depression Detection

The depression detection system offers:

- Continuous monitoring of emotional patterns
- Depression risk scoring based on emotional indicators
- Classification into risk levels (low, moderate, high)
- Trend analysis to track changes over time

### Chat Interface

The chat interface provides:

- Text-based conversation with the AI assistant
- Emotion-aware responses tailored to the user's state
- Background monitoring for continuous assessment
- Integration with the depression report generation feature

### Audio Chat

The audio chat feature allows users to communicate with the AI assistant using their voice:

#### Getting Started with Audio Chat

1. **Accessing the Audio Chat**:
   - From the dashboard, click on "Chat" in the navigation
   - In the chat interface, click the "Audio Chat" button at the top
   - You'll be redirected to the dedicated audio chat page

2. **Using the Audio Chat**:
   - Click the microphone button to start recording
   - Speak clearly into your microphone
   - Click the button again to stop recording
   - Your speech will be automatically converted to text
   - Click the send button to send your message to the AI assistant
   - The AI will respond with a text message
   - When you're ready to end the chat, click "End Chat & Generate Report" to receive a comprehensive depression analysis

3. **Requirements**:
   - A working microphone connected to your device
   - Modern browser that supports the Web Audio API (Chrome, Firefox, Edge, Safari)
   - Permission to access your microphone (you'll be prompted)

#### Technology Behind the Feature

The audio chat feature uses several technologies:

1. **Web Audio API**: For capturing audio from your microphone
2. **MediaRecorder API**: For recording the audio stream
3. **Speech Recognition**: Using Google's Speech-to-Text service through the SpeechRecognition library
4. **Audio Visualization**: Real-time visual feedback during recording

#### Privacy Considerations

- Audio recordings are processed on the server but are not permanently stored
- Only the transcribed text is saved in your chat history
- Audio processing occurs only when you explicitly click to record
- You can delete your chat history at any time

### Depression Report Generation

The depression report generation feature provides comprehensive analysis of the user's emotional state:

#### Generating a Depression Report

1. **From the Chat Interface**:
   - Engage in a conversation with the AI assistant
   - When you're ready, click the "End Chat & Generate Report" button
   - A detailed report will be generated based on your conversation patterns

2. **What's Analyzed**:
   - Emotional content of your messages
   - Depression indicators in your language
   - Patterns of emotional expression
   - Overall emotional tone of the conversation

#### Understanding Your Report

The depression report includes several key sections:

1. **Summary**:
   - Your overall depression risk level (Low, Moderate, or High)
   - A visual risk indicator showing the severity
   - A brief explanation of what the risk level means

2. **Emotional Analysis**:
   - A chart visualizing the distribution of different emotions
   - Identification of dominant emotions
   - Analysis of emotional patterns and their significance
   - Emotional chips showing each emotion and its intensity

3. **Recommendations**:
   - Personalized suggestions based on your emotional state and depression risk
   - Practical self-care activities
   - Mental health strategies
   - Resources for support
   - Preventive measures for maintaining well-being

#### Interpreting Risk Levels

- **Low Risk (0-30%)**: Shows generally balanced emotional responses with predominantly positive or neutral expressions. Continue with current self-care practices.

- **Moderate Risk (31-60%)**: Shows some indicators of mild to moderate depressive symptoms. While there are positive emotions present, there are also notable periods of negative emotional expression. Consider implementing the recommended strategies.

- **High Risk (61-100%)**: Shows indicators of significant depressive symptoms. The analysis reveals persistent negative emotional expressions and language patterns associated with depression. Consider consulting with a mental health professional.

## Database Schema

The MongoDB database uses the following document structure:

```json
{
  "username": "string",
  "email": "string",
  "password": "hashed_string",
  "created_at": "datetime",
  "activity_images": [
    {
      "filename": "string",
      "timestamp": "datetime",
      "image_path": "string",
      "activity_date": "date",
      "emotion_data": {
        "label": "string",
        "score": "float"
      },
      "depression_analysis": {
        "depression_score": "float",
        "depression_level": "string"
      }
    }
  ],
  "last_activity": "datetime",
  "emotional_data": [
    {
      "timestamp": "datetime",
      "source": "string",
      "text": "string",
      "emotion": {
        "label": "string",
        "score": "float"
      },
      "depression_score": "float"
    }
  ],
  "depression_scores": [
    {
      "timestamp": "datetime",
      "score": "float",
      "level": "string"
    }
  ],
  "depression_reports": [
    {
      "depression_score": "float",
      "emotions": [
        {
          "label": "string",
          "score": "float",
          "count": "int"
        }
      ],
      "summary": "string",
      "emotion_analysis": "string",
      "recommendations": [
        {
          "title": "string",
          "text": "string",
          "icon": "string"
        }
      ],
      "generated_at": "datetime"
    }
  ]
}
```

## Ollama Integration

The chat functionality is powered by Ollama, which provides local language model inference:

- **Recommended Models**: llama3, llama3.2, phi3, or deepseek-v2
- **Model Selection**: Run `python setup_ollama.py` to select and download your preferred model
- **Fallback System**: The application includes a robust fallback system that provides rule-based responses if Ollama is not available
- **Privacy**: All chat interactions are processed locally on your machine, ensuring privacy

To install Ollama and set up the models:
1. Download Ollama from [ollama.com](https://ollama.com/download)
2. Run `python setup_ollama.py` to download and configure your preferred model
3. Restart the application

## Installation and Setup

### Prerequisites

Before starting, ensure you have the following installed:

1. **Python 3.10 or higher**
2. **MongoDB** (local or Atlas connection)
3. **Webcam** for image capture
4. **Ollama** for local language model support

### Installation Steps

#### 1. Install Required Packages

```bash
pip install -r requirements.txt
```

The updated requirements.txt includes all necessary dependencies, including:
- Flask and MongoDB libraries
- Machine learning frameworks (PyTorch, Transformers)
- OpenCV for webcam access
- Ollama for chat functionality

#### 2. Download Pre-trained Models

Run the download script to pre-download the required models:

```bash
python download_models.py
```

This will download and cache:
- Text emotion detection model
- Facial emotion detection model 
- Speech-to-text model (for future audio support)

#### 3. Set Up Ollama

Install Ollama from [ollama.ai](https://ollama.ai) and run:

```bash
python setup_ollama.py
```

This script will check if Ollama is installed and provide installation instructions if needed. It will then download the gptoss:20b model used for enhanced chat functionality.

Alternatively, you can manually run:

```bash
ollama pull gptoss:20b
```

Note: The gptoss:20b model provides higher quality responses but requires more system resources. If your system cannot handle this model, you can modify the `chat_service.py` file to use a smaller model like "llama3".

#### 4. Configure MongoDB

Ensure your MongoDB connection string is properly configured in the app.py file. The application uses MongoDB Atlas by default.

#### 5. Start the Application

```bash
python app.py
```

The Flask application will start on http://localhost:5000

## Usage Guide

### Using the Chat Interface

1. **Accessing the Chat Interface**
   - Log in to your account
   - From the dashboard, click "Start Chat Session" in the Quick Actions panel

2. **Choosing Chat Mode**
   - The interface offers text chat and audio chat options
   - Select the mode that best suits your needs

3. **Using the Text Chat**
   - Type messages in the input field and press Enter or click Send
   - The AI will respond based on your message and detected emotional state
   - Current mood and depression risk are displayed at the top of the chat

4. **Using the Audio Chat**
   - Click the microphone button to start recording
   - Speak clearly into your microphone
   - Click the button again to stop recording
   - Your speech will be automatically converted to text
   - The AI will respond in text format

5. **Generating a Depression Report**
   - When you're ready to end the chat, click "End Chat & Generate Report"
   - Review your depression report with emotional analysis and recommendations
   - Download the report for your records

### Background Monitoring

- The system automatically captures webcam images every 20 seconds
- These images are analyzed for facial emotions and depression indicators
- The mood display updates based on both text and image analysis

### Wellness Tips

- The system provides personalized wellness tips based on your emotional state
- These appear during the conversation
- Tips are tailored to your specific emotional needs

## Privacy and Security

### Data Protection

- All user data is encrypted and securely stored
- Passwords are hashed using bcrypt
- Activity images are stored locally on the server
- Emotion analysis is performed locally
- No sharing of personal information without explicit consent

### Audio Privacy

- Audio recordings are processed on the server but are not permanently stored
- Only the transcribed text is saved in your chat history
- Audio processing occurs only when you explicitly click to record
- You can delete your chat history at any time

### Local Processing

- All chat interactions with Ollama are processed locally on your machine
- No data is sent to external servers for language model inference
- Background images are processed locally and not stored long-term
- Only emotion analysis results are saved to your account

## Future Enhancements

1. **Intervention Recommendations**:
   - AI-generated coping strategies based on emotional state
   - Personalized meditation and mindfulness exercises

2. **Professional Integration**:
   - Optional sharing of emotional data with healthcare providers
   - Alert system for critical mental health situations

3. **Advanced Analysis**:
   - Identification of emotional triggers
   - Correlation of activities with emotional states
   - Sleep and physical activity integration

4. **Mobile Application**:
   - Cross-platform mobile app for iOS and Android
   - Push notifications for mood tracking reminders

5. **Enhanced Voice Interaction**:
   - Voice-to-voice conversation capabilities
   - Emotion detection from voice patterns and tonality
   - Multilingual voice support

## Ethical Considerations

1. **Not a Replacement for Professional Help**:
   - The application should be used as a supplementary tool, not a substitute for professional mental health care
   - Clear disclaimers about limitations
   - Emergency resources provided for crisis situations

2. **Bias Mitigation**:
   - Regular auditing of AI models for cultural and demographic biases
   - Diverse training data to ensure equitable performance
   - Continuous improvement to address potential biases

3. **Transparency**:
   - Clear explanations of how emotional analysis works
   - No hidden data collection or analysis
   - User control over data collection and storage

4. **Crisis Support**:
   - Integration with crisis helplines
   - Clear guidance for emergency situations
   - Escalation protocols for high-risk cases

5. **Accessibility**:
   - Design considerations for users with disabilities
   - Support for different literacy levels
   - Affordability to ensure broad access

## Conclusion

The Mental Health Companion represents an innovative approach to mental health support, leveraging AI technologies to provide accessible, continuous emotional monitoring and support. By combining multi-modal emotion detection with personalized insights, the application aims to empower users with greater emotional self-awareness and proactive mental health management.

While not a replacement for professional mental health services, this tool can serve as a valuable complement to traditional care, particularly for continuous monitoring between appointments and early detection of concerning emotional patterns.
