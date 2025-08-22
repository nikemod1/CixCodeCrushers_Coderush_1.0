"""
Chat Service for Mental Health Companion
Integrates Ollama for LLM-based chat responses and analyzes user's text
and images for depression detection.
"""

import os
import time
import threading
import base64
import json
from datetime import datetime
from emotion_model import emotion_detector

# Try to import optional dependencies with fallbacks
try:
    import cv2
except ImportError:
    print("Warning: OpenCV not available. Background image capture will be disabled.")
    cv2 = None

try:
    import ollama
except ImportError:
    print("Warning: Ollama not available. Using fallback chat responses.")
    ollama = None

class ChatService:
    def __init__(self, db=None, user_id=None):
        """Initialize the chat service with user information and database connection"""
        self.db = db
        self.user_id = user_id
        self.capture_interval = 20  # seconds
        self.stop_capture = False
        self.capture_thread = None
        self.camera = None
        self.ollama_model = "llama3.2"  # Using llama3.2 model which is available
        self.conversation_history = []
        
    def start_chat(self, chat_type="text"):
        """Start a new chat session"""
        self.conversation_history = []
        
        # Create a more engaging and comforting welcome message
        welcome_messages = [
            "Hi there! I'm Chi Chi, your mental health companion. I'm here to chat, listen, and support you. How are you feeling today?",
            "Hello! I'm Chi Chi, and I'm here to provide a safe space for you to share your thoughts and feelings. How's your day going so far?",
            "Welcome! I'm Chi Chi, your friendly mental health companion. I'm all ears if you'd like to talk about anything that's on your mind today.",
            "Hi! I'm Chi Chi. Think of me as a supportive friend who's here to listen without judgment. What's on your mind today?"
        ]
        
        import random
        welcome_content = random.choice(welcome_messages)
        
        welcome_message = {
            "role": "assistant",
            "content": welcome_content
        }
        self.conversation_history.append(welcome_message)
        
        # Start background image capture if enabled
        if chat_type == "text":
            try:
                self.start_background_capture()
            except Exception as e:
                print(f"Warning: Could not start background capture: {e}")
        
        return welcome_message
    
    def send_message(self, message):
        """Send a message to the chat and get a response"""
        if not message or not message.strip():
            return {"role": "assistant", "content": "I didn't catch that. Could you please say something?"}
        
        # Add user message to history
        user_message = {"role": "user", "content": message}
        self.conversation_history.append(user_message)
        
        # Analyze message for emotion and depression
        try:
            emotion_result = emotion_detector.detect_from_text(message)
            depression_analysis = emotion_detector.detect_depression(text=message)
            
            # Store in database if available
            if self.db and self.user_id:
                from bson import ObjectId
                self.db.users.update_one(
                    {'_id': ObjectId(self.user_id)},
                    {
                        '$push': {
                            'emotional_data': {
                                'timestamp': datetime.utcnow(),
                                'source': 'chat',
                                'text': message,
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
        except Exception as e:
            print(f"Error analyzing message: {e}")
            emotion_result = {"label": "unknown", "score": 0.0}
            depression_analysis = {"depression_score": 0.0, "depression_level": "unknown"}
        
        # Get response from Ollama
        try:
            # Prepare context about emotional state for better responses
            system_message = f"""You are a compassionate mental health companion named Chi Chi, designed to create a warm, supportive environment for users. 
            
            EMOTIONAL CONTEXT:
            - The user's current emotion appears to be: {emotion_result['label']} (confidence: {emotion_result['score']:.2f})
            - Their depression risk level is: {depression_analysis['depression_level']} (score: {depression_analysis['depression_score']:.2f})
            
            CONVERSATION GOALS:
            1. Create a safe, judgment-free space where the user feels heard and validated
            2. Build rapport through warmth, genuine interest, and appropriate emotional responsiveness
            3. Encourage self-expression while respecting boundaries
            4. Offer gentle support and practical coping strategies when appropriate
            
            APPROACH:
            - Respond with empathy, warmth, and genuine care
            - Use a conversational, friendly tone while maintaining appropriate professionalism
            - Validate the user's feelings without judgment ("It makes sense you'd feel that way...")
            - Listen actively and reflect back what you hear ("It sounds like you're feeling...")
            - Normalize emotions ("Many people experience similar feelings...")
            - Offer perspective when helpful, but avoid minimizing their experiences
            - Use hopeful, encouraging language while acknowledging challenges
            - Ask thoughtful follow-up questions to show interest and deepen understanding
            
            IMPORTANT:
            - Never explicitly mention their depression score or emotion analysis
            - Subtly adjust your tone and suggestions based on their emotional state
            - If they show signs of serious distress or self-harm, gently encourage professional help
            - Remember personal details they share and reference them appropriately in later responses
            - Always prioritize creating a comfortable, trusting relationship over giving advice
            
            Today's date is August 23, 2025."""
            
            # Format conversation history for Ollama
            formatted_history = []
            for msg in self.conversation_history[-5:]:  # Only use last 5 messages for context
                formatted_history.append({"role": msg["role"], "content": msg["content"]})
            
            # Add system message at the beginning
            formatted_history.insert(0, {"role": "system", "content": system_message})
            
            # Get response from Ollama if available, otherwise use fallback
            if ollama:
                try:
                    response = ollama.chat(
                        model=self.ollama_model,
                        messages=formatted_history
                    )
                    assistant_message_content = response['message']['content']
                except Exception as e:
                    print(f"Error connecting to Ollama: {e}")
                    # Fall back to rule-based responses
                    assistant_message_content = self._get_fallback_response(emotion_result, depression_analysis, message)
            else:
                # Use rule-based fallback responses
                assistant_message_content = self._get_fallback_response(emotion_result, depression_analysis, message)
            
            assistant_message = {"role": "assistant", "content": assistant_message_content}
            self.conversation_history.append(assistant_message)
            
            # Add additional context about their emotional state
            enhanced_response = self._enhance_response_with_emotional_context(
                assistant_message_content, 
                emotion_result, 
                depression_analysis
            )
            
            return {
                "role": "assistant", 
                "content": enhanced_response,
                "emotion": emotion_result,
                "depression": depression_analysis
            }
            
        except Exception as e:
            print(f"Error getting chat response: {e}")
            fallback_message = {"role": "assistant", "content": "I'm having trouble connecting right now. Could you try again?"}
            self.conversation_history.append(fallback_message)
            return fallback_message
    
    def _enhance_response_with_emotional_context(self, response, emotion, depression):
        """Add subtle emotional context to the response based on analysis"""
        enhanced_response = response
        
        # For high depression risk, add supportive resources
        if depression['depression_level'] == 'high' and depression['depression_score'] > 0.7:
            resources = "\n\nIf you're feeling overwhelmed, remember that help is available. Consider talking to a trusted friend, family member, or mental health professional. You don't have to face these feelings alone."
            enhanced_response += resources
        
        # For moderate depression risk, add gentle encouragement
        elif depression['depression_level'] == 'moderate' and depression['depression_score'] > 0.4:
            encouragement = "\n\nRemember that it's okay to have difficult days. Taking small steps to care for yourself can make a difference. Perhaps try a short walk outside or connect with someone you trust."
            enhanced_response += encouragement
        
        # For specific emotions, add tailored support
        emotion_label = emotion['label'].lower()
        emotion_score = emotion['score']
        
        if emotion_label == 'sadness' and emotion_score > 0.7:
            suggestion = "\n\nWhen feelings of sadness are present, it can help to engage your senses. Maybe try listening to a favorite uplifting song, enjoying a warm drink, or stepping outside for some fresh air."
            enhanced_response += suggestion
        
        elif emotion_label == 'fear' and emotion_score > 0.7:
            grounding = "\n\nWhen anxiety or fear feels strong, grounding techniques can help. Try the 5-4-3-2-1 technique: notice 5 things you see, 4 things you can touch, 3 things you hear, 2 things you smell, and 1 thing you taste."
            enhanced_response += grounding
        
        elif emotion_label == 'anger' and emotion_score > 0.7:
            calming = "\n\nWhen strong emotions like frustration arise, taking a moment for some deep breaths can help create space between feelings and reactions. Breathing in for 4 counts and out for 6 can be especially calming."
            enhanced_response += calming
        
        # For positive emotions, add reinforcement
        elif emotion_label == 'joy' and emotion_score > 0.7:
            reinforcement = "\n\nIt's wonderful to experience these positive feelings. Taking a moment to savor and appreciate them can help extend their benefits."
            enhanced_response += reinforcement
        
        return enhanced_response
    
    def _get_fallback_response(self, emotion, depression, user_message):
        """Generate fallback responses based on detected emotion when Ollama is unavailable"""
        # Check for specific keywords in the message
        message_lower = user_message.lower()
        
        # Check for greeting patterns
        if any(word in message_lower for word in ["hello", "hi", "hey", "greetings"]):
            greetings = [
                "Hello! It's so nice to connect with you today. How are you feeling?",
                "Hi there! I'm Chi Chi, your mental health companion. I'm here to chat and support you. How's your day going?",
                "Hey! Thanks for reaching out. I'm here to listen and support you. How are you doing today?",
                "Hello! I'm glad you're here. How are you feeling today? I'm here to listen and chat."
            ]
            import random
            return random.choice(greetings)
        
        # Check for gratitude
        if any(word in message_lower for word in ["thanks", "thank you", "appreciate"]):
            gratitude_responses = [
                "You're very welcome. I'm glad I could help. Is there anything else on your mind you'd like to talk about?",
                "I'm happy I could be here for you. Remember, I'm always available when you need someone to talk to.",
                "It means a lot to hear that. I'm here to support you anytime you need. How else are you feeling today?",
                "You're welcome! Your wellbeing matters, and I'm glad to be part of your journey. Is there anything else you'd like to discuss?"
            ]
            import random
            return random.choice(gratitude_responses)
        
        # Check for questions about the bot
        if "who are you" in message_lower or "what are you" in message_lower:
            bot_descriptions = [
                "I'm Chi Chi, your Mental Health Companion. I'm an AI designed to provide emotional support and help monitor your mental wellbeing. I'm here to listen, chat, and support you in a judgment-free space.",
                "I'm Chi Chi! Think of me as a supportive friend who's always here to listen. I'm designed to provide emotional support, help you track your mental wellbeing, and offer gentle guidance when needed.",
                "I'm your Mental Health Companion, Chi Chi. I'm here to provide a safe space for you to express your thoughts and feelings, offer support, and help you monitor your emotional wellbeing over time.",
                "Hello! I'm Chi Chi, an AI companion focused on mental health support. I'm designed to listen, respond with empathy, and help you track your emotional wellbeing. I'm here for you whenever you need someone to talk to."
            ]
            import random
            return random.choice(bot_descriptions)
        
        # Check for help requests
        if any(word in message_lower for word in ["help", "assist", "support"]):
            help_responses = [
                "I'm here to help. Feel free to share what's on your mind, and we can work through it together. Remember that while I'm designed to offer support, for serious concerns, it's important to reach out to a mental health professional.",
                "I'm listening and ready to support you. Would you like to talk about what's troubling you? Sometimes just expressing our thoughts can help us see things more clearly.",
                "You're not alone, and I'm here to support you. Feel free to share as much or as little as you're comfortable with. What kind of help are you looking for today?",
                "I'm here to provide support in any way I can. Would it help to talk through what you're experiencing? For serious concerns, I'd also encourage connecting with a mental health professional who can provide specialized care."
            ]
            import random
            return random.choice(help_responses)
        
        # Responses for feeling statements
        if any(word in message_lower for word in ["i feel", "feeling", "felt", "i am", "i'm"]):
            if any(word in message_lower for word in ["sad", "down", "depressed", "unhappy", "miserable"]):
                return self._get_sadness_response()
            elif any(word in message_lower for word in ["angry", "mad", "frustrated", "annoyed", "irritated"]):
                return self._get_anger_response()
            elif any(word in message_lower for word in ["scared", "afraid", "anxious", "nervous", "worried"]):
                return self._get_fear_response()
            elif any(word in message_lower for word in ["happy", "good", "great", "wonderful", "fantastic"]):
                return self._get_joy_response()
        
        # Responses based on emotional state
        if emotion['label'].lower() == 'sadness':
            return self._get_sadness_response()
        elif emotion['label'].lower() == 'anger':
            return self._get_anger_response()
        elif emotion['label'].lower() == 'fear':
            return self._get_fear_response()
        elif emotion['label'].lower() == 'joy':
            return self._get_joy_response()
        else:
            general_responses = [
                "Thank you for sharing that with me. I'm here to listen and support you. Would you like to tell me more about what's on your mind?",
                "I appreciate you reaching out. Sometimes having someone to talk to can make a difference. How else have you been feeling lately?",
                "I'm here to support you. Feel free to share whatever you're comfortable with, and we can explore it together. What matters most to you right now?",
                "I'm listening and I care about what you're going through. Would you like to tell me more about your experience, or is there something specific you'd like to focus on today?"
            ]
            import random
            return random.choice(general_responses)
            
    def _get_sadness_response(self):
        """Generate responses for sadness emotion"""
        responses = [
            "I'm sorry to hear you're feeling down. Remember that emotions come and go, and difficult moments will pass. Would it help to talk about what's causing these feelings?",
            "It sounds like you're going through a tough time. Sometimes sharing your feelings can help lighten the emotional burden. What's been on your mind lately?",
            "I notice a sense of sadness in your message. It's okay to feel this way, and acknowledging your emotions is an important step. Would you like to explore some gentle activities that might help lift your mood?",
            "I hear that you're feeling sad. Many people experience these feelings, and it's a normal part of being human. Is there something specific that triggered these feelings?",
            "When we're feeling sad, it can sometimes feel like it will last forever, but emotions do shift and change. Would it help to talk about what might bring you some comfort right now?"
        ]
        import random
        return random.choice(responses)
        
    def _get_anger_response(self):
        """Generate responses for anger emotion"""
        responses = [
            "I notice there's some frustration in your message. Taking a few deep breaths can sometimes help clear your mind. Would you like to talk more about what's bothering you?",
            "It seems like you're feeling frustrated. That's a natural emotion when facing challenges. What specifically is triggering these feelings right now?",
            "I can sense some anger in your words. Sometimes writing down exactly what's upsetting you can help process these emotions. Would you like to share more about the situation?",
            "It sounds like you're feeling angry, which is a completely valid emotion. Sometimes anger points us toward something important that needs our attention. What do you think your anger might be telling you?",
            "When we feel angry, our bodies often respond physically too. Taking a moment to notice these sensations can sometimes help. Would it help to talk about what triggered these feelings?"
        ]
        import random
        return random.choice(responses)
        
    def _get_fear_response(self):
        """Generate responses for fear emotion"""
        responses = [
            "It sounds like you might be experiencing some anxiety. Remember that you're not alone, and many people go through similar feelings. Is there something specific that's causing concern right now?",
            "I notice some worry in your message. Sometimes anxiety is our mind's way of trying to protect us. Can you identify what specifically feels threatening or uncertain?",
            "Your message suggests you might be feeling anxious. Grounding exercises can sometimes help - try noticing 5 things you can see, 4 things you can touch, 3 things you can hear, 2 things you can smell, and 1 thing you can taste.",
            "Feeling anxious or worried is something many of us experience. Sometimes it helps to break down what feels overwhelming into smaller pieces. Would it help to talk about what's causing these feelings?",
            "I hear that you're feeling fearful or anxious. These emotions can be uncomfortable, but they're also normal responses to stress or uncertainty. Would it help to explore some calming techniques together?"
        ]
        import random
        return random.choice(responses)
        
    def _get_joy_response(self):
        """Generate responses for joy emotion"""
        responses = [
            "It's wonderful to see you in good spirits! Positive moments like these are great opportunities to reflect on what brings you happiness and how to incorporate more of it into your daily life.",
            "I'm glad to hear you're feeling positive! What's contributed to your good mood today?",
            "It's great to see your upbeat message! Savoring positive emotions can help extend their benefits. Maybe take a moment to really appreciate what's going well right now?",
            "I'm happy to hear you're feeling good! These positive moments are worth celebrating. Is there something specific that brought you joy today?",
            "It's wonderful to hear the positivity in your message! Taking time to notice and appreciate good feelings can actually help strengthen them. What's bringing you happiness right now?"
        ]
        import random
        return random.choice(responses)
    
    def start_background_capture(self):
        """Start background image capture thread"""
        if self.capture_thread and self.capture_thread.is_alive():
            return  # Already running
        
        if not cv2:
            print("Warning: OpenCV not available. Background image capture disabled.")
            return
        
        self.stop_capture = False
        self.capture_thread = threading.Thread(target=self._capture_loop)
        self.capture_thread.daemon = True
        self.capture_thread.start()
    
    def stop_background_capture(self):
        """Stop the background image capture thread"""
        self.stop_capture = True
        if self.camera:
            self.camera.release()
            self.camera = None
    
    def _capture_loop(self):
        """Background thread that captures images periodically"""
        try:
            self.camera = cv2.VideoCapture(0)
            
            while not self.stop_capture:
                ret, frame = self.camera.read()
                if not ret:
                    print("Failed to capture image")
                    time.sleep(5)
                    continue
                
                # Save image to temporary file
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                if not os.path.exists('temp'):
                    os.makedirs('temp')
                temp_path = os.path.join('temp', f'capture_{timestamp}.jpg')
                cv2.imwrite(temp_path, frame)
                
                # Analyze image for emotion and depression
                try:
                    emotion_result = emotion_detector.detect_from_image(temp_path)
                    depression_analysis = emotion_detector.detect_depression(image_path=temp_path)
                    
                    # Store in database if available
                    if self.db and self.user_id:
                        from bson import ObjectId
                        
                        # Move to permanent storage
                        permanent_filename = f"{self.user_id}_{timestamp}.jpg"
                        permanent_path = os.path.join('static', 'activity_images', permanent_filename)
                        
                        # Ensure directory exists
                        os.makedirs(os.path.dirname(permanent_path), exist_ok=True)
                        
                        # Move file
                        import shutil
                        shutil.copy2(temp_path, permanent_path)
                        
                        # Create image metadata
                        image_data = {
                            'filename': permanent_filename,
                            'timestamp': datetime.utcnow(),
                            'image_path': f"/static/activity_images/{permanent_filename}",
                            'activity_date': datetime.now().date().isoformat(),
                            'emotion_data': emotion_result,
                            'depression_analysis': depression_analysis,
                            'source': 'background_capture'
                        }
                        
                        # Update database
                        self.db.users.update_one(
                            {'_id': ObjectId(self.user_id)},
                            {
                                '$push': {
                                    'activity_images': image_data,
                                    'emotional_data': {
                                        'timestamp': datetime.utcnow(),
                                        'source': 'background_image',
                                        'emotion': emotion_result,
                                        'depression_score': depression_analysis['depression_score']
                                    },
                                    'depression_scores': {
                                        'timestamp': datetime.utcnow(),
                                        'score': depression_analysis['depression_score'],
                                        'level': depression_analysis['depression_level']
                                    }
                                }
                            }
                        )
                except Exception as e:
                    print(f"Error analyzing background image: {e}")
                
                # Remove temporary file
                try:
                    os.remove(temp_path)
                except:
                    pass
                
                # Wait for next capture
                time.sleep(self.capture_interval)
        
        except Exception as e:
            print(f"Error in background capture: {e}")
        finally:
            if self.camera:
                self.camera.release()
                self.camera = None

# Initialize a singleton instance
chat_service = None

def get_chat_service(db=None, user_id=None):
    """Get a global chat service instance"""
    global chat_service
    if chat_service is None:
        chat_service = ChatService(db, user_id)
    else:
        # Update db and user_id if needed
        chat_service.db = db
        chat_service.user_id = user_id
    return chat_service
