"""Testes para o módulo translator."""

from transcribe_video.translator import _split_text


class TestSplitText:
    def test_texto_curto_nao_divide(self):
        text = "Hello world"
        chunks = _split_text(text, max_length=100)
        assert chunks == ["Hello world"]

    def test_divide_em_chunks(self):
        text = "a " * 50  # 100 chars
        chunks = _split_text(text.strip(), max_length=20)
        assert len(chunks) > 1
        assert all(len(c) <= 22 for c in chunks)  # margem de 1 palavra

    def test_texto_vazio(self):
        assert _split_text("", max_length=100) == []

    def test_reconstroi_texto_completo(self):
        text = "palavra " * 100
        chunks = _split_text(text.strip(), max_length=50)
        reconstruido = " ".join(chunks)
        assert reconstruido == text.strip()
