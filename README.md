# nomax-video-pipeline

Pipeline NÔMAX para produção de cortes de podcast (curadoria + rough cut + fine cut), empacotada como Claude Code plugin para distribuição interna.

Modo de uso: **conversacional**. Você abre o Claude Code no diretório do projeto e diz, em linguagem natural, o que quer.

## O que tem dentro

| Componente | Função |
|---|---|
| `skills/nomax-edit/` | Skill canônica NÔMAX: pipeline 8-camadas, 5 SOPs, 5 scripts |
| `skills/video-use/` | Skill upstream **vendored** (MIT, browser-use) — transcribe + cut + render canonical |
| `commands/nomax-transcribe.md` | `/nomax-transcribe <video>` — Scribe + diarização |
| `commands/nomax-curate.md` | `/nomax-curate <slug> [n]` — Modo 1 (curadoria pura, tabela editorial) |
| `commands/nomax-clip-rough.md` | `/nomax-clip-rough <slug> [n]` — Modo 2 (curadoria + reframe MP4) |
| `commands/nomax-clip-fine.md` | `/nomax-clip-fine <slug> <clip>` — Modo 3 (fine cut completo) |
| `scripts/install-deps.sh` | Setup macOS one-shot (deps + venv do video-use bundled) |
| `docs/ONBOARDING.md` | Guia do primeiro corte |

## Não tem (ainda)

- **Captions kinéticas** — fora do escopo desta versão. Decisão documentada em [docs/captions-deferred.md](docs/captions-deferred.md). Use CapCut/Premiere manual após o fine cut.

## Instalação (uma vez)

Funciona em **Mac, Linux ou Windows**. O plugin é cross-platform; só os comandos de instalação de dependências mudam por OS.

### 1. Instalar o plugin (qualquer OS)

Requer **Claude Code v2.1.128+**. Atualize antes se necessário:
- Mac: `brew upgrade claude-code`
- npm: `npm install -g @anthropic-ai/claude-code@latest`

Dentro do Claude Code, são **dois comandos**:

```bash
/plugin marketplace add vshub-ltda/nomax-video-pipeline
/plugin install nomax-video-pipeline@nomax-video-pipeline
```

**Fallback manual** (se `/plugin` não estiver disponível no seu ambiente):

```bash
git clone https://github.com/vshub-ltda/nomax-video-pipeline.git \
  ~/.claude/plugins/nomax-video-pipeline
```

Reinicie Claude Code depois.

### 2. Instalar dependências de sistema

| OS | Comando |
|---|---|
| **Mac** | `bash $(claude plugin path nomax-video-pipeline)/scripts/install-deps.sh` |
| **Linux (Debian/Ubuntu)** | `sudo apt install ffmpeg python3 python3-venv python3-pip nodejs && pipx install openai-whisper` |
| **Windows** | `choco install ffmpeg python nodejs` (PowerShell admin) + `pip install openai-whisper` |

### 3. Criar venv do video-use (Linux/Windows apenas — o installer Mac faz sozinho)

```bash
cd $(claude plugin path nomax-video-pipeline)/skills/video-use
python3 -m venv .venv
.venv/bin/pip install -e .
```

### 4. ElevenLabs API key

```bash
# adicionar no ~/.zshrc (Mac/Linux) ou nas env vars do Windows:
export ELEVENLABS_API_KEY='sk_...'
```

video-use é **bundled** no plugin (`skills/video-use/`) — não há clone externo nem divergência entre máquinas do time.

Detalhes do primeiro corte: [docs/ONBOARDING.md](docs/ONBOARDING.md).

## Stack externa (sistema, instalada via installer)

Tudo abaixo é dependência de sistema. O plugin instala ou checa cada uma via `install-deps.sh`:

- `ffmpeg-full` (libass, ProRes, AOM, x265)
- `python3` + venv interno
- `pipx` + `openai-whisper` (timing word-level)
- `node@20` (helpers de render se necessário)
- ElevenLabs Scribe API (texto + diarização) — key via env var

## Stack bundled (vendored no plugin)

- `skills/video-use/` — pinned source de [browser-use/video-use](https://github.com/browser-use/video-use). Licença MIT. Última sincronização: 2026-05-22.
- `skills/nomax-edit/` — engenharia proprietária NÔMAX

## Convenções

- **Project layout**: `~/Movies/NOMAX-podcasts/YYYY-MM-DD_<slug>/edit/{transcripts,sources,clips,inspect,work}`
- **3 modos** de trabalho: curadoria pura / curadoria + rough cut / pipeline completo. Default em ambiguidade = curadoria pura.
- **Tabela de cortes** (Modo 1) = entregável canônico em `edit/clip_candidates.md`
- **EDL declarativo**: JSON com `{sources, ranges, fps, grade}` — fonte da verdade do clip
- **Speaker-follow obrigatório**: turnos >800ms exigem cam separada (Hard Rule #7)
- **Hard Rules**: ver [skills/nomax-edit/SKILL.md](skills/nomax-edit/SKILL.md)

## Versionamento

| Versão | Marco |
|---|---|
| 0.1.0 | Rough + fine cut sem captions. Pipeline batizada no Bureau Social podcast. |
| 0.2.0 | Reframe conversational-first + Modo 1 (curadoria pura como entregável standalone). |
| 0.3.0 | video-use vendored (1 instalação ao invés de 2). |
| (futuro) | Captions calibradas com referências validadas + Notion database de cortes em curadoria |

## Atribuição de upstream

`skills/video-use/` é uma cópia pinada do projeto [browser-use/video-use](https://github.com/browser-use/video-use) (MIT License, Copyright (c) 2026 Browser Use). Mantida vendored para garantir reprodutibilidade entre máquinas do time NÔMAX. Para sincronizar com upstream, ver `docs/sync-video-use.md` (a criar).

## Contribuir

Padrões internos NÔMAX, então mudanças por PR no `main`. Cada mudança em SOP ou hard rule precisa de exemplo de origem (qual projeto/data motivou).
