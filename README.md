# nomax-video-pipeline

Pipeline NÔMAX para produção de cortes de podcast (rough + fine cut). Empacotada como Claude Code plugin para distribuição interna.

## O que tem dentro

| Componente | Função |
|---|---|
| `skills/nomax-edit/` | Skill canônica: pipeline 8-camadas, 3 SOPs, 5 scripts |
| `commands/nomax-transcribe.md` | `/nomax-transcribe <video>` — Scribe + diarização |
| `commands/nomax-clip-rough.md` | `/nomax-clip-rough <slug>` — clip-selector + reframe |
| `commands/nomax-clip-fine.md` | `/nomax-clip-fine <slug> <clip>` — surgical + speaker-follow + grade + loudnorm |
| `scripts/install-deps.sh` | Setup macOS one-shot |
| `docs/ONBOARDING.md` | Guia do primeiro corte |

## Não tem (ainda)

- **Captions kinéticas** — fora do escopo desta versão. Decisão: investir tempo em referências antes de automatizar. Use CapCut/Premiere manual após o fine cut.
- **Linux installer** — só macOS por ora.
- **Windows** — sem planos.

## Instalação rápida

```bash
# dentro do Claude Code:
/plugin install vshub-ltda/nomax-video-pipeline

# depois, no terminal:
bash $(claude plugin path nomax-video-pipeline)/scripts/install-deps.sh

# adicionar no ~/.zshrc:
export ELEVENLABS_API_KEY='sk_...'
```

Detalhes em [docs/ONBOARDING.md](docs/ONBOARDING.md).

## Stack externa (não bundled)

- `video-use` skill (Anthropic) — transcribe + cut + render canonical
- `clip-selector` skill — curatorial (Hook+Payload + 4-eixos)
- `ffmpeg-full` (libass, ProRes, AOM, x265)
- `openai-whisper` (timing word-level)
- ElevenLabs Scribe API (texto + diarização)

## Convenções

- **Project layout**: `~/Movies/NOMAX-podcasts/YYYY-MM-DD_<slug>/edit/{transcripts,sources,clips,inspect,work}`
- **EDL declarativo**: JSON com `{sources, ranges, fps, grade}` — fonte da verdade do clip
- **Speaker-follow obrigatório**: turnos >800ms exigem cam separada (Hard Rule #6)
- **Hard Rules**: ver [skills/nomax-edit/SKILL.md](skills/nomax-edit/SKILL.md)

## Versionamento

| Versão | Marco |
|---|---|
| 0.1.0 | Rough + fine cut sem captions. Pipeline batizada no Bureau Social podcast. |
| (futuro) | Captions calibradas com referências validadas |

## Contribuir

Padrões internos NÔMAX, então mudanças por PR no `main`. Cada mudança em SOP ou hard rule precisa de exemplo de origem (qual projeto/data motivou).
