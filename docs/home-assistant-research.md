# Building an Alexa/Google Home Replacement

**Research Overview from the `home-assistant` Project**

---

## Executive Summary

The `home-assistant` project demonstrates a fully functional voice assistant that replaces Alexa or Google Home with open, swappable components. The architecture is intentionally modular: wake word detection, speech-to-text, LLM processing with tools, and text-to-speech are each separate modules that can be replaced independently.

**Key advantages over commercial assistants:**
- **Model agnostic** - Swap GPT-4o for Claude, Ollama, or any LLM
- **Tool extensibility** - Add new capabilities with a single Pydantic model
- **Privacy** - All processing can run locally (with the right model choices)
- **No vendor lock-in** - Each component is replaceable

---

## Architecture Overview

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Microphone │────▶│ Wake Word    │────▶│ Record      │
│             │     │ (openWakeWord)│    │ Until Silence│
└─────────────┘     └──────────────┘     └──────┬──────┘
                                                 │
                                                 ▼
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Speaker   │◀────│ TTS          │◀────│ LLM + Tools │
│             │     │ (OpenAI)     │     │ (GPT-4o)    │
└─────────────┘     └──────────────┘     └──────┬──────┘
                                                 │
                                                 ▼
                                          ┌─────────────┐
                                          │ Whisper STT │
                                          └─────────────┘
```

| Component | Current Implementation | Alternatives |
|-----------|----------------------|--------------|
| Wake Word | openWakeWord | Porcupine, Snowboy, Mycroft Precise |
| Speech-to-Text | OpenAI Whisper API | Whisper.cpp (local), Vosk, DeepSpeech |
| LLM | OpenAI GPT-4o | Claude, Ollama, LM Studio, vLLM |
| Text-to-Speech | OpenAI TTS | Piper, Coqui TTS, ElevenLabs |

---

## Wake Word Detection

Wake word detection runs continuously, listening for a trigger phrase before activating the full pipeline.

### Implementation: openWakeWord

**File:** `wake_word.py`

```python
from openwakeword.model import Model

class WakeWordDetector:
    def __init__(self, model_name: str = "hey_jarvis", threshold: float = 0.5):
        self.model = Model(wakeword_models=[model_name])
        self.threshold = threshold

    def detect(self, audio: np.ndarray) -> bool:
        prediction = self.model.predict(audio.flatten())
        for name, score in prediction.items():
            if score >= self.threshold:
                return True
        return False
```

**Pre-trained models available:**
- `hey_jarvis` (default)
- `alexa`
- `hey_mycroft`
- `hey_rhasspy`

**Audio requirements:**
- 16 kHz sample rate
- 16-bit PCM mono
- ~80ms chunks (1280 samples)

### Alternative Wake Word Systems

| Library | Licensing | Local/Cloud | Custom Wake Words |
|---------|-----------|-------------|-------------------|
| **openWakeWord** | Apache 2.0 | Local | Yes (train your own) |
| **Porcupine** | Free tier / Commercial | Local | Yes (via console) |
| **Snowboy** | Apache 2.0 (deprecated) | Local | Yes |
| **Mycroft Precise** | Apache 2.0 | Local | Yes |

**Recommendation:** openWakeWord is the best open-source choice. Fully local, Apache licensed, and supports custom wake word training.

---

## Speech-to-Text (Transcription)

After wake word detection, audio is recorded until silence, then transcribed.

### Voice Activity Detection (VAD)

**File:** `audio.py`

Uses WebRTC VAD to detect when the user stops speaking:

```python
import webrtcvad

def record_until_silence(
    stream: AudioStream,
    vad: webrtcvad.Vad,
    silence_duration: float = 0.5,
    max_duration: float = 30.0,
) -> bytes:
    """Record until silence_duration seconds of silence."""
    frames = []
    silent_frames = 0
    max_silent_frames = int(silence_duration * 1000 / FRAME_DURATION_MS)

    for _ in range(max_frames):
        audio = stream.read(timeout=1.0)
        frame_bytes = audio.flatten().tobytes()
        frames.append(frame_bytes)

        if vad.is_speech(frame_bytes, SAMPLE_RATE):
            silent_frames = 0
        else:
            silent_frames += 1

        if silent_frames >= max_silent_frames:
            break

    return b"".join(frames)
```

### Transcription with Whisper

**File:** `transcribe.py`

```python
from openai import OpenAI

def transcribe(client: OpenAI, audio_buffer: io.BytesIO) -> str:
    response = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_buffer,
    )
    return response.text
