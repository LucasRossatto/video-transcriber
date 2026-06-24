"""Tradução de texto usando deep-translator (gratuito, sem API key)."""

import re

from deep_translator import GoogleTranslator

_SEPARATOR = " ||| "
_TIMESTAMP_RE = re.compile(r"^\d{2}:\d{2}:\d{2}$")


def translate_to_portuguese(text: str, source_lang: str = "auto") -> str:
    """
    Traduz texto de qualquer idioma para o português preservando timestamps.
    Extrai só as linhas de texto, traduz em poucos chunks e reconstrói.
    """
    lines = text.split("\n")
    translator = GoogleTranslator(source=source_lang, target="pt")

    # separa índices e textos das linhas não-timestamp
    text_indices: list[int] = []
    text_lines: list[str] = []
    for i, line in enumerate(lines):
        if not _TIMESTAMP_RE.match(line.strip()) and line.strip():
            text_indices.append(i)
            text_lines.append(line.strip())

    # junta tudo com separador e traduz em chunks
    joined = _SEPARATOR.join(text_lines)
    chunks = _split_text(joined, max_length=4500)
    translated_joined = _SEPARATOR.join(
        translator.translate(chunk) for chunk in chunks
    )
    translated_lines = translated_joined.split(_SEPARATOR)

    # reconstrói o texto original substituindo as linhas traduzidas
    if len(translated_lines) == len(text_indices):
        for idx, translated in zip(text_indices, translated_lines):
            lines[idx] = translated.strip()

    return "\n".join(lines)


def _split_text(text: str, max_length: int) -> list[str]:
    """Divide o texto em partes menores respeitando espaços."""
    words = text.split()
    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    for word in words:
        if current_len + len(word) + 1 > max_length:
            chunks.append(" ".join(current))
            current = [word]
            current_len = len(word)
        else:
            current.append(word)
            current_len += len(word) + 1

    if current:
        chunks.append(" ".join(current))

    return chunks
