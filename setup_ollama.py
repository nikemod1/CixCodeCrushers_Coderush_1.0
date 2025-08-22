"""
Setup script for Ollama integration with Mental Health Companion
"""

import os
import subprocess
import platform
import sys
import time
import json
from pathlib import Path

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("Warning: requests library not installed. Will use subprocess for API calls.")

def check_ollama_installed():
    """Check if Ollama is installed by looking for the command or binary."""
    # First try the command
    try:
        result = subprocess.run(
            ["ollama", "--version"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            check=False
        )
        if result.returncode == 0:
            version = result.stdout.decode('utf-8').strip()
            print(f"✅ Ollama found: {version}")
            return True
    except FileNotFoundError:
        pass
    
    # If command not found, check common installation paths
    system = platform.system()
    if system == "Windows":
        possible_paths = [
            os.path.expanduser("~\\AppData\\Local\\Programs\\Ollama\\ollama.exe"),
            "C:\\Program Files\\Ollama\\ollama.exe",
            "C:\\Ollama\\ollama.exe"
        ]
    elif system == "Darwin":  # macOS
        possible_paths = [
            "/usr/local/bin/ollama",
            os.path.expanduser("~/ollama")
        ]
    else:  # Linux
        possible_paths = [
            "/usr/local/bin/ollama",
            "/usr/bin/ollama",
            os.path.expanduser("~/ollama")
        ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"✅ Ollama found at: {path}")
            return True
    
    print("❌ Ollama not found")
    return False

def check_ollama_running():
    """Check if Ollama server is running."""
    if REQUESTS_AVAILABLE:
        try:
            response = requests.get("http://localhost:11434/api/version", timeout=5)
            if response.status_code == 200:
                version_info = response.json()
                print(f"✅ Ollama is running - Version: {version_info.get('version', 'unknown')}")
                return True
            else:
                print(f"❌ Ollama returned status code {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("❌ Ollama server is not running")
            return False
        except Exception as e:
            print(f"❌ Error checking Ollama: {str(e)}")
            return False
    else:
        # Fallback to curl if requests is not available
        try:
            result = subprocess.run(
                ["curl", "-s", "http://localhost:11434/api/version"], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                check=False
            )
            if result.returncode == 0:
                try:
                    version_info = json.loads(result.stdout.decode('utf-8'))
                    print(f"✅ Ollama is running - Version: {version_info.get('version', 'unknown')}")
                    return True
                except json.JSONDecodeError:
                    print("❌ Ollama returned invalid response")
                    return False
            else:
                print("❌ Ollama server is not running")
                return False
        except Exception as e:
            print(f"❌ Error checking Ollama: {str(e)}")
            return False

def start_ollama_server():
    """Attempt to start the Ollama server."""
    system = platform.system()
    
    try:
        if system == "Windows":
            # On Windows, start in a new window
            subprocess.Popen(
                ["ollama", "serve"], 
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            # On Unix systems, start in background
            subprocess.Popen(
                ["ollama", "serve"], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE
            )
        
        print("Starting Ollama server... please wait")
        # Give it a few seconds to start
        time.sleep(5)
        
        # Check if it's running now
        return check_ollama_running()
    except Exception as e:
        print(f"❌ Failed to start Ollama server: {str(e)}")
        return False

def list_available_models():
    """List available models in Ollama."""
    if REQUESTS_AVAILABLE:
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                if not models:
                    print("No models available in Ollama")
                    return []
                    
                print("\nAvailable models in Ollama:")
                model_names = []
                for model in models:
                    name = model.get("name")
                    model_names.append(name)
                    print(f"- {name}")
                return model_names
            else:
                print(f"❌ Failed to list models (status code: {response.status_code})")
                return []
        except Exception as e:
            print(f"❌ Error listing models: {str(e)}")
            return []
    else:
        # Fallback to curl
        try:
            result = subprocess.run(
                ["curl", "-s", "http://localhost:11434/api/tags"], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                check=False
            )
            if result.returncode == 0:
                try:
                    data = json.loads(result.stdout.decode('utf-8'))
                    models = data.get("models", [])
                    if not models:
                        print("No models available in Ollama")
                        return []
                        
                    print("\nAvailable models in Ollama:")
                    model_names = []
                    for model in models:
                        name = model.get("name")
                        model_names.append(name)
                        print(f"- {name}")
                    return model_names
                except json.JSONDecodeError:
                    print("❌ Ollama returned invalid response")
                    return []
            else:
                print(f"❌ Failed to list models")
                return []
        except Exception as e:
            print(f"❌ Error listing models: {str(e)}")
            return []

def download_model(model_name):
    """Download a model from Ollama."""
    print(f"\nDownloading model '{model_name}'...")
    print("This may take a while depending on your internet speed and model size.")
    
    try:
        process = subprocess.Popen(
            ["ollama", "pull", model_name], 
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Print output in real-time
        for line in process.stdout:
            print(line.strip())
        
        process.wait()
        
        if process.returncode == 0:
            print(f"✅ Model '{model_name}' downloaded successfully")
            return True
        else:
            print(f"❌ Failed to download model. Return code: {process.returncode}")
            return False
    except Exception as e:
        print(f"❌ Error downloading model: {str(e)}")
        return False

def update_chat_service(model_name):
    """Update the chat_service.py file to use the specified model."""
    try:
        filepath = "chat_service.py"
        if not os.path.exists(filepath):
            print(f"❌ Cannot find {filepath}")
            return False
            
        with open(filepath, 'r') as f:
            content = f.read()
            
        # Update the model name
        import re
        pattern = r"self\.ollama_model = \"[^\"]*\""
        replacement = f'self.ollama_model = "{model_name}"'
        
        new_content = re.sub(pattern, replacement, content)
        
        with open(filepath, 'w') as f:
            f.write(new_content)
            
        print(f"✅ Updated chat_service.py to use model '{model_name}'")
        return True
    except Exception as e:
        print(f"❌ Error updating chat_service.py: {str(e)}")
        return False

def print_installation_instructions():
    """Print instructions for installing Ollama."""
    system = platform.system()
    
    print("\n==== OLLAMA INSTALLATION INSTRUCTIONS ====")
    print("1. Visit https://ollama.com/download")
    
    if system == "Windows":
        print("2. Download the Windows installer")
        print("3. Run the installer and follow the prompts")
    elif system == "Darwin":  # macOS
        print("2. Download the macOS installer")
        print("3. Open the downloaded file and drag Ollama to your Applications folder")
    else:  # Linux
        print("2. Run the following command in your terminal:")
        print("   curl -fsSL https://ollama.com/install.sh | sh")
    
    print("\nAfter installation:")
    print("1. Start Ollama")
    print("2. Run this script again to configure models")

def main():
    """Main function to set up Ollama for the Mental Health Companion."""
    print("==== MENTAL HEALTH COMPANION - OLLAMA SETUP ====")
    
    # Check if Ollama is installed
    installed = check_ollama_installed()
    
    if not installed:
        print_installation_instructions()
        return
    
    # Check if Ollama is running
    running = check_ollama_running()
    
    # If not running, try to start it
    if not running:
        print("Attempting to start Ollama...")
        running = start_ollama_server()
    
    if not running:
        print("\n❌ Could not start Ollama server")
        print("Please start it manually before continuing")
        print("On Windows: Start the Ollama application")
        print("On macOS/Linux: Run 'ollama serve' in a terminal")
        return
    
    # List available models
    available_models = list_available_models()
    
    # Recommended models for the Mental Health Companion
    recommended_models = [
        "llama3.2:latest",
        "phi3:latest",
        "deepseek-v2:latest",
        "llama3:latest"
    ]
    
    # Check which recommended models are missing
    missing_models = [model for model in recommended_models if model not in available_models]
    
    if missing_models:
        print("\nRecommended models not yet installed:")
        for i, model in enumerate(missing_models, 1):
            print(f"{i}. {model}")
        
        try:
            choice = input("\nEnter the number of the model to download (or 'q' to quit): ")
            if choice.lower() == 'q':
                return
                
            choice = int(choice)
            if 1 <= choice <= len(missing_models):
                model_to_download = missing_models[choice-1]
                if download_model(model_to_download):
                    # Ask if they want to use this model
                    use_model = input(f"Would you like to use {model_to_download} as the default model for the chat? (y/n): ")
                    if use_model.lower() in ['y', 'yes']:
                        update_chat_service(model_to_download)
            else:
                print("Invalid choice.")
        except ValueError:
            print("Please enter a valid number.")
    else:
        print("\nAll recommended models are already installed!")
        
        # Ask which model to use
        if available_models:
            print("\nWhich model would you like to use for the chat?")
            for i, model in enumerate(available_models, 1):
                print(f"{i}. {model}")
                
            try:
                choice = input("\nEnter the number of the model to use (or 'q' to quit): ")
                if choice.lower() == 'q':
                    return
                    
                choice = int(choice)
                if 1 <= choice <= len(available_models):
                    model_to_use = available_models[choice-1]
                    update_chat_service(model_to_use)
                else:
                    print("Invalid choice.")
            except ValueError:
                print("Please enter a valid number.")
    
    print("\n==== SETUP COMPLETE ====")
    print("You can now run the Mental Health Companion application!")
    print("Run 'python app.py' to start the server")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSetup interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
