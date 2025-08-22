# Setting Up and Running the Enhanced Mental Health Companion

This guide provides step-by-step instructions for setting up and running the enhanced Mental Health Companion application with the new chat features.

## Prerequisites

Before starting, ensure you have the following installed:

1. **Python 3.10 or higher**
2. **MongoDB** (local or Atlas connection)
3. **Webcam** for image capture
4. **Ollama** for local language model support

## Installation Steps

### 1. Install Required Packages

```bash
pip install -r requirements.txt
```

The updated requirements.txt includes all necessary dependencies, including:
- Flask and MongoDB libraries
- Machine learning frameworks (PyTorch, Transformers)
- OpenCV for webcam access
- Ollama for chat functionality

### 2. Download Pre-trained Models

Run the download script to pre-download the required models:

```bash
python download_models.py
```

This will download and cache:
- Text emotion detection model
- Facial emotion detection model 
- Speech-to-text model (for future audio support)

### 3. Set Up Ollama

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

### 4. Configure MongoDB

Ensure your MongoDB connection string is properly configured in the app.py file. The application uses MongoDB Atlas by default.

### 5. Start the Application

```bash
python app.py
```

The Flask application will start on http://localhost:5000

## Using the Enhanced Chat Feature

1. **Accessing the Chat Interface**
   - Log in to your account
   - From the dashboard, click "Start Chat Session" in the Quick Actions panel

2. **Choosing Chat Mode**
   - The interface offers text chat (fully functional)
   - Audio chat will be available in a future update

3. **Using the Chat**
   - Type messages in the input field and press Enter or click Send
   - The AI will respond based on your message and detected emotional state
   - Current mood and depression risk are displayed at the top of the chat

4. **Background Monitoring**
   - The system automatically captures webcam images every 20 seconds
   - These images are analyzed for facial emotions and depression indicators
   - The mood display updates based on both text and image analysis

5. **Wellness Tips**
   - The system provides personalized wellness tips based on your emotional state
   - These appear in a popup panel during the conversation

## Privacy Features

- Background images are processed locally and not stored long-term
- Only emotion analysis results are saved to your account
- All processing happens on your device
- You can exit the chat at any time to stop monitoring

## Troubleshooting

### Camera Access Issues

If the application cannot access your webcam:

1. Check browser permissions for camera access
2. Ensure no other application is using the webcam
3. Try refreshing the page

### Chat Connection Issues

If the chat doesn't connect to Ollama:

1. Verify Ollama is running (check with `ollama list`)
2. Ensure the Llama 3 model is downloaded
3. Restart the Flask application

### Model Loading Errors

If emotion models fail to load:

1. Run the download_models.py script again
2. Check internet connection for downloading models
3. Ensure you have sufficient disk space

## Technical Support

For issues or questions, please contact the development team or raise an issue in the project repository.

## Data Usage Notice

The Mental Health Companion analyzes and stores:
- Text messages sent during chat sessions
- Emotional analysis results from text and images
- Depression risk assessments

This data is used solely for providing personalized support and is not shared with third parties.

## Disclaimer

This application is not a replacement for professional mental health care. If you are experiencing severe distress, please contact a mental health professional or crisis helpline immediately.
