---
description: Transcrever podcast bruto via ElevenLabs Scribe (texto + diarização speaker_id). Output em edit/transcripts/<source>.json
argument-hint: <video_path> [project_slug]
---

Transcrever o vídeo `$1` usando ElevenLabs Scribe (skill video-use) e salvar em `edit/transcripts/<basename>.json`.

Passos:
1. Verificar que `$ELEVENLABS_API_KEY` está no ambiente. Se não, parar e pedir ao user.
2. Determinar projeto raiz:
   - Se `$2` foi passado: `~/Movies/NOMAX-podcasts/$2/`
   - Senão: derivar do basename do vídeo e usar `~/Movies/NOMAX-podcasts/$(date +%Y-%m-%d)_<basename>/`
3. Criar estrutura `edit/{transcripts,sources,clips,inspect,work,overlays}`.
4. Invocar a skill `video-use` para fazer a transcrição com Scribe (`include_diarization=true`, `language=pt`).
5. Salvar output em `edit/transcripts/<basename>.json`.
6. Reportar: quantos speakers detectados (Scribe `speaker_id`), duração total, e onde foi salvo o JSON.

Hard rules:
- Use ElevenLabs Scribe (não Whisper) para o texto principal. Scribe acerta português e faz diarização nativa.
- Whisper pode ser rodado em paralelo para timing word-level acurado se a fine cut precisar (`inspect_audio.py` aceita ambos).
- Se a chave não estiver setada, NÃO chutar — parar e instruir o user a `export ELEVENLABS_API_KEY=...`.
