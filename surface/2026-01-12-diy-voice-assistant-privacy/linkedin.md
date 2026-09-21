"Would you like to try Alexa Plus?"

This happens about 80 times a day now. Amazon turned my Echo from a useful tool into a subscription salesperson.

So I'm building my own voice assistant. The code works, the hardware is on the way, and I wanted to share what I've learned.

The stack:
- openWakeWord (runs 100% locally)
- Whisper for speech-to-text
- Any LLM (GPT-4o, Claude, or Ollama locally)
- Pydantic-based tools for weather, music, smart home

The elegant part? Each tool is just a Python class. Adding Spotify control or smart lights takes 20 lines of code.

It runs on my Mac Mini that already serves as my AI dev server. One machine handles remote coding workflows AND home automation.

No subscription nagging. No upsells. Just a voice assistant that does what you ask.
