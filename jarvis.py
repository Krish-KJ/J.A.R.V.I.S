import speech_recognition as sr
import webbrowser
import google.generativeai as genai
import os
import sys
import time
import dotenv
import pyttsx3 # <--- UPGRADE: Import the Text-to-Speech library

# --- Configuration ---
# Load environment variables from the .env file
dotenv.load_dotenv()

# Your API key will be read from the environment variables.
# For this code to work, you must set the GEMINI_API_KEY environment variable.
# It is highly recommended to use environment variables for security.
try:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
except KeyError:
    print("Error: 'GEMINI_API_KEY' environment variable not found.")
    print("Please set your API key as an environment variable before running this script.")
    sys.exit(1)

# --- Speech Recognition and TTS Setup ---
r = sr.Recognizer()
# <--- UPGRADE: Initialize the TTS engine
engine = pyttsx3.init()
# Optional: Adjust the voice, rate, or volume here
# voices = engine.getProperty('voices')
# engine.setProperty('voice', voices[0].id) # Change to a different voice if available
# engine.setProperty('rate', 150) # Speed of speech

# --- Functions ---

def speak(text):
    """
    UPGRADE: This function now uses a Text-to-Speech engine to speak the text aloud.
    It still prints to the console as a fallback.
    """
    print(f"JARVIS: {text}")
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"TTS Error: Could not speak the text. {e}")

def listen():
    """Listens for a voice command and returns the transcribed text."""
    with sr.Microphone() as source:
        print("Listening...")
        r.adjust_for_ambient_noise(source)
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=5)
            print("Processing...")
            command = r.recognize_google(audio)
            print(f"You: {command}")
            return command.lower()
        except sr.WaitTimeoutError:
            speak("I did not hear any command. Please try again.")
            return None
        except sr.UnknownValueError:
            speak("Sorry, I could not understand what you said.")
            return None
        except sr.RequestError as e:
            speak(f"Could not request results from Google Speech Recognition service; {e}")
            return None

def open_website(url):
    """
    UPGRADE: Added error handling to gracefully fail if the browser cannot be opened.
    Opens a website in the default web browser.
    """
    try:
        webbrowser.open_new_tab(url)
        speak(f"Opening {url.split('//')[1].split('/')[0]} for you.")
    except Exception as e:
        speak("I'm sorry, I was unable to open the website.")
        print(f"Error opening website: {e}")

def process_command(command):
    """Processes the voice command."""
    if not command:
        return

    # Hardcoded commands for opening websites
    if "open google" in command or "go to google" in command:
        open_website("https://www.google.com")
    elif "open youtube" in command or "go to youtube" in command:
        open_website("https://www.youtube.com")
    elif "open wikipedia" in command or "go to wikipedia" in command:
        open_website("https://www.wikipedia.org")
    elif "open github" in command:
        open_website("https://www.github.com")
    elif "open facebook" in command:
        open_website("https://www.facebook.com")
    elif "open twitter" in command:
        open_website("https://www.twitter.com")
    
    # Check for a specific keyword to exit the program
    elif "exit" in command or "stop" in command or "bye" in command:
        speak("Goodbye, sir. Shutting down systems.")
        sys.exit(0)

    # If no hardcoded command is matched, send to Gemini API
    else:
        ask_gemini(command)

def ask_gemini(prompt):
    """Sends a query to the Gemini API and prints the response."""
    try:
        model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20')
        speak("Thinking...")
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                candidate_count=1
            )
        )
        # Check if the response contains text and print it
        if response.text:
            speak(response.text)
        else:
            speak("I'm sorry, I couldn't generate a response for that command.")
            print(f"Debug: API response was empty or not in text format: {response}")
    except Exception as e:
        speak("An error occurred while communicating with the API.")
        print(f"Error: {e}")

# --- Main Loop ---

def main():
    speak("JARVIS systems online. Awaiting your command.")
    while True:
        command = listen()
        if command:
            process_command(command)
        time.sleep(1) # Small delay to prevent continuous listening

if __name__ == "__main__":
    main()
