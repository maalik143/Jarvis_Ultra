"""
JARVIS ULTRA — Futuristic AI Voice Assistant GUI
High-Tech Arc Reactor HUD with Live Voice Interaction
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext
import datetime

# Add directory to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from jarvis_engine import VoiceEngine, JarvisBrain


class JarvisUltraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("J.A.R.V.I.S. ULTRA — Mark L")
        self.root.geometry("820x680")
        self.root.configure(bg="#050B14")
        self.root.resizable(False, False)

        # Brain & Voice
        config_path = os.path.join(BASE_DIR, "data", "config.json")
        self.voice = VoiceEngine(on_speak_start=self._on_speaking, on_speak_end=self._on_idle)
        self.brain = JarvisBrain(config_path)

        self.is_listening = False
        self._build_ui()

        # Startup greeting
        threading.Thread(target=self._startup_greet, daemon=True).start()

    def _build_ui(self):
        # 1. Header Banner
        header = tk.Frame(self.root, bg="#0A1424", height=60)
        header.pack(fill="x", padx=10, pady=10)

        title_lbl = tk.Label(
            header,
            text="⚡ J . A . R . V . I . S   U L T R A",
            font=("Segoe UI", 18, "bold"),
            fg="#00E5FF",
            bg="#0A1424"
        )
        title_lbl.pack(side="left", padx=15, pady=10)

        self.status_lbl = tk.Label(
            header,
            text="● SYSTEM ONLINE (GEMINI 2.0)",
            font=("Segoe UI", 10, "bold"),
            fg="#00FFAA",
            bg="#0A1424"
        )
        self.status_lbl.pack(side="right", padx=15, pady=10)

        # 2. Glowing Arc Reactor Center Visualizer
        reactor_frame = tk.Frame(self.root, bg="#050B14", height=140)
        reactor_frame.pack(fill="x", pady=5)

        self.canvas = tk.Canvas(reactor_frame, width=130, height=130, bg="#050B14", highlightthickness=0)
        self.canvas.pack()
        self._draw_arc_reactor("#00E5FF")

        self.state_text = tk.Label(
            reactor_frame,
            text="READY FOR COMMAND",
            font=("Segoe UI", 11, "bold"),
            fg="#80D8FF",
            bg="#050B14"
        )
        self.state_text.pack(pady=4)

        # 3. Chat / Activity Console
        console_frame = tk.Frame(self.root, bg="#0A1424", bd=1, relief="solid")
        console_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.chat_log = scrolledtext.ScrolledText(
            console_frame,
            wrap="word",
            font=("Consolas", 10),
            bg="#040910",
            fg="#B0BEC5",
            insertbackground="#00E5FF",
            selectbackground="#005B94",
            bd=0,
            padx=12,
            pady=10
        )
        self.chat_log.pack(fill="both", expand=True)
        self.chat_log.tag_config("user", foreground="#00FFAA", font=("Consolas", 10, "bold"))
        self.chat_log.tag_config("jarvis", foreground="#00E5FF", font=("Consolas", 10))
        self.chat_log.tag_config("sys", foreground="#FFB300", font=("Consolas", 9, "italic"))

        # 4. Action / Control Bar
        control_frame = tk.Frame(self.root, bg="#050B14")
        control_frame.pack(fill="x", padx=20, pady=10)

        # Text input
        self.entry_var = tk.StringVar()
        self.entry = tk.Entry(
            control_frame,
            textvariable=self.entry_var,
            font=("Segoe UI", 11),
            bg="#0A1424",
            fg="#FFFFFF",
            insertbackground="#00E5FF",
            bd=1,
            relief="solid"
        )
        self.entry.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 10))
        self.entry.bind("<Return>", lambda e: self.send_text_command())

        # Send Button
        send_btn = tk.Button(
            control_frame,
            text="SEND",
            font=("Segoe UI", 10, "bold"),
            bg="#0091EA",
            fg="#FFFFFF",
            activebackground="#00B0FF",
            activeforeground="#FFFFFF",
            bd=0,
            padx=15,
            pady=6,
            cursor="hand2",
            command=self.send_text_command
        )
        send_btn.pack(side="left", padx=(0, 10))

        # Microphone Button
        self.mic_btn = tk.Button(
            control_frame,
            text="🎤 SPEAK",
            font=("Segoe UI", 10, "bold"),
            bg="#00C853",
            fg="#FFFFFF",
            activebackground="#00E676",
            activeforeground="#FFFFFF",
            bd=0,
            padx=20,
            pady=6,
            cursor="hand2",
            command=self.trigger_voice_listen
        )
        self.mic_btn.pack(side="left")

        # Quick command bar
        quick_frame = tk.Frame(self.root, bg="#050B14")
        quick_frame.pack(fill="x", padx=20, pady=(0, 12))

        shortcuts = [
            ("📸 Screenshot", "take a screenshot"),
            ("🌐 YouTube", "open youtube"),
            ("🕒 Time", "what time is it"),
            ("💻 System Info", "system info"),
            ("🧮 Calculator", "open calculator"),
            ("📝 Notepad", "open notepad")
        ]
        for label, cmd in shortcuts:
            b = tk.Button(
                quick_frame,
                text=label,
                font=("Segoe UI", 9),
                bg="#0D1E36",
                fg="#80D8FF",
                activebackground="#005B94",
                activeforeground="#FFFFFF",
                bd=0,
                padx=8,
                pady=3,
                cursor="hand2",
                command=lambda c=cmd: self.process_query(c)
            )
            b.pack(side="left", padx=4)

    def _draw_arc_reactor(self, color):
        self.canvas.delete("all")
        # Outer rings
        self.canvas.create_oval(10, 10, 120, 120, outline=color, width=2)
        self.canvas.create_oval(25, 25, 105, 105, outline=color, width=1)
        # Inner Core
        self.canvas.create_oval(45, 45, 85, 85, fill=color, outline="#FFFFFF", width=2)

    def _on_speaking(self, text):
        self.state_text.config(text="🔊 JARVIS IS SPEAKING...", fg="#00E5FF")
        self._draw_arc_reactor("#00E5FF")

    def _on_idle(self):
        self.state_text.config(text="READY FOR COMMAND", fg="#80D8FF")
        self._draw_arc_reactor("#0091EA")

    def _startup_greet(self):
        self.log_message("SYSTEM", "Jarvis Ultra online. Gemini 2.0 Flash AI core connected and ready.")
        greeting = "Jarvis Ultra online. Ready for your command, Boss."
        self.voice.speak(greeting)

    def log_message(self, sender, message):
        self.chat_log.config(state="normal")
        time_str = datetime.datetime.now().strftime("%H:%M:%S")
        if sender == "USER":
            self.chat_log.insert("end", f"[{time_str}] You: {message}\n", "user")
        elif sender == "JARVIS":
            self.chat_log.insert("end", f"[{time_str}] Jarvis: {message}\n\n", "jarvis")
        else:
            self.chat_log.insert("end", f"[{time_str}] {message}\n", "sys")
        self.chat_log.see("end")
        self.chat_log.config(state="disabled")

    def send_text_command(self):
        cmd = self.entry_var.get().strip()
        if not cmd:
            return
        self.entry_var.set("")
        self.process_query(cmd)

    def trigger_voice_listen(self):
        threading.Thread(target=self._listen_worker, daemon=True).start()

    def _listen_worker(self):
        self.mic_btn.config(bg="#D50000", text="🔴 LISTENING...")
        self.state_text.config(text="🎙️ LISTENING TO YOUR VOICE...", fg="#FF1744")
        self._draw_arc_reactor("#FF1744")

        text = self.voice.listen(timeout=7)

        self.mic_btn.config(bg="#00C853", text="🎤 SPEAK")
        if text:
            self.process_query(text)
        else:
            self.state_text.config(text="NO SPEECH DETECTED", fg="#80D8FF")
            self._draw_arc_reactor("#0091EA")

    def process_query(self, query):
        threading.Thread(target=self._process_worker, args=(query,), daemon=True).start()

    def _process_worker(self, query):
        self.log_message("USER", query)
        self.state_text.config(text="🧠 THINKING...", fg="#FFD600")
        self._draw_arc_reactor("#FFD600")

        # Get response from Brain (Gemini 2.0 or local tools)
        response = self.brain.ask(query)

        self.log_message("JARVIS", response)
        # Speak out loud!
        self.voice.speak(response)


if __name__ == "__main__":
    root = tk.Tk()
    app = JarvisUltraApp(root)
    root.mainloop()
