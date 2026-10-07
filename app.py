"""A small REST API + web UI that wraps an OpenAI-compatible LLM.

Endpoints:
    GET  /            -> chat UI
    GET  /health      -> {"status": "ok", "mock_mode": bool}
    POST /api/chat    -> {"reply": "..."}  body: {"messages": [{"role","content"}]}
"""
from __future__ import annotations

from flask import Flask, jsonify, render_template, request

from llm import LLMClient, LLMError

app = Flask(__name__)
client = LLMClient()

MAX_MESSAGES = 40
MAX_CHARS = 8000


def _validate(messages: object) -> list[dict[str, str]]:
    if not isinstance(messages, list) or not messages:
        raise ValueError("'messages' must be a non-empty list.")
    if len(messages) > MAX_MESSAGES:
        raise ValueError(f"Too many messages (max {MAX_MESSAGES}).")

    cleaned: list[dict[str, str]] = []
    for item in messages:
        if not isinstance(item, dict):
            raise ValueError("Each message must be an object.")
        role = item.get("role")
        content = item.get("content")
        if role not in {"system", "user", "assistant"}:
            raise ValueError(f"Invalid role: {role!r}")
        if not isinstance(content, str) or not content.strip():
            raise ValueError("Each message needs non-empty 'content'.")
        cleaned.append({"role": role, "content": content[:MAX_CHARS]})
    return cleaned


@app.get("/")
def index():
    return render_template("index.html", mock_mode=client.mock_mode, model=client.model)


@app.get("/health")
def health():
    return jsonify({"status": "ok", "mock_mode": client.mock_mode, "model": client.model})


@app.post("/api/chat")
def chat():
    data = request.get_json(silent=True) or {}
    try:
        messages = _validate(data.get("messages"))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    try:
        reply = client.chat(messages)
    except LLMError as exc:
        return jsonify({"error": str(exc)}), 502

    return jsonify({"reply": reply, "mock_mode": client.mock_mode})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)