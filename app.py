from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from pymongo import MongoClient
from flask_bcrypt import Bcrypt
import os
import json
import tempfile
from datetime import datetime
from werkzeug.utils import secure_filename
from bson import ObjectId
from emotion_model import emotion_detector
from chat_service import get_chat_service

# Import speech recognition libraries
try:
    import speech_recognition as sr
except ImportError:
    print("Warning: speech_recognition not available. Audio transcription will be disabled.")
    sr = None

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a secure secret key
bcrypt = Bcrypt(app)

# Configure upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'activity_images')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# MongoDB connection
client = MongoClient("mongodb+srv://ycce:123@cluster0.tiu64si.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client['mental_health_companion']
users = db['users']

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if user already exists
        if users.find_one({'email': email}):
            flash('Email already registered', 'error')
            return redirect(url_for('register'))
        
        # Hash the password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # Create new user
        new_user = {
            'username': username,
            'email': email,
            'password': hashed_password,
            'created_at': datetime.utcnow(),
            'activity_images': [],  # Initialize empty array for activity images
            'last_activity': None,  # Track last activity timestamp
            'emotional_data': [],   # Store emotional analysis results
            'depression_scores': [] # Track depression scores over time
        }
        users.insert_one(new_user)
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = users.find_one({'email': email})
        
        if user and bcrypt.check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])
            session['username'] = user['username']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
            
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get user data including activity images
    user = users.find_one({'_id': ObjectId(session['user_id'])})
    activity_images = user.get('activity_images', [])
    
    # Sort activity images by timestamp in descending order
    activity_images.sort(key=lambda x: x['timestamp'], reverse=True)
    
    # Get depression scores for chart
    depression_scores = user.get('depression_scores', [])
    depression_scores.sort(key=lambda x: x['timestamp'])
    
    # Format for chart display (last 10 entries)
    recent_scores = depression_scores[-10:] if len(depression_scores) > 10 else depression_scores
    chart_data = {
        'labels': [score['timestamp'].strftime('%m/%d') for score in recent_scores],
        'scores': [score['score'] for score in recent_scores]
    }
    
    # Calculate overall depression risk
    avg_score = 0
    if depression_scores:
        recent_scores = depression_scores[-5:] if len(depression_scores) >= 5 else depression_scores
        avg_score = sum(score['score'] for score in recent_scores) / len(recent_scores)
    
    depression_risk = "Low"
    if avg_score > 0.6:
        depression_risk = "High"
    elif avg_score > 0.3:
        depression_risk = "Moderate"
    
    return render_template('dashboard.html', 
                         username=session['username'],
                         activity_images=activity_images,
                         chart_data=json.dumps(chart_data),
                         depression_risk=depression_risk,
                         depression_score=round(avg_score, 2))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/analyze_text_emotion', methods=['POST'])
