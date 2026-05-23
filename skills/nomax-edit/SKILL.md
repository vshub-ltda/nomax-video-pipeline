---
name: nomax-edit
description: NÔMAX podcast clip pipeline — curadoria + rough cut + fine cut, em modo conversacional. Para quando o usuário menciona "corte de podcast", "curadoria de cortes", "tabela de cortes", "podcast clip", "rough cut", "fine cut", "Bureau Social", ou pede pra olhar um podcast e levantar momentos. Pareia com clip-selector (curatorial) e video-use (transcribe + render canonical).
---

# nomax-edit — Pipeline NÔMAX de cortes de podcast

Sistema completo, **conversacional**, para trabalho de podcast clips. Cobre desde curadoria pura (tabela de candidatos para editor humano) até fine cut renderizado pronto para post.

## Modo de interação — conversacional, não comando-driven

O time NÔMAX interage com este pipeline em linguagem natural. Não force slash commands a menos que o usuário explicitamente peça por eles. Quando alguém disser algo como:

- "Tenho um podcast aqui, quero curar os cortes"
- "Faz o fine cut do c03 com speaker-follow"
- "Esse corte aqui tá com stutter, dá uma olhada"

→ Conduza a conversa: pergunte o que falta (path, slug, modo), execute o passo certo, devolva o resultado. Use o pipeline declarado abaixo como guia interno.

## Os 3 modos de trabalho

| Modo | Output | Quando aplica |
|---|---|---|
| **1. Curadoria pura** | Tabela markdown em `edit/clip_candidates.md` (ver SOP 05) | Quando o usuário só quer levantar candidatos. Editor humano vai cortar depois. **Não extrai MP4.** |
| **2. Curadoria + rough cut** | Tabela + arquivos em `edit/sources/<clip>.mp4` (reframe aplicado) | Quando o usuário quer adiantar a parte mecânica mas deixar fine cut pro editor humano. |
| **3. Pipeline completo** | `edit/clips/<clip>_gold.mp4` (post-ready) | Quando o clipe vai direto pra post, sem revisão de editor humano. |

Default em ambiguidade: **Modo 1**. É o mais barato e o mais comum. Confirme antes de subir pra Modo 2 ou 3.

## Pipeline interno (8 camadas)

```
1. Inventário ffprobe → metadata do bruto
2. Transcrição Scribe (texto + diarização speaker_id por palavra)
3. Seleção via clip-selector (Hook+Payload + scoring 4-eixos)
   ← Modo 1 PARA aqui (output: tabela)
4. Pré-processo: cut + reframe 9:16 ou keep 16:9
   ← Modo 2 PARA aqui (output: tabela + MP4s)
5. silence_trim.py: silences auto + extra-cuts cirúrgicos + drop-tokens
6. EDL declarativa (sources, ranges, grade, fps) — multi-source pra speaker-follow
7. render_local.py (extract → concat → loudnorm -14 LUFS)
8. Verificação: verify_playback (contact sheet) + inspect_audio (seam check)
   ← Modo 3 PARA aqui (output: <clip>_gold.mp4)
```

## Tools

| Script | Função | Modos onde aparece |
|---|---|---|
| `scripts/inspect_audio.py` | Waveform + silencedetect + Scribe word list (texto+timing). Suporte opcional a Whisper só pra debug de divergência em casos extremos. | 3 (fine cut) |
| `scripts/verify_playback.py` | Contact sheet de N frames pra "assistir" o clipe | 3 |
| `scripts/silence_trim.py` | Cuts de silêncio + extra-cut surgical + drop-token | 3 |
| `scripts/render_local.py` | Fork local de video-use render.py com fps configurável + multi-source | 3 |
| `scripts/grade.py` | Auto color grade matemático bounded ±8% | 3 |

## Project layout esperado

```
~/Movies/NOMAX-podcasts/YYYY-MM-DD_<slug>/
├── <SOURCE>.MP4 (symlink ao bruto)
└── edit/
    ├── transcripts/
    │   └── <source>.json           ← Scribe (ElevenLabs) — texto + diarização speaker_id
    ├── clip_candidates.md          ← TABELA editorial (Modo 1 output)
    ├── sources/
    │   ├── <clip>.mp4              ← Modo 2 output: speaker A reframe
    │   └── <clip>_<speakerB>.mp4   ← speaker B reframe (multi-cam)
    ├── <clip>_edl.json             ← declarativa (Modo 3)
    ├── work/                       ← scripts + intermediários
    ├── inspect/<clip>/             ← dossiers do inspect_audio
    └── clips/
        └── <clip>_gold.mp4         ← Modo 3 output: post-ready
```

## SOPs obrigatórios

Antes de qualquer ação não-trivial, ler:
- `sops/01-editorial-vs-technical.md` — pedidos editoriais → inventário ao usuário, não chutar
- `sops/02-reference-first.md` — zero design from scratch, sempre referência
- `sops/04-speaker-follow.md` — multi-speaker SEMPRE com cam seguindo locutor
- `sops/05-clip-curation-table.md` — formato canônico da tabela (Modo 1)

## Hard rules

1. **Default em ambiguidade = Modo 1 (curadoria pura).** Não extraia MP4 nem renderize sem confirmação. Curadoria é barato; rendering é caro e descartável.
2. **Nunca chutar cut surgical.** Usar `inspect_audio.py` → pedir marcação ao usuário.
3. **Nunca aprovar clipe Modo 3 sem playback verification.** Rodar `verify_playback.py` antes.
4. **Nunca design from scratch.** Pedir referência ou perguntar estilo desejado.
5. **Nunca usar render.py upstream.** Sempre o fork local com fps configurável.
6. **Alinhar fps via EDL** (default 30 social, ou fps do source).
7. **Speaker-follow obrigatório em multi-speaker.** Voz cega é amador. Skip turnos ≤ 800ms. Cut 100ms antes da fala.

## Slash commands (atalhos opcionais)

Existem para repetição automatizada — não são a interface primária.

- `/nomax-transcribe <video>` — só transcrição Scribe
- `/nomax-clip-rough <slug> [n]` — Modo 2 (tabela + MP4s)
- `/nomax-clip-fine <slug> <clip>` — Modo 3 (fine cut completo)

Para Modo 1 (curadoria pura, sem MP4), peça em conversa: "curadoria de N cortes do projeto X".
