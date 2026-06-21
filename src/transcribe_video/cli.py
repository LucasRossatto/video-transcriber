"""Entry point da CLI."""

import argparse
import re
import sys
from pathlib import Path

from transcribe_video.transcript import TranscriptResult, extract_video_id, fetch_transcript
from transcribe_video.translator import translate_to_portuguese


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="transcribe-video",
        description="Transcreve vídeos do YouTube para arquivo .txt",
    )
    parser.add_argument("url", help="URL do vídeo do YouTube")
    parser.add_argument(
        "-o",
        "--output",
        help="Caminho do arquivo de saída (padrão: <video_id>.txt)",
        type=Path,
        default=None,
    )
    parser.add_argument(
        "--no-translate",
        action="store_true",
        help="Não perguntar sobre tradução quando a legenda for em inglês",
    )
    args = parser.parse_args()

    try:
        video_id = extract_video_id(args.url)
    except ValueError as e:
        print(f"Erro: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Buscando legenda para o vídeo {video_id}...")

    try:
        result: TranscriptResult = fetch_transcript(video_id)
    except RuntimeError as e:
        print(f"Erro: {e}", file=sys.stderr)
        sys.exit(1)

    text = result.text

    if result.language == "en" and not args.no_translate:
        resposta = input("Legenda encontrada em inglês. Deseja traduzir para português? [s/N] ")
        if resposta.strip().lower() in ("s", "sim", "y", "yes"):
            print("Traduzindo...")
            text = translate_to_portuguese(text)

    output_path: Path = args.output or Path(f"{video_id}.txt")
    output_path.write_text(text, encoding="utf-8")

    print(f"Transcrição salva em: {output_path.resolve()}")


if __name__ == "__main__":
    main()
