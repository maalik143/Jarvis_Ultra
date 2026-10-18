"""
JARVIS ULTRA — High-Performance AI Voice Core
Powered by Google Gemini 2.0 Flash + Windows Native Speech Engine
"""

import os
import sys
import json
import re
import time
import subprocess
import webbrowser
import datetime
import threading
from typing import Callable, Optional

# Audio / Voice libraries
import win32com.client
import speech_recognition as sr
import pyautogui
import psutil

try:
    from google import genai
except ImportError:
    genai = None


class VoiceEngine:
    """Ultra-reliable Voice Output (TTS) & Input (STT)."""

    def __init__(self, on_speak_start: Optional[Callable] = None, on_speak_end: Optional[Callable] = None):
        self.on_speak_start = on_speak_start
        self.on_speak_end = on_speak_end
        self.recognizer = sr.Recognizer()
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.energy_threshold = 300
        self.recognizer.pause_threshold = 0.8
        self._speaker_lock = threading.Lock()

    def speak(self, text: str):
        """Speak text aloud through speakers cleanly and synchronously."""
        if not text:
            return
        
        # Clean text for speech (strip emojis, markdown, URLs)
        clean_text = re.sub(r'[*_#`~>]', '', text)
        clean_text = re.sub(r'https?://\S+', 'link', clean_text)
        clean_text = re.sub(r'\b[a-f0-9]{32,}\b', '', clean_text)
        clean_text = re.sub(r'[\U00010000-\U0010ffff]', '', clean_text)
        clean_text = clean_text.strip()
        
        if not clean_text:
            return

        if self.on_speak_start:
            self.on_speak_start(clean_text)

        with self._speaker_lock:
            try:
                speaker = win32com.client.Dispatch("SAPI.SpVoice")
                speaker.Rate = 1  # Natural speed
                speaker.Volume = 100
                speaker.Speak(clean_text)
            except Exception as e:
                print(f"[TTS Error]: {e}")

        if self.on_speak_end:
            self.on_speak_end()

    def listen(self, timeout: int = 6) -> Optional[str]:
        """Listen from microphone and transcribe speech."""
        with sr.Microphone() as source:
            try:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                print("[Listening...]")
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
                print("[Transcribing...]")
                query = self.recognizer.recognize_google(audio, language="en-US")
                print(f"[User Said]: {query}")
                return query
            except (sr.WaitTimeoutError, sr.UnknownValueError):
                return None
            except Exception as e:
                print(f"[Listen Error]: {e}")
                return None


