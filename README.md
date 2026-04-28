# LyraVerse — Your Elegant AI Desktop Companion ✨

LyraVerse is a lightweight, beautiful desktop AI assistant that blends real-time speech recognition, graceful text-to-speech, and a modern GUI to deliver a delightful conversational experience. Built for local desktop use with optional cloud model integration, LyraVerse focuses on polish, responsiveness, and usability.

---

# 🚀 Quick highlights
- Modern, dark-themed GUI with typing animation and status indicators
- Real-time microphone capture + fallback to text-only mode
- Reliable queued TTS (pyttsx3) to avoid overlapping speech
- Compact persistent memory for context-aware conversations
- Built-in utilities: weather, time, open web pages, graceful shutdown
- Extensible AI backend compatible with OpenAI-like chat APIs

---

Table of contents
- [Why LyraVerse?](#why-lyraverse)
- [Features](#features)
- [Install (fast)](#install-fast)
- [Configuration](#configuration)
- [Run](#run)
- [Example usage](#example-usage)
- [Architecture & internals](#architecture--internals)
- [Troubleshooting](#troubleshooting)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)
- [Credits & Links](#Credits--Links)


# Why LyraVerse?
- Designed for clarity and refinement: small, well-organized codebase focused on UX.
- Works offline for TTS and voice capture — uses cloud models only for advanced replies.
- Lightweight and extensible: easy to swap the model backend or add new commands.

---

# Features
- Beautiful, dark UI using CustomTkinter with:
  - Status LED (Online / Listening / Thinking / Speaking)
  - Typewriter-like message animation
  - Smooth user input flow
- Voice-first with fallback: automatic microphone detection; if unavailable, full text-mode remains functional.
- Text-to-Speech with queueing to guarantee non-overlapping audio.
- Persistent, pruned chat memory stored in `lyra_memory.json`.
- Built-in utilities: Weather (OpenWeather), local time, open websites, shutdown.
- Simple logging (`lyra.log`) for debugging.

---

# Install (fast)

1. Clone
```bash
git clone https://github.com/kxnux-builds/LyraVerse.git
cd LyraVerse
```

2. Virtual environment (recommended)
```bash
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
```

3. Install Python deps
```bash
pip install -r requirements.txt
```

Notes:
- If PyAudio fails on Windows, use pipwin:
  ```bash
  pip install pipwin
  pipwin install pyaudio
  ```
- On macOS: `brew install portaudio` then `pip install pyaudio`.
- On Debian/Ubuntu: `sudo apt-get install portaudio19-dev` then `pip install pyaudio`.

---

# Configuration

Create a `.env` file in the project root or export environment variables:

```
GEMINI_API_KEY=<your_model_api_key>
OPENWEATHER_API_KEY=<your_openweather_api_key>
CITY_NAME=Kolkata
```

- GEMINI_API_KEY: used to talk to your generative model (the code expects an OpenAI-like chat API).
- OPENWEATHER_API_KEY: required for weather queries.
- CITY_NAME: default city for weather (optional, defaults to "Kolkata").

Security: Do not commit `.env` to Git. Use OS-level secret storage for production deployments.

---

# Run

Start the GUI and assistant:

```bash
python main.py
```

Behavior:
- On first run the assistant tries to initialize the microphone. If unavailable, Lyra will continue in text-only mode.
- TTS runs in a background thread, so the GUI remains responsive.

---

# Example usage

- Type or speak: "What's the weather?"
  - Lyra uses OpenWeather and replies with current temperature and conditions.
- Type or speak: "What time is it?"
  - Lyra reads the local time.
- Type or speak: "Open YouTube"
  - Lyra launches youtube.com in your default browser.
- Ask anything else and the configured AI model will generate a thoughtful response.

Sample session (typed):
> You: What's the weather today?
> Lyra: In Kolkata, it is currently 28°C with clear sky.

---

# Architecture & internals (concise)

- main.py
  - LyraGUI: CustomTkinter-based UI, status indicator, typewriter effect.
  - Spins a VoiceAssistant and runs its main loop in a daemon thread.

- assistant.py
  - VoiceAssistant: microphone setup (SpeechRecognition), TTS worker (pyttsx3), AI request flow, command routing, memory persistence, logging.
  - Memory trimming: keeps system prompt + last 10 messages.
  - AI integration: expects chat-style responses at `response.choices[0].message.content`.

Data flow:
User (voice/text) → VoiceAssistant.listen/process_command → built-ins or ask_ai → TTS queue & UI updates → memory saved.

---

# Extending LyraVerse
- Add new commands: extend process_command with custom triggers.
- Swap model backend: replace ai_client initialization and response parsing in ask_ai.
- Add settings panel: a small GUI panel for API keys, voice selection, and preferences.

---

# Best practices & tips
- Keep your system prompt (first memory element) concise but purpose-specific.
- Limit chat_history size to avoid long payloads to the model — the code already prunes history.
- Use environment-based configs for keys in CI or multi-machine setups.

---

# Troubleshooting

Microphone issues:
- Check system privacy settings to allow microphone access.
- Run a basic microphone test using the `arecord`/`sox` or platform tools.

PyAudio install errors:
- Windows: use pipwin to install the wheel matching your Python version.
- macOS: ensure PortAudio is installed via Homebrew.
- Linux: install portaudio dev packages via apt/yum before pip installing PyAudio.

Model/API errors:
- Confirm GEMINI_API_KEY is set and valid for the base URL used in the code.
- Check `lyra.log` for full stack traces and error details.

---

# Roadmap (short)
- [ ] Settings UI for runtime configuration (voices, API keys)
- [ ] Plugin system for adding new utilities (calendar, email)
- [ ] Local LLM support fallback (for offline responses)
- [ ] Unit/integration tests and CI workflow

Have ideas? Open an issue or PR — I'm building this with developer ergonomics in mind.

---

# Contributing
1. Fork the repo
2. Create a feature branch: `git checkout -b feat/awesome-feature`
3. Commit your changes: `git commit -m "feat: add awesome feature"`
4. Push & open a PR

Please keep secrets out of commits and provide clear PR descriptions and screenshots when applicable.

---

# License

LyraVerse is provided under the terms of the LICENSE file in this repository.

Core libraries and acknowledgements:
- SpeechRecognition
- pyttsx3
- CustomTkinter
- OpenAI-style client (used as a pattern for generative model integration)
- OpenWeatherMap (weather data)

---

# Credits & Links

- Author: Kishanu Mondal
- GitHub: https://github.com/kxnux-builds
- LinkedIn: https://www.linkedin.com/in/kishanu-mondal/
- X (Twitter): https://x.com/Kxnux_Dev

---