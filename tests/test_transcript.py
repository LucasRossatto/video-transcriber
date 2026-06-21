"""Testes para o módulo transcript."""

import pytest

from transcribe_video.transcript import extract_video_id, _join_entries


class TestExtractVideoId:
    def test_url_padrao(self):
        assert extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_url_curta(self):
        assert extract_video_id("https://youtu.be/dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_url_com_parametros_extras(self):
        assert extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=42s") == "dQw4w9WgXcQ"

    def test_url_invalida(self):
        with pytest.raises(ValueError, match="Não foi possível extrair"):
            extract_video_id("https://exemplo.com/video")


class TestJoinEntries:
    def test_junta_entradas(self):
        entries = [{"text": "Olá"}, {"text": "mundo"}]
        assert _join_entries(entries) == "Olá mundo"

    def test_ignora_entradas_vazias(self):
        entries = [{"text": "Olá"}, {"text": ""}, {"text": "mundo"}]
        assert _join_entries(entries) == "Olá mundo"

    def test_lista_vazia(self):
        assert _join_entries([]) == ""
