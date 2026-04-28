import customtkinter as ctk
import tkinter as tk
from tkinter import scrolledtext
import threading
from assistant import VoiceAssistant

class LyraGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("LyraVerse")
        self.geometry("900x650")
        self.configure(fg_color="#0B0B0D")
        self.typing_queue = []
        self.is_typing = False
        
        self.head = ctk.CTkFrame(self, fg_color="#141417", height=70, corner_radius=0)
        self.head.pack(fill="x")
        
        self.status_light = tk.Canvas(self.head, width=15, height=15, bg="#141417", highlightthickness=0)
        self.status_light.place(x=30, y=28)
        self.led = self.status_light.create_oval(2, 2, 13, 13, fill="#00FFCC")

        self.status_lbl = ctk.CTkLabel(self.head, text="INITIALIZING...", font=("Consolas", 14, "bold"), text_color="#00FFCC")
        self.status_lbl.place(x=60, y=24)

        self.chat_display = scrolledtext.ScrolledText(
            self, bg="#0B0B0D", fg="#E0E0E0", font=("Helvetica", 13),
            padx=35, pady=35, borderwidth=0, highlightthickness=0, state="disabled", wrap="word"
        )
        self.chat_display.pack(fill="both", expand=True)
        self.chat_display.tag_config("user", foreground="#00FFCC", font=("Helvetica", 13, "bold"))
        self.chat_display.tag_config("lyra", foreground="#FF007A", font=("Helvetica", 13, "bold"))
        self.chat_display.tag_config("lyra_text", foreground="#E0E0E0")

        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.pack(fill="x", side="bottom", padx=30, pady=25)
        
        self.entry = ctk.CTkEntry(
            self.input_frame, 
            placeholder_text="Type a message or speak...", 
            height=50, 
            fg_color="#141417", 
            border_color="#333",
            font=("Helvetica", 13)
        )
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 15))
        self.entry.bind("<Return>", lambda e: self.manual_input())

        self.lyra = VoiceAssistant(
            ui_callback=self.thread_safe_add_message, 
            status_callback=self.thread_safe_update_status
        )
        threading.Thread(target=self.lyra.run, daemon=True).start()

    def thread_safe_update_status(self, msg):
        self.after(0, self.update_status, msg)

    def thread_safe_add_message(self, text, is_user):
        self.after(0, self.add_message, text, is_user)

    def update_status(self, msg):
        colors = {
            "Online": "#00FFCC", 
            "Listening...": "#FFD700", 
            "Thinking...": "#FF007A", 
            "Speaking...": "#00CCFF",
            "Calibrating...": "#FFA500",
            "Audio Offline - Text Only": "#FF4444"
        }
        color = colors.get(msg, "#00FFCC")
        self.status_lbl.configure(text=msg.upper(), text_color=color)
        self.status_light.itemconfig(self.led, fill=color)

    def add_message(self, text, is_user=False):
        self.chat_display.configure(state="normal")
        if is_user:
            self.chat_display.insert("end", f"▶ {text}\n\n", "user")
            self.chat_display.configure(state="disabled")
            self.chat_display.see("end")
        else:
            name, content = text.split(": ", 1)
            self.chat_display.insert("end", f"✨ {name}\n", "lyra")
            self.chat_display.configure(state="disabled")

            self.typing_queue.extend(list(content + "\n\n"))
            if not self.is_typing:
                self.is_typing = True
                self._process_typing_queue()

    def _process_typing_queue(self):
        """FIFO Queue processor to prevent text jumbling from rapid API responses."""
        if self.typing_queue:
            char = self.typing_queue.pop(0)
            self.chat_display.configure(state="normal")
            self.chat_display.insert("end", char, "lyra_text")
            self.chat_display.configure(state="disabled")
            self.chat_display.see("end")

            delay = 10 if char not in [".", "?", "!"] else 150
            self.after(delay, self._process_typing_queue)
        else:
            self.is_typing = False

    def manual_input(self):
        txt = self.entry.get().strip()
        if txt:
            self.entry.delete(0, 'end')
            self.add_message(f"You: {txt}", is_user=True)
            threading.Thread(target=self.lyra.process_command, args=(txt,), daemon=True).start()

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    app = LyraGUI()
    app.mainloop()