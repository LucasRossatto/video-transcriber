"""Servidor web Flask para a interface de transcrição."""

import io
import sys
from pathlib import Path

from flask import Flask, Response, jsonify, render_template, request

from transcribe_video.transcript import (
    YouTubeAPIError,
    _sanitize_filename,
    convert_text_to_md,
    convert_text_to_srt,
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
    except YouTubeAPIError as e:
        return jsonify({"error": str(e)}), 424
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
    base_name = _sanitize_filename(title)
    final_text = translated_text or original_text

    return jsonify({
        "text": final_text,
        "text_srt": convert_text_to_srt(final_text),
        "text_md": convert_text_to_md(final_text, title=title),
        "original_text": original_text if translated_text else None,
        "original_text_srt": convert_text_to_srt(original_text) if translated_text else None,
        "original_text_md": convert_text_to_md(original_text, title=title) if translated_text else None,
        "translated": translated_text is not None,
        "base_name": base_name,
    })


def main() -> None:
    print("Servidor rodando em http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)


if __name__ == "__main__":
    main()
