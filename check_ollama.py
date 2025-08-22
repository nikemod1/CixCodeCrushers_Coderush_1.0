import requests
import sys
import subprocess
import platform
import os

def check_ollama_installed():
    """Check if Ollama is installed by looking for typical installation paths."""
    system = platform.system()
    
    if system == "Windows":
        # Common Windows installation paths
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
            return True, path
    
    print("❌ Ollama not found in common installation locations")
    return False, None

def check_ollama_running():
    """Check if Ollama server is running by making a request."""
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
        print("❌ Ollama server is not running (connection refused)")
        return False
    except Exception as e:
        print(f"❌ Error checking Ollama: {str(e)}")
        return False

def check_model_available(model_name="gptoss:20b"):
    """Check if the specified model is available in Ollama."""
    try:
        response = requests.get(f"http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [model.get("name") for model in models]
            
            if model_name in model_names:
                print(f"✅ Model '{model_name}' is available")
                return True
            else:
                print(f"❌ Model '{model_name}' is not available in Ollama")
                print(f"Available models: {', '.join(model_names) if model_names else 'None'}")
                return False
        else:
            print(f"❌ Failed to list models (status code: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Error checking model availability: {str(e)}")
        return False

def start_ollama_server(ollama_path=None):
    """Attempt to start the Ollama server if it's not running."""
    system = platform.system()
    
    if not ollama_path:
        installed, ollama_path = check_ollama_installed()
        if not installed:
            print("Cannot start Ollama server - Ollama not found")
            return False
    
    try:
        if system == "Windows":
            # On Windows, start in a new window
            subprocess.Popen([ollama_path, "serve"], 
                           creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            # On Unix systems, start in background
            subprocess.Popen([ollama_path, "serve"], 
                           stdout=subprocess.PIPE, 
                           stderr=subprocess.PIPE)
        
        print("Attempting to start Ollama server... please wait a few seconds")
        # Give it a few seconds to start
        import time
        time.sleep(5)
        
        # Check if it's running now
        return check_ollama_running()
    except Exception as e:
        print(f"❌ Failed to start Ollama server: {str(e)}")
        return False

def download_model(model_name="gptoss:20b"):
    """Download the specified model."""
    try:
        print(f"Attempting to download model '{model_name}'...")
        print("This may take a while depending on your internet speed and the model size.")
        print("The gptoss:20b model is quite large (around 20GB), so please be patient.")
        
        response = requests.post(
            "http://localhost:11434/api/pull",
            json={"name": model_name},
            stream=True
        )
        
        if response.status_code == 200:
            for line in response.iter_lines():
                if line:
                    print(f"Download progress: {line.decode('utf-8')}")
            print(f"✅ Model '{model_name}' downloaded successfully")
            return True
        else:
            print(f"❌ Failed to download model (status code: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Error downloading model: {str(e)}")
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
    print("2. Run this script again to check if Ollama is running")
    print("3. If necessary, download the gptoss:20b model")
    print("======================================")

def main():
    print("==== OLLAMA STATUS CHECK ====")
    
    # Check if Ollama is installed
    installed, ollama_path = check_ollama_installed()
    
    if not installed:
        print_installation_instructions()
        return
    
    # Check if Ollama is running
    running = check_ollama_running()
    
    # If not running, try to start it
    if not running:
        print("Attempting to start Ollama server...")
        running = start_ollama_server(ollama_path)
    
    # If still not running, provide instructions
    if not running:
        print("\n❌ Could not start Ollama server automatically")
        print("Please start it manually:")
        
        system = platform.system()
        if system == "Windows":
            print("1. Open a command prompt")
            print(f"2. Run: \"{ollama_path}\" serve")
        else:
            print("1. Open a terminal")
            print("2. Run: ollama serve")
        
        return
    
    # Check if model is available
    model_available = check_model_available("gptoss:20b")
    
    # If model is not available, offer to download it
    if not model_available:
        user_input = input("Would you like to download the gptoss:20b model now? (y/n): ")
        if user_input.lower() in ['y', 'yes']:
            download_model("gptoss:20b")
        else:
            print("\nTo download the model later, run:")
            print("ollama pull gptoss:20b")
    
    print("\n==== SUMMARY ====")
    print(f"Ollama installed: {'✅ Yes' if installed else '❌ No'}")
    print(f"Ollama running: {'✅ Yes' if running else '❌ No'}")
    print(f"gptoss:20b available: {'✅ Yes' if model_available else '❌ No'}")
    
    if installed and running and model_available:
        print("\n✅ Everything is set up correctly! You can use gptoss:20b in your application.")
    else:
        print("\n❌ Some components are missing or not running correctly.")
        print("Please address the issues mentioned above.")

if __name__ == "__main__":
    main()