class JarvisBrain:
    """Gemini 2.0 AI Core with Tool & Windows Automation."""

    SYSTEM_PROMPT = """You are JARVIS Ultra, an advanced AI Voice Assistant with full PC control.
You speak fluently in English and Somali.
You are concise, intelligent, respectful, and fast.
Keep voice answers conversational, direct, and under 3 sentences unless asked for details.
You can execute tasks like opening websites, launching applications, adjusting volume, searching the web, taking screenshots, and answering any general question."""

    def __init__(self, config_path: str):
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)
        
        self.api_key = self.config.get("api_key", "")
        self.model_name = self.config.get("model", "gemini-2.0-flash")
        self.client = None
        self.history = []
        self._init_gemini()

    def _init_gemini(self):
        if self.api_key and genai:
            try:
                self.client = genai.Client(api_key=self.api_key)
                print("✅ Gemini 2.0 Flash AI Brain Connected!")
            except Exception as e:
                print(f"[Gemini Init Error]: {e}")

    def execute_system_command(self, query: str) -> Optional[str]:
        """Direct local system commands for instant execution."""
        q = query.lower().strip()

        # 1. Time / Saacadda
        if any(w in q for w in ["what time", "current time", "saacada", "waqtiga", "saacaddu waa immisa"]):
            now = datetime.datetime.now().strftime("%I:%M %p")
            return f"The current time is {now}."

        # 2. Date / Taariikhda
        if any(w in q for w in ["what date", "today's date", "taariikhda", "maanta"]):
            today = datetime.datetime.now().strftime("%A, %B %d, %Y")
            return f"Today is {today}."

        # 3. Screenshot
        if any(w in q for w in ["screenshot", "take a screenshot", "sawir qaad", "shaashada sawir"]):
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            path = os.path.join(r"C:\Users\hp\Desktop\Projects_Software\Jarvis_Ultra\screenshots", f"shot_{ts}.png")
            pyautogui.screenshot(path)
            return "Screenshot captured and saved to screenshots folder, Boss."

        # 4. Open YouTube
        if "open youtube" in q or "youtube fur" in q:
            webbrowser.open("https://www.youtube.com")
            return "Opening YouTube."

        # 5. Search YouTube
        if q.startswith("play ") or "search youtube for " in q or "youtube ka raadi" in q:
            song = q.replace("play ", "").replace("search youtube for ", "").replace("youtube ka raadi", "").strip()
            webbrowser.open(f"https://www.youtube.com/results?search_query={song}")
            return f"Searching and playing {song} on YouTube."

        # 6. Open Google / Web Search
        if q.startswith("google ") or q.startswith("search for ") or "raadi " in q:
            target = q.replace("google ", "").replace("search for ", "").replace("raadi ", "").strip()
            webbrowser.open(f"https://www.google.com/search?q={target}")
            return f"Searching Google for {target}."

        # 7. Open Apps
        apps = {
            "calculator": "calc",
            "xisaabiyaha": "calc",
            "notepad": "notepad",
            "qoraal": "notepad",
            "chrome": "chrome",
            "browser": "chrome",
            "file explorer": "explorer",
            "files": "explorer",
            "cmd": "cmd",
            "terminal": "wt",
            "task manager": "taskmgr",
            "spotify": "spotify",
        }
        for name, cmd in apps.items():
            if f"open {name}" in q or f"fur {name}" in q:
                try:
                    subprocess.Popen(cmd, shell=True)
                    return f"Opening {name.capitalize()}, Boss."
                except Exception as e:
                    return f"Could not launch {name}: {e}"

        # 8. Volume controls
        if any(w in q for w in ["volume up", "codka kordhi", "louder"]):
            for _ in range(5):
                pyautogui.press("volumeup")
            return "Volume increased."
        if any(w in q for w in ["volume down", "codka dhim", "quieter"]):
            for _ in range(5):
                pyautogui.press("volumedown")
            return "Volume decreased."
        if any(w in q for w in ["mute volume", "mute", "aamus"]):
            pyautogui.press("volumemute")
            return "Volume muted."

        # 9. System Info
        if any(w in q for w in ["system info", "cpu", "battery", "ram", "xogta kombiyuutarka"]):
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            return f"CPU utilization is at {cpu} percent, and RAM usage is at {ram} percent."

        return None

    def ask(self, user_query: str) -> str:
        """Process user input with system tools or Gemini AI."""
        if not user_query or not user_query.strip():
            return "I am listening, Boss."

        # Check local system commands first
        sys_res = self.execute_system_command(user_query)
        if sys_res:
            return sys_res

        # If not a direct system shortcut, ask Gemini 2.0 AI
        if self.client:
            try:
                chat_context = f"{self.SYSTEM_PROMPT}\n\n"
                for msg in self.history[-4:]:
                    chat_context += f"{msg['role']}: {msg['text']}\n"
                chat_context += f"User: {user_query}\nJarvis:"

                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=chat_context
                )
                answer = response.text.strip()
                self.history.append({"role": "User", "text": user_query})
                self.history.append({"role": "Jarvis", "text": answer})
                return answer
            except Exception as e:
                print(f"[Gemini Query Error]: {e}")
                return f"I encountered an issue connecting to the AI cloud: {e}"

        return "I understood your command, but the AI brain is currently in offline mode."
