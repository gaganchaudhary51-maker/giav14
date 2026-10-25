# Local GIA model setup (Windows)

GIA uses its existing conversation endpoint and an OpenAI-compatible local Ollama endpoint. This adds no separate calling agent and does not require a cloud model API key.

## Recommended profile for this laptop

The inspected machine has 8 GB RAM. Use the smaller Qwen3 1.7B model instead of the 4B profile to reduce memory pressure:

| Setting | Value |
| --- | --- |
| API URL | `http://127.0.0.1:11434/v1` |
| Model | `qwen3:1.7b` |
| API key field | `ollama` (local compatibility placeholder; not a secret) |
| Model download | about 1.4 GB |

Ollama serves OpenAI-compatible chat completions on loopback. After installing Ollama for Windows and starting it, run:

```powershell
ollama pull qwen3:1.7b
```

The next GIA desktop build will prefill this profile on first run. If changing an existing setup, open GIA's **Configure provider** dialog, choose **Use local Ollama**, and save. GIA's chat prompts are sent to `127.0.0.1`; the local model request does not go to a hosted LLM API. Close memory-heavy apps if Ollama reports insufficient memory or responds slowly.

The 1.7B model is a small local model and will not match a large hosted GPT model on complex tasks. Laptop speech recognition currently uses browser `SpeechRecognition`; that audio path can use a remote recognition service and is not guaranteed to stay local. Do not use voice input for sensitive audio until a local speech-recognition runtime is configured.