```

### Alternative STT Options

| Service | Latency | Cost | Local/Cloud | Quality |
|---------|---------|------|-------------|---------|
| **OpenAI Whisper API** | ~1-2s | $0.006/min | Cloud | Excellent |
| **Whisper.cpp** | ~0.5-3s | Free | Local | Excellent |
| **Faster Whisper** | ~0.3-1s | Free | Local (GPU) | Excellent |
| **Vosk** | ~0.1s | Free | Local | Good |
| **DeepSpeech** | ~0.5s | Free | Local | Good |

**For local operation:** Use `whisper.cpp` or `faster-whisper` with a local model. The `tiny` or `base` models work well for voice commands with minimal latency.

**Example local Whisper integration:**
```python
from faster_whisper import WhisperModel

model = WhisperModel("base", device="cpu", compute_type="int8")

def transcribe_local(audio_path: str) -> str:
    segments, _ = model.transcribe(audio_path)
    return " ".join(segment.text for segment in segments)
```

---

## LLM Integration with Tools

The core of the assistant is the LLM conversation loop with tool/function calling support.

### Conversation Engine

**File:** `assistant.py`

```python
from openai import OpenAI
from tools import TOOLS, execute_tool

SYSTEM_PROMPT = """
You are a helpful voice assistant.

## Response Style
- Keep responses concise and conversational
- Responses will be spoken aloud, so avoid markdown

## Input Context
You receive transcribed speech. Transcriptions may contain:
- Phonetic errors (words that sound similar)
- Missing or extra words
- Misheard proper nouns

Be tolerant of these errors and focus on understanding intent.

## Current Time
{timestamp}
"""

def process_message(client: OpenAI, user_message: str, model: str = "gpt-4o"):
    messages = [
        {"role": "system", "content": get_system_prompt()},
        {"role": "user", "content": user_message},
    ]

    while True:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=TOOLS,  # Registered tools
        )

        message = response.choices[0].message

        # No tool calls - return final response
        if not message.tool_calls:
            return message.content

        # Execute tools and continue loop
        for tool_call in message.tool_calls:
            result = execute_tool(tool_call.function.name,
                                  json.loads(tool_call.function.arguments))
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            })
```

### Swapping LLM Providers

The architecture supports any LLM with function/tool calling:

**Claude (Anthropic):**
```python
from anthropic import Anthropic

client = Anthropic()
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    messages=messages,
    tools=convert_to_anthropic_format(TOOLS),
)
```

**Ollama (Local):**
```python
import ollama

response = ollama.chat(
    model="llama3.2",
    messages=messages,
    tools=TOOLS,  # Ollama supports OpenAI tool format
)
```

**LM Studio / vLLM:**
```python
# Compatible with OpenAI SDK - just change base_url
client = OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed")
```

---

## Tool Framework

The tool system uses a single Pydantic model as the source of truth for both CLI and LLM function schemas.

### Core Framework

**File:** `tools/base.py`

```python
from pydantic import BaseModel
from openai import pydantic_function_tool

_TOOLS: list = []
_HANDLERS: dict[str, tuple[type[BaseModel], Callable]] = {}

def tool(model: type[T]):
    """Decorator to register a tool."""
    def decorator(func):
        _TOOLS.append(pydantic_function_tool(model))
        _HANDLERS[model.__name__] = (model, func)
        return func
    return decorator

def execute_tool(name: str, args: dict) -> str:
    """Execute a registered tool by name."""
    model_class, handler = _HANDLERS[name]
    params = model_class(**args)
    return handler(params)

def get_tools() -> list:
    """Get all tools in OpenAI format."""
    return _TOOLS
```

### Creating a New Tool

**Example: Weather Tool** (`tools/weather.py`)

```python
from pydantic import BaseModel, Field

class GetWeather(BaseModel):
    """Get the current weather for a location."""

    location: str | None = Field(
        default=None,
        description="City name (optional, defaults to current location)"
    )

def get_weather(params: GetWeather) -> str:
    # Fetch weather data...
    return f"In {location}, it's currently {temp}°F with {condition}."

# Register for LLM use (when imported)
from tools.base import tool
tool(GetWeather)(get_weather)
```

**The Pydantic model provides:**
1. **LLM function schema** - Via `pydantic_function_tool()`
2. **CLI arguments** - Required fields = positional, optional = flags
3. **Documentation** - Docstring becomes function description
4. **Validation** - Type checking and constraints

### Available Tools

| Tool | Description | API/Service |
|------|-------------|-------------|
| `GetWeather` | Current weather by location | Open-Meteo (free) |
| `GetNews` | Latest headlines | BBC News API |
| `SearchInternet` | Web search | Perplexity API |
| `GetHistory` | Past conversation lookup | Local SQLite |
| `GetDeviceVolume` / `SetDeviceVolume` | System volume | macOS AppleScript |
| `PlayMusic` | Play track/artist/album | Spotify API |
| `PauseMusic` / `ResumeMusic` / `SkipTrack` | Playback control | Spotify API |
| `SetMusicVolume` | Media volume | Spotify API |
| `GetPlaybackStatus` | What's playing | Spotify API |

### Adding Smart Home Tools

The pattern makes it trivial to add Home Assistant, Hue, or other integrations:

```python
class ControlLight(BaseModel):
    """Turn a light on or off."""

    room: str = Field(description="Room name (e.g., 'living room', 'bedroom')")
    state: bool = Field(description="True for on, False for off")
    brightness: int | None = Field(default=None, ge=0, le=100)

