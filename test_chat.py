"""
Test script for the chat service
"""

from chat_service import ChatService

def test_chat():
    """Test the chat service with a simple conversation"""
    chat = ChatService()
    
    print("=== Starting Chat Test ===")
    
    # Start chat
    welcome = chat.start_chat()
    print(f"Bot: {welcome['content']}")
    
    # Test messages
    test_messages = [
        "Hello there, how are you?",
        "I'm feeling a bit sad today",
        "Can you help me feel better?",
        "What are some good ways to improve mental health?",
        "Thank you for your help"
    ]
    
    for message in test_messages:
        print(f"\nUser: {message}")
        response = chat.send_message(message)
        print(f"Bot: {response['content']}")
        
        if 'emotion' in response:
            print(f"Detected emotion: {response['emotion']['label']} ({response['emotion']['score']:.2f})")
        
        if 'depression' in response:
            print(f"Depression analysis: {response['depression']['depression_level']} ({response['depression']['depression_score']:.2f})")
    
    print("\n=== Chat Test Complete ===")

if __name__ == "__main__":
    test_chat()
