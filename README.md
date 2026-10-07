# ai-assistant-api

A small **REST API + web UI** that wraps an OpenAI-compatible LLM. Built with Flask and the Python standard library — no SDK required.

It works with **OpenAI, OpenRouter, Groq, or any `/chat/completions` endpoint**, and runs in **mock mode** out of the box so you can try it without an API key.

## Features

- `POST /api/chat` — send a conversation, get a reply
- `GET /health` — health check
- `GET /` — a minimal chat UI (vanilla JS, no build step)
- **Mock mode** when no API key is set, so tests and demos always work
- Input validation and clear error responses

## Quick start

```bash
git clone https://github.com/jjrc163/ai-assistant-api.git
cd ai-assistant-api
pip install -r requirements.txt

# Optional: connect a real model
export LLM_API_KEY="sk-..."          # or OPENAI_API_KEY
export LLM_BASE_URL="https://api.openai.com/v1"   # optional
export LLM_MODEL="gpt-4o-mini"                    # optional

python app.py
# open http://127.0.0.1:5000
```

## API

```bash
curl -X POST http://127.0.0.1:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Explain REST in one sentence."}]}'
```

```json
{ "reply": "REST is an architectural style ..." }
```

## Project layout

```
ai-assistant-api/
├── app.py              # Flask routes
├── llm.py              # OpenAI-compatible client (+ mock mode)
├── templates/index.html
├── static/style.css
└── tests/test_app.py
```

## Tests

```bash
pip install -r requirements.txt
pytest -q
```

## Design notes

- **No vendor lock-in.** Any OpenAI-compatible endpoint works by changing `LLM_BASE_URL`.
- **Graceful degradation.** Without a key the app still runs, which keeps CI and demos green.
- **Small surface area.** One client class, three routes, validated input.

## License

MIT — see [LICENSE](LICENSE).