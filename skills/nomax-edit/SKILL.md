---
name: nomax-edit
description: NÔMAX podcast clip production pipeline (rough + fine cut). Cut, reframe 9:16/16:9, surgical stutter removal, speaker-follow multi-cam, color grade, loudnorm broadcast-grade. Use when the user mentions "corte de podcast", "editar clipe", "podcast clip", "Bureau Social", "rough cut", "fine cut", or references this pipeline. Pairs with clip-selector (curatorial) and video-use (transcribe + render canonical).
---

# nomax-edit — Pipeline NÔMAX de produção de cortes

Sistema completo de produção de podcast clips, do bruto ao final aprovado. Foco em rough cut + fine cut. Captions kinéticas ficam fora do escopo desta skill (decisão: investir tempo em referência antes de automatizar — ver `docs/captions-deferred.md` do plugin).

## Quando usar

Quando o trabalho envolve:
- Cortar segmentos de podcast bruto pra social (9:16) ou VSL (16:9)
- Trim de silêncios + cortes cirúrgicos de stutters
- Reframe seguindo locutor (multi-speaker)
- Color grade automático + loudnorm broadcast-grade -14 LUFS

## Pipeline (8 camadas, sem captions)

```
1. Inventário ffprobe → metadata do bruto
2. Transcrição Scribe (texto + diarização speaker_id por palavra)
3. Seleção via clip-selector (Hook+Payload + 4-eixos)
4. Pré-processo: cut + reframe 9:16 ou keep 16:9
5. silence_trim.py: silences auto + extra-cuts cirúrgicos + drop-tokens
6. EDL declarativa (sources, ranges, grade, fps) — multi-source pra speaker-follow
7. render_local.py (extract → concat → loudnorm -14 LUFS)
8. Verificação: ffprobe + verify_playback (contact sheet) + inspect_audio (seam check)
```

## Tools

| Script | Função |
|---|---|
| `scripts/inspect_audio.py` | Waveform + silencedetect + Scribe/Whisper divergência → user lê timestamps exatos |
| `scripts/verify_playback.py` | Contact sheet de N frames distribuídos pra "assistir" o clipe |
| `scripts/silence_trim.py` | Cuts de silêncio + extra-cut surgical (stutters) + drop-token (fillers) |
| `scripts/render_local.py` | Fork local de video-use render.py com fps configurável via EDL + multi-source ranges |
| `scripts/grade.py` | Auto color grade matemático bounded ±8% |

## Project layout esperado

```
~/Movies/NOMAX-podcasts/YYYY-MM-DD_<slug>/
├── <SOURCE>.MP4 (symlink ao bruto)
└── edit/
    ├── transcripts/
    │   ├── <source>.json           ← Scribe
    │   └── whisper_<clip>.json     ← Whisper word-level (opcional, fine cut)
    ├── sources/
    │   ├── <clip>.mp4              ← speaker A reframe
    │   └── <clip>_<speakerB>.mp4   ← speaker B reframe (multi-cam)
    ├── clip_candidates.json        ← do clip-selector
    ├── <clip>_edl.json             ← declarativa
    ├── work/                       ← scripts + intermediários
    ├── inspect/<clip>/             ← dossiers do inspect_audio
    └── clips/
        └── <clip>_gold.mp4         ← output final
```

## SOPs obrigatórios

Antes de QUALQUER edição surgical ou estética, ler:
- `sops/01-editorial-vs-technical.md` — pedidos editoriais não-explícitos → inventário ao editor, não chutar
- `sops/02-reference-first.md` — zero design from scratch, sempre referência
- `sops/04-speaker-follow.md` — multi-speaker SEMPRE com cam seguindo locutor

## Hard rules

1. **Nunca chutar cut surgical.** Usar `inspect_audio.py` → pedir marcação ao user.
2. **Nunca aprovar clipe sem playback verification.** Rodar `verify_playback.py` antes de declarar pronto.
3. **Nunca design from scratch.** Pedir referência ou perguntar estilo desejado.
4. **Nunca usar render.py upstream.** Sempre o fork local com fps configurável.
5. **Nunca clip ≥ 24fps com fonte de fps diferente** (alinhar fps via EDL).
6. **Sempre cortar pro locutor que está falando.** Voz cega (audio de A sobre imagem fixa de B) é amador. Skip turnos ≤ 800ms (reações tipo "É.", "Sim", "Hum"). Cut 100ms ANTES da fala começar. Ver `sops/04-speaker-follow.md`.
