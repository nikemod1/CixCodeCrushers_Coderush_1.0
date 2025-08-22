import ollama

def test_ollama():
    """Test that Ollama is working with the configured model"""
    try:
        # Get the list of available models
        models = ollama.list()
        print("Available models:", models)
        
        # Test a simple chat with llama3
        print("\nTesting chat with llama3:latest model...")
        response = ollama.chat(
            model="llama3:latest",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant."
                },
                {
                    "role": "user",
                    "content": "Hello! How are you today?"
                }
            ]
        )
        
        print(f"\nResponse from llama3:latest: {response['message']['content']}")
        print("\nOllama is working correctly!")
        return True
    except Exception as e:
        print(f"Error testing Ollama: {e}")
        return False

if __name__ == "__main__":
    test_ollama()
