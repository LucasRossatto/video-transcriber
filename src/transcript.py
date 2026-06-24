"""Busca e formatação de legendas do YouTube."""

import json
import re
import urllib.request
from dataclasses import dataclass

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    AgeRestricted,
    IpBlocked,
    NoTranscriptFound,
    RequestBlocked,
    TranscriptsDisabled,
    VideoUnavailable,
    VideoUnplayable,
    YouTubeRequestFailed,
)

_api = YouTubeTranscriptApi()


class YouTubeAPIError(Exception):
    """Erro originado pela API do YouTube (bloqueio, vídeo indisponível, falha de rede)."""


@dataclass
class TranscriptResult:
    text: str
    language: str
    video_id: str


def fetch_video_title(video_id: str) -> str:
    """Busca o título do vídeo via oEmbed (sem API key)."""
    oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
    try:
        with urllib.request.urlopen(oembed_url, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            return data.get("title") or video_id
    except Exception:
        return video_id


def _sanitize_filename(name: str) -> str:
    """Remove caracteres inválidos para nomes de arquivo."""
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    name = name.strip(". ")
    return name or "transcript"


def extract_video_id(url: str) -> str:
    """Extrai o ID do vídeo a partir de uma URL do YouTube."""
    patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11}).*",
        r"(?:youtu\.be\/)([0-9A-Za-z_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError(f"Não foi possível extrair o ID do vídeo da URL: {url}")


def fetch_transcript(video_id: str) -> TranscriptResult:
    """
    Busca a legenda do vídeo priorizando PT, depois EN, depois qualquer idioma disponível.
    """
    try:
        transcript_list = _api.list(video_id)
    except TranscriptsDisabled:
        raise RuntimeError("Este vídeo não possui legendas disponíveis.")
    except VideoUnavailable:
        raise YouTubeAPIError("O vídeo não está disponível ou foi removido.")
    except VideoUnplayable:
        raise YouTubeAPIError("O vídeo não pode ser reproduzido.")
    except AgeRestricted:
        raise YouTubeAPIError("O vídeo possui restrição de idade.")
    except IpBlocked:
        raise YouTubeAPIError("O acesso foi bloqueado pelo YouTube. Tente novamente mais tarde.")
    except RequestBlocked:
        raise YouTubeAPIError("A requisição foi bloqueada pelo YouTube. Tente novamente mais tarde.")
    except YouTubeRequestFailed as e:
        raise YouTubeAPIError(f"Falha na requisição ao YouTube: {e}")

    for lang in ("pt", "pt-BR", "pt-PT", "en"):
        try:
            transcript = transcript_list.find_transcript([lang])
            entries = transcript.fetch()
            return TranscriptResult(
                text=_join_entries(entries),
                language=lang,
                video_id=video_id,
            )
        except NoTranscriptFound:
            continue

    # fallback: qualquer legenda disponível
    try:
        transcript = next(iter(transcript_list))
        entries = transcript.fetch()
        return TranscriptResult(
            text=_join_entries(entries),
            language=transcript.language_code,
            video_id=video_id,
        )
    except StopIteration:
        pass

    raise RuntimeError("Nenhuma legenda disponível para este vídeo.")


def convert_text_to_srt(text: str) -> str:
    """Converte o formato interno (HH:MM:SS\ntexto) para SRT."""
    lines = text.split("\n")
    blocks = []
    i = 0
    index = 1
    while i < len(lines):
        line = lines[i].strip()
        if re.match(r"^\d{2}:\d{2}:\d{2}$", line) and i + 1 < len(lines):
            start_ts = line.replace(":", ":", 2)
            end_ts = lines[i + 2].strip() if i + 2 < len(lines) and re.match(r"^\d{2}:\d{2}:\d{2}$", lines[i + 2].strip()) else _add_seconds(start_ts, 3)
            content = lines[i + 1].strip()
            blocks.append(f"{index}\n{start_ts},000 --> {end_ts},000\n{content}\n")
            index += 1
            i += 2
        else:
            i += 1
    return "\n".join(blocks)


def convert_text_to_md(text: str, title: str = "") -> str:
    """Converte o formato interno (HH:MM:SS\ntexto) para Markdown."""
    lines = text.split("\n")
    parts = [f"# {title}\n" if title else "# Transcrição\n"]
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if re.match(r"^\d{2}:\d{2}:\d{2}$", line) and i + 1 < len(lines):
            content = lines[i + 1].strip()
            parts.append(f"**`{line}`** {content}\n")
            i += 2
        else:
            i += 1
    return "\n".join(parts)


def _add_seconds(timestamp: str, seconds: int) -> str:
    h, m, s = map(int, timestamp.split(":"))
    total = h * 3600 + m * 60 + s + seconds
    h2, r = divmod(total, 3600)
    m2, s2 = divmod(r, 60)
    return f"{h2:02d}:{m2:02d}:{s2:02d}"


def _join_entries(entries) -> str:
    """Formata as entradas da legenda com timestamps."""
    lines = []
    for snippet in entries:
        if not snippet.text:
            continue
        total = int(snippet.start)
        h, remainder = divmod(total, 3600)
        m, s = divmod(remainder, 60)
        timestamp = f"{h:02d}:{m:02d}:{s:02d}" if h else f"00:{m:02d}:{s:02d}"
        lines.append(f"{timestamp}\n{snippet.text.strip()}")
    return "\n".join(lines)
