# transcribe-video

CLI para transcrever vídeos do YouTube para arquivos `.txt`. Busca legendas em português automaticamente; se não houver, oferece a opção de buscar em inglês e traduzir para português.

## Requisitos

- Python 3.10+

## Instalação

```bash
pip install -e .
```

## Uso

```bash
transcribe-video <URL_DO_VIDEO>
```

**Exemplos:**

```bash
# Transcreve e salva como <video_id>.txt
transcribe-video "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Salva em arquivo específico
transcribe-video "https://www.youtube.com/watch?v=dQw4w9WgXcQ" -o minha_transcricao.txt

# Não pergunta sobre tradução (mantém em inglês se necessário)
transcribe-video "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --no-translate
```

## Comportamento

1. Busca legenda em português (pt, pt-BR, pt-PT)
2. Se não encontrar, busca em inglês
3. Se a legenda for em inglês, pergunta se deseja traduzir para português
4. Salva o resultado em `.txt`

## Desenvolvimento

```bash
# Instalar com dependências de desenvolvimento
pip install -e ".[dev]"

# Rodar testes
pytest
```