def analyze_text_emotion():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    
    data = request.json
    text = data.get('text', '')
    
    if not text:
        return jsonify({'success': False, 'error': 'No text provided'}), 400
    
    try:
        # Analyze text for emotions
        emotion_result = emotion_detector.detect_from_text(text)
        
        # Detect depression from text
        depression_analysis = emotion_detector.detect_depression(text=text)
        
        # Store the emotional data
        users.update_one(
            {'_id': ObjectId(session['user_id'])},
            {
                '$push': {
                    'emotional_data': {
                        'timestamp': datetime.utcnow(),
                        'source': 'text',
                        'text': text,
                        'emotion': emotion_result,
                        'depression_score': depression_analysis['depression_score']
                    },
                    'depression_scores': {
                        'timestamp': datetime.utcnow(),
                        'score': depression_analysis['depression_score'],
                        'level': depression_analysis['depression_level']
                    }
                },
                '$set': {
                    'last_activity': datetime.utcnow()
                }
            }
        )
        
        return jsonify({
            'success': True,
            'emotion': emotion_result,
            'depression_analysis': depression_analysis
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/get_depression_trend', methods=['GET'])
def get_depression_trend():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    
    try:
        user = users.find_one({'_id': ObjectId(session['user_id'])})
        depression_scores = user.get('depression_scores', [])
        
        # Limit to last 30 entries and sort by timestamp
        depression_scores.sort(key=lambda x: x['timestamp'], reverse=True)
        depression_scores = depression_scores[:30]
        
        # Format for chart display
        chart_data = [
            {
                'date': score['timestamp'].strftime('%Y-%m-%d'),
                'score': score['score'],
                'level': score['level']
            }
            for score in depression_scores
        ]
        
        return jsonify({
            'success': True,
            'depression_trend': chart_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/upload_activity_image', methods=['POST'])
def upload_activity_image():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401

    if 'image' not in request.files:
        return jsonify({'success': False, 'error': 'No image file'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        try:
            # Create a unique filename using timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{session['user_id']}_{timestamp}.jpg"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Save the file
            file.save(filepath)
            
            # Analyze the image for emotions
            emotion_result = emotion_detector.analyze_activity_image(filepath)
            
            # Detect depression from image
            depression_analysis = emotion_detector.detect_depression(image_path=filepath)
            
            # Create image metadata
            image_data = {
                'filename': filename,
                'timestamp': datetime.utcnow(),
                'image_path': f"/static/activity_images/{filename}",
                'activity_date': datetime.now().date().isoformat(),
                'emotion_data': emotion_result,
                'depression_analysis': depression_analysis
            }
            
            # Update user document with new activity image and emotional data
            users.update_one(
                {'_id': ObjectId(session['user_id'])},
                {
                    '$push': {
                        'activity_images': image_data,
                        'emotional_data': {
                            'timestamp': datetime.utcnow(),
                            'source': 'image',
                            'emotion': emotion_result,
                            'depression_score': depression_analysis['depression_score']
                        },
                        'depression_scores': {
                            'timestamp': datetime.utcnow(),
                            'score': depression_analysis['depression_score'],
                            'level': depression_analysis['depression_level']
                        }
                    },
                    '$set': {
                        'last_activity': datetime.utcnow()
                    }
                }
            )
            
            return jsonify({
                'success': True, 
                'filename': filename,
                'timestamp': image_data['timestamp'].isoformat(),
                'emotion': emotion_result,
                'depression_analysis': depression_analysis
            })
        except Exception as e:
            # If any error occurs, return error response
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

        return jsonify({'success': False, 'error': 'Invalid file type'}), 400

@app.route('/chat')
def chat():
    """Render the chat interface"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('chat.html')

@app.route('/audio_chat')
def audio_chat():
    """Render the audio chat interface"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('audio_chat.html')

@app.route('/chat/start', methods=['POST'])
def start_chat():
    """Start a new chat session"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    
    data = request.json
    chat_type = data.get('chat_type', 'text')
    
    # Initialize chat service with current user info
    chat_service = get_chat_service(db, session['user_id'])
    welcome_message = chat_service.start_chat(chat_type)
    
    return jsonify({
        'success': True,
        'message': welcome_message
    })

@app.route('/chat/message', methods=['POST'])
def chat_message():
    """Process a chat message and get a response"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    
    data = request.json
    message = data.get('message', '')
    
    if not message:
        return jsonify({'success': False, 'error': 'No message provided'}), 400
    
    # Get chat service with current user info
    chat_service = get_chat_service(db, session['user_id'])
    response = chat_service.send_message(message)
    
    return jsonify({
        'success': True,
        'response': response
    })

@app.route('/chat/analyze_image', methods=['POST'])
def chat_analyze_image():
    """Analyze an image captured during chat"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    
    if 'image' not in request.files:
        return jsonify({'success': False, 'error': 'No image file'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'}), 400
    
    try:
        # Create a unique filename using timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{session['user_id']}_chat_{timestamp}.jpg"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save the file
        file.save(filepath)
        
        # Analyze the image for emotions
        emotion_result = emotion_detector.detect_from_image(filepath)
        
        # Detect depression from image
        depression_analysis = emotion_detector.detect_depression(image_path=filepath)
        
        # Create image metadata
        image_data = {
            'filename': filename,
            'timestamp': datetime.utcnow(),
            'image_path': f"/static/activity_images/{filename}",
            'activity_date': datetime.now().date().isoformat(),
            'emotion_data': emotion_result,
            'depression_analysis': depression_analysis,
            'source': 'chat_background'
        }
        
        # Update user document with new image and emotional data
        users.update_one(
            {'_id': ObjectId(session['user_id'])},
            {
                '$push': {
                    'activity_images': image_data,
                    'emotional_data': {
                        'timestamp': datetime.utcnow(),
                        'source': 'chat_image',
                        'emotion': emotion_result,
                        'depression_score': depression_analysis['depression_score']
                    },
                    'depression_scores': {
                        'timestamp': datetime.utcnow(),
                        'score': depression_analysis['depression_score'],
                        'level': depression_analysis['depression_level']
                    }
                },
                '$set': {
                    'last_activity': datetime.utcnow()
                }
            }
        )
        
        return jsonify({
            'success': True,
            'emotion': emotion_result,
            'depression': depression_analysis
        })
    except Exception as e:
        print(f"Error analyzing chat image: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/audio/transcribe', methods=['POST'])
def transcribe_audio():
    """Transcribe audio to text"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    
    if 'audio' not in request.files:
        return jsonify({'success': False, 'error': 'No audio file'}), 400
    
    audio_file = request.files['audio']
    
    if audio_file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'}), 400
    
    try:
        # Check if speech recognition is available
        if not sr:
            return jsonify({'success': False, 'error': 'Speech recognition not available'}), 500
        
        # Save the audio file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            audio_file.save(tmp_file.name)
            tmp_filepath = tmp_file.name
        
        # Initialize recognizer
        recognizer = sr.Recognizer()
        
        # Transcribe audio
        with sr.AudioFile(tmp_filepath) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
        
        # Remove temporary file
        os.unlink(tmp_filepath)
        
        return jsonify({
            'success': True,
            'text': text
        })
    except sr.UnknownValueError:
        return jsonify({
            'success': False,
            'error': 'Speech could not be understood'
        }), 400
    except sr.RequestError as e:
        return jsonify({
            'success': False,
            'error': f'Could not request results from Speech Recognition service: {e}'
        }), 500
    except Exception as e:
        print(f"Error transcribing audio: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/audio/message', methods=['POST'])
def audio_message():
    """Process an audio message and get a response"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    
    if 'audio' not in request.files:
        return jsonify({'success': False, 'error': 'No audio file'}), 400
    
    audio_file = request.files['audio']
    
    if audio_file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'}), 400
    
    try:
        # Check if speech recognition is available
        if not sr:
            return jsonify({'success': False, 'error': 'Speech recognition not available'}), 500
        
        # Save the audio file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            audio_file.save(tmp_file.name)
            tmp_filepath = tmp_file.name
        
        # Initialize recognizer
        recognizer = sr.Recognizer()
        
        # Transcribe audio
        with sr.AudioFile(tmp_filepath) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
        
        # Remove temporary file
        os.unlink(tmp_filepath)
        
        # Get chat service with current user info
        chat_service = get_chat_service(db, session['user_id'])
        response = chat_service.send_message(text)
        
        return jsonify({
            'success': True,
            'text': text,
            'response': response
        })
    except sr.UnknownValueError:
        return jsonify({
            'success': False,
            'error': 'Speech could not be understood'
        }), 400
    except sr.RequestError as e:
        return jsonify({
            'success': False,
            'error': f'Could not request results from Speech Recognition service: {e}'
        }), 500
    except Exception as e:
        print(f"Error processing audio message: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/audio/generate_report', methods=['POST'])
def generate_depression_report():
    """Generate a comprehensive depression analysis report based on chat history"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    
    try:
        # Get user data
        user = users.find_one({'_id': ObjectId(session['user_id'])})
        
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        # Get emotional data from recent interactions
        emotional_data = user.get('emotional_data', [])
        
        # Sort by timestamp and get most recent entries (last 20)
        emotional_data.sort(key=lambda x: x.get('timestamp', datetime.min), reverse=True)
        recent_data = emotional_data[:20]
        
        # Calculate depression score from recent data
        depression_scores = [entry.get('depression_score', 0) for entry in recent_data if 'depression_score' in entry]
        avg_depression_score = sum(depression_scores) / len(depression_scores) if depression_scores else 0
        
        # Analyze emotions
        emotions_count = {}
        for entry in recent_data:
            if 'emotion' in entry:
                emotion_label = entry['emotion'].get('label', 'neutral').lower()
                emotion_score = entry['emotion'].get('score', 0)
                
                if emotion_label in emotions_count:
                    emotions_count[emotion_label]['count'] += 1
                    emotions_count[emotion_label]['total_score'] += emotion_score
                else:
                    emotions_count[emotion_label] = {
                        'count': 1,
                        'total_score': emotion_score
                    }
        
        # Calculate average score for each emotion
        emotions = []
        for label, data in emotions_count.items():
            avg_score = data['total_score'] / data['count']
            emotions.append({
                'label': label.capitalize(),
                'score': avg_score,
                'count': data['count']
            })
        
        # Sort emotions by score in descending order
        emotions.sort(key=lambda x: x['score'], reverse=True)
        
        # Generate summary text based on depression score
        summary = ""
        if avg_depression_score > 0.6:
            summary = "Based on your conversation patterns, there are indicators of significant depressive symptoms. The analysis shows persistent negative emotional expressions and language patterns associated with depression."
        elif avg_depression_score > 0.3:
            summary = "Your conversation patterns show some indicators of mild to moderate depressive symptoms. While there are some positive emotions present, there are also notable periods of negative emotional expression."
        else:
            summary = "Based on your conversation patterns, your depression risk appears to be low. The analysis shows generally balanced emotional responses with predominantly positive or neutral expressions."
        
        # Generate emotion analysis text
        emotion_analysis = ""
        if emotions:
            dominant_emotion = emotions[0]['label'].lower()
            if dominant_emotion == 'joy':
                emotion_analysis = "Your conversations show predominantly positive emotions, with joy being the most frequent. This suggests a generally positive outlook."
            elif dominant_emotion in ['sadness', 'fear', 'anger']:
                emotion_analysis = f"Your conversations show a significant presence of {dominant_emotion}, which can be associated with depressive states when persistent. There are also signs of {emotions[1]['label'].lower() if len(emotions) > 1 else 'other emotions'}."
            else:
                emotion_analysis = f"Your conversations show a mix of emotions, with {dominant_emotion} being most prominent. The emotional variety suggests normal emotional fluctuations."
        else:
            emotion_analysis = "There isn't enough emotional data to provide a detailed analysis."
        
        # Generate personalized recommendations
        recommendations = []
        
        # Basic recommendations for everyone
        recommendations.append({
            'title': 'Practice Mindfulness',
            'text': 'Take 5-10 minutes each day for mindful breathing or meditation to center yourself and reduce stress.',
            'icon': 'fa-leaf'
        })
        
        # Add specific recommendations based on depression score
        if avg_depression_score > 0.6:
            recommendations.append({
                'title': 'Seek Professional Support',
                'text': 'Consider reaching out to a mental health professional to discuss your feelings and explore treatment options.',
                'icon': 'fa-user-md'
            })
            recommendations.append({
                'title': 'Establish Daily Routine',
                'text': 'Create and maintain a structured daily routine, including regular sleep times, meals, and activities.',
                'icon': 'fa-calendar'
            })
        elif avg_depression_score > 0.3:
            recommendations.append({
                'title': 'Physical Activity',
                'text': 'Aim for 30 minutes of moderate exercise at least 3 times a week to boost mood and energy levels.',
                'icon': 'fa-walking'
            })
            recommendations.append({
                'title': 'Social Connection',
                'text': 'Schedule time to connect with supportive friends or family members, even if briefly.',
                'icon': 'fa-users'
            })
        else:
            recommendations.append({
                'title': 'Maintain Healthy Habits',
                'text': 'Continue with activities that bring you joy and maintain your well-being.',
                'icon': 'fa-heart'
            })
            recommendations.append({
                'title': 'Preventive Self-Care',
                'text': 'Practice regular self-care activities to maintain your emotional resilience.',
                'icon': 'fa-spa'
            })
        
        # Create the report object
        report = {
            'depression_score': avg_depression_score,
            'emotions': emotions,
            'summary': summary,
            'emotion_analysis': emotion_analysis,
            'recommendations': recommendations,
            'generated_at': datetime.now().isoformat()
        }
        
        # Save the report to user's data
        users.update_one(
            {'_id': ObjectId(session['user_id'])},
            {
                '$push': {
                    'depression_reports': report
                }
            }
        )
        
        return jsonify({
            'success': True,
            'report': report
        })
        
    except Exception as e:
        print(f"Error generating depression report: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