def control_light(params: ControlLight) -> str:
    # Call Home Assistant API, Hue bridge, etc.
    response = requests.post(f"{HA_URL}/api/services/light/turn_{'on' if params.state else 'off'}",
                            json={"entity_id": f"light.{params.room}"})
    return f"Turned {params.room} light {'on' if params.state else 'off'}"

tool(ControlLight)(control_light)
```

---

## Text-to-Speech

The final step speaks the LLM's response.

### OpenAI TTS

**File:** `tts.py`

```python
from openai import OpenAI

VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

def speak(client: OpenAI, text: str, voice: str = "alloy") -> None:
    response = client.audio.speech.create(
        model="tts-1",
        voice=voice,
        input=text,
        response_format="pcm",
    )
    play_audio(response.content)
```

### Alternative TTS Options

| Service | Quality | Latency | Cost | Local/Cloud |
|---------|---------|---------|------|-------------|
| **OpenAI TTS** | Excellent | ~0.5s | $0.015/1K chars | Cloud |
| **ElevenLabs** | Excellent | ~0.3s | $0.30/1K chars | Cloud |
| **Piper** | Good | ~0.1s | Free | Local |
| **Coqui TTS** | Good | ~0.2s | Free | Local |
| **edge-tts** | Good | ~0.3s | Free | Cloud (Edge) |

**For local operation:** Piper is the best choice - fast, high quality, and fully offline.

```python
# Piper TTS example
import subprocess

def speak_local(text: str, model: str = "en_US-lessac-medium"):
    subprocess.run(
        f'echo "{text}" | piper --model {model} --output_file - | aplay',
        shell=True
    )
```

---

## Running the Assistant

### Installation

```bash
# Clone and install
cd home-assistant
uv sync

# Download wake word models
uv run python -c "from openwakeword import utils; utils.download_models()"

# Configure
cp .env.example .env
# Edit .env with your OPENAI_API_KEY
```

### Usage Modes

```bash
# Voice mode (wake word + TTS)
uv run assistant

# Interactive text mode (no audio)
uv run assistant --repl

# One-shot query
uv run assistant "what's the weather in Tokyo"
```

### Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | *required* | API key |
| `WAKE_WORD` | `hey_jarvis` | Wake word model |
| `MODEL` | `gpt-4o` | LLM model |
| `TTS_VOICE` | `alloy` | TTS voice |
| `SILENCE_THRESHOLD` | `0.5` | Seconds of silence to stop |

---

## Full Local Setup

For a completely local, privacy-preserving assistant:

| Component | Cloud Version | Local Replacement |
|-----------|---------------|-------------------|
| Wake Word | openWakeWord | openWakeWord (already local) |
| STT | Whisper API | faster-whisper / whisper.cpp |
| LLM | GPT-4o | Ollama + Llama 3.2 / Mistral |
| TTS | OpenAI TTS | Piper |

**Local LLM with Ollama:**

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model with tool support
ollama pull llama3.2

# Update .env
MODEL=llama3.2
OPENAI_BASE_URL=http://localhost:11434/v1
```

**Performance considerations:**
- Wake word: Runs on CPU, ~5% usage
- STT: CPU works, GPU preferred for speed
- LLM: GPU strongly recommended (or cloud)
- TTS: CPU works fine for most models

---

## Comparison with Commercial Assistants

| Feature | Alexa | Google | This Project |
|---------|-------|--------|--------------|
| Wake word customization | Limited | No | Full |
| LLM choice | Alexa AI | Gemini | Any |
| Tool/skill creation | Complex | Complex | Simple Python |
| Privacy | Cloud | Cloud | Can be local |
| Latency | ~1-2s | ~1-2s | ~1-3s |
| Cost | Free (device) | Free (device) | API costs |
| Offline mode | Limited | Limited | Full (with local stack) |

---

## Summary

The `home-assistant` project provides a production-ready foundation for building an Alexa/Google Home replacement:

1. **Wake Words** - openWakeWord with 4 pre-trained models, custom training support
2. **Transcription** - Whisper API (swap to whisper.cpp for local)
3. **LLM + Tools** - OpenAI function calling with elegant Pydantic-based tool framework
4. **TTS** - OpenAI voices (swap to Piper for local)

**Key insight:** The Pydantic tool pattern is the standout feature. A single model definition provides:
- CLI interface for testing
- OpenAI function schema for the LLM
- Type validation and documentation

Adding new capabilities (lights, thermostats, calendars, reminders) is just a matter of defining a Pydantic model and handler function.
