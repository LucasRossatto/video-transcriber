"""Servidor web Flask para a interface de transcrição."""

import io
import sys
from pathlib import Path

from flask import Flask, Response, jsonify, render_template, request

from transcribe_video.transcript import (
    _sanitize_filename,
    extract_video_id,
    fetch_transcript,
    fetch_video_title,
)
from transcribe_video.translator import translate_to_portuguese

app = Flask(__name__, template_folder="templates")


@app.route("/")
def index() -> str:
    return render_template("index.html")


@app.route("/transcribe", methods=["POST"])
def transcribe() -> Response:
    data = request.get_json(force=True)
    url: str = (data.get("url") or "").strip()
    should_translate: bool = bool(data.get("translate", False))

    if not url:
        return jsonify({"error": "URL não informada."}), 400

    try:
        video_id = extract_video_id(url)
    except ValueError:
        return jsonify({"error": "URL do YouTube inválida."}), 400

    try:
        result = fetch_transcript(video_id)
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 422

    original_text = result.text
    translated_text = None

    if should_translate and not result.language.startswith("pt"):
        try:
            translated_text = translate_to_portuguese(original_text, source_lang=result.language)
        except Exception:
            return jsonify({"error": "Falha ao traduzir a transcrição."}), 500

    title = fetch_video_title(video_id)
    filename = f"{_sanitize_filename(title)}.txt"
    return jsonify({
        "text": translated_text or original_text,
        "original_text": original_text if translated_text else None,
        "translated": translated_text is not None,
        "filename": filename,
    })


def main() -> None:
    print("Servidor rodando em http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)


if __name__ == "__main__":
    main()
