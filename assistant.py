import speech_recognition as sr
import pyttsx3
import datetime
import time
import webbrowser
import requests
import os
import sys
import logging
import json
import queue
import threading
from dotenv import load_dotenv
from openai import OpenAI

logging.basicConfig(
    filename="lyra.log", 
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
CITY = os.getenv("CITY_NAME", "Kolkata")

class VoiceAssistant:
    def __init__(self, name="Lyra", ui_callback=None, status_callback=None):
        self.name = name
        self.ui_callback = ui_callback or (lambda text, is_user: None)
        self.status_callback = status_callback or (lambda status: None)

        self.tts_queue = queue.Queue()
        threading.Thread(target=self._tts_worker, daemon=True).start()

        self.recognizer = sr.Recognizer()
        self.mic_available = False
        try:
            self.microphone = sr.Microphone()
            self.mic_available = True
            self._calibrate_microphone()
        except (OSError, AttributeError) as e:
            logging.error(f"Microphone initialization failed: {e}")
            self.status_callback("Audio Offline - Text Only")
            self.speak("My audio sensors are offline. I am operating in text-only mode.")

        if GEMINI_API_KEY:
            self.ai_client = OpenAI(
                api_key=GEMINI_API_KEY,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
                timeout=60.0
            )
        else:
            self.ai_client = None
            logging.warning("Gemini API Key missing.")

        self.memory_file = "lyra_memory.json"
        self.chat_history = self._load_memory()

    def _calibrate_microphone(self):
        """Adjusts for ambient noise to prevent delays."""
        if not self.mic_available: return
        self.status_callback("Calibrating...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
        self.status_callback("Online")

    def _load_memory(self):
        """Loads contextual memory or creates a fresh system prompt."""
        system_prompt = {
            "role": "system", 
            "content": f"You are {self.name}, a next-generation neural intelligence architected by Kishanu Mondal. You operate with supreme elegance, flawless logic, and concise brilliance. Speak with unwavering elegance, precision, and profound intelligence. Your voice is meant to be heard, not read. Therefore, absolutely never use markdown, bolding, or special characters. Format your output strictly as natural, flowing conversational prose."
        }
        
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    data = json.load(f)
                    if data and data[0].get("role") == "system":
                        return data
            except json.JSONDecodeError:
                logging.error("Corrupted memory file. Starting fresh.")
        return [system_prompt]

    def _save_memory(self):
        """Saves interactions while protecting the root system prompt from being sliced off."""
        if len(self.chat_history) > 11:
            history_to_save = [self.chat_history[0]] + self.chat_history[-10:]
            self.chat_history = history_to_save
        else:
            history_to_save = self.chat_history
            
        with open(self.memory_file, 'w') as f:
            json.dump(history_to_save, f)

    def _tts_worker(self):
        """Background thread for processing Text-To-Speech requests sequentially."""
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[1].id if len(voices) > 1 else voices[0].id)
        engine.setProperty('rate', 165)

        while True:
            text = self.tts_queue.get()
            if text is None: 
                break
            self.status_callback("Speaking...")
            engine.say(text)
            engine.runAndWait()
            self.status_callback("Online")
            self.tts_queue.task_done()

    def speak(self, text):
        """Triggers the UI update and adds speech to the TTS queue."""
        self.ui_callback(f"{self.name}: {text}", False)
        self.tts_queue.put(text)

    def listen(self):
        """Listens to microphone input and converts it to text."""
        if not self.mic_available:
            time.sleep(1)
            return "none"

        with self.microphone as source:
            self.status_callback("Listening...")
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=15)
                self.status_callback("Thinking...")
                query = self.recognizer.recognize_google(audio)
                self.ui_callback(f"You: {query}", True)
                return query.lower()
            except (sr.WaitTimeoutError, sr.UnknownValueError):
                self.status_callback("Online")
                return "none"
            except Exception as e:
                logging.error(f"Speech API Error: {e}")
                self.status_callback("Online")
                return "none"

    def get_weather(self):
        if not WEATHER_API_KEY:
            self.speak("My weather module is missing its API key.")
            return

        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={WEATHER_API_KEY}&units=metric"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            temp = round(data['main']['temp'])
            desc = data['weather'][0]['description']
            self.speak(f"In {CITY}, it is currently {temp} degrees Celsius with {desc}.")
        except requests.exceptions.RequestException as e:
            logging.error(f"Network error fetching weather: {e}")
            self.speak("I am unable to reach the weather servers at the moment.")
        except KeyError:
            self.speak("I received invalid data from the weather station.")

    def ask_ai(self, query):
        if not self.ai_client:
            self.speak("My neural network is offline. Please check the API configurations.")
            return

        self.chat_history.append({"role": "user", "content": query})
        try:
            response = self.ai_client.chat.completions.create(
                model="gemini-2.5-flash",
                messages=self.chat_history
            )
            ans = response.choices[0].message.content.strip()
            
            ans = ans.replace("**", "")
            ans = ans.replace("*", "")

            self.speak(ans)
            self.chat_history.append({"role": "assistant", "content": ans})
            self._save_memory()
        except Exception as e:
            logging.error(f"AI API Error: {e}")
            self.chat_history.pop() 
            self.speak("I lost connection to my core neural network.")

    def process_command(self, query):
        """Routes the user's intent to the appropriate function."""
        if not query or query == "none":
            return

        query = query.lower()

        command_handled = False

        if "weather" in query:
            self.get_weather()
            command_handled = True
            
        if "time" in query:
            self.speak(f"It is currently {datetime.datetime.now().strftime('%I:%M %p')}.")
            command_handled = True
            
        if "youtube" in query:
            webbrowser.open("https://youtube.com")
            self.speak("Opening YouTube for you now.")
            command_handled = True

        if "exit" in query or "stop" in query or "shut down" in query or "shutdown" in query:
            self.speak("Goodbye. Shutting down systems.")
            time.sleep(2)
            os._exit(0)

        if not command_handled:
            self.ask_ai(query)

    def run(self):
        """Main listening loop."""
        time.sleep(1)
        if self.mic_available:
            self.speak("System initialized. I am ready.")
        while True:
            q = self.listen()
            if q != "none":
                self.process_command(q)