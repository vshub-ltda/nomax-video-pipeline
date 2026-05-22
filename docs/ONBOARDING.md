# Onboarding — nomax-video-pipeline

Guia do primeiro corte. Tempo estimado: ~25min (instalação) + 20min (primeiro clip).

## 0. Pré-requisitos

- macOS (Apple Silicon ou Intel) — Linux ainda não suportado pelo installer
- Homebrew instalado
- Git + acesso à org `vshub-ltda` no GitHub
- ElevenLabs API key com permissão Scribe (Speech to Text)
- Claude Code instalado

## 1. Instalar o plugin

```bash
# A partir de qualquer pasta:
claude
# dentro do Claude Code:
/plugin install vshub-ltda/nomax-video-pipeline
```

Reinicie o Claude Code para registrar skills e slash-commands.

## 2. Rodar o installer de dependências

```bash
bash $(claude plugin path nomax-video-pipeline)/scripts/install-deps.sh
```

Vai instalar (se não estiver presente):
- `ffmpeg-full` (com libass + ProRes + AOM/x265)
- `pipx` + `openai-whisper`
- `node@20`
- `video-use` em `~/Developer/video-use/`

## 3. Configurar API keys

Adicione no seu `~/.zshrc` (ou `~/.bashrc`):

```bash
export ELEVENLABS_API_KEY='sk_...'         # obrigatório
export OPENAI_API_KEY='sk-...'             # opcional, só se for usar Whisper API
```

Recarregue: `source ~/.zshrc`

## 4. Primeiro corte (smoke test)

Vamos cortar 1 trecho de qualquer podcast bruto para validar a pipeline.

### 4.1. Organizar o source

```bash
mkdir -p ~/Movies/NOMAX-podcasts/$(date +%Y-%m-%d)_meu-primeiro-corte
cp /caminho/do/podcast.mp4 ~/Movies/NOMAX-podcasts/$(date +%Y-%m-%d)_meu-primeiro-corte/
```

### 4.2. Transcrever

Dentro do Claude Code, na raiz do projeto:

```
/nomax-transcribe ~/Movies/NOMAX-podcasts/2026-05-22_meu-primeiro-corte/podcast.mp4
```

Espere 1-5 minutos (depende da duração). Output em `edit/transcripts/podcast.json`.

### 4.3. Selecionar cortes (rough cut)

```
/nomax-clip-rough 2026-05-22_meu-primeiro-corte 3
```

(3 = quantos cortes top quer). Vai listar candidatos com score 4-eixos e extrair os MP4s em `edit/sources/`.

**Pare aqui e revise os 3 candidatos.** Veja se faz sentido editorial antes de gastar tempo no fine cut.

### 4.4. Fine cut

Para cada clip aprovado:

```
/nomax-clip-fine 2026-05-22_meu-primeiro-corte c01
```

Esse comando:
1. Roda `inspect_audio.py` no clip e **pergunta pra você** se há stutters cortar
2. Identifica turnos de speaker (se multi-cam, pede pra criar fontes adicionais)
3. Gera EDL declarativa
4. Renderiza com auto-grade + loudnorm -14 LUFS
5. Gera contact sheet de verificação

Output: `edit/clips/c01_gold.mp4`

### 4.5. Conferência final

Abra o `c01_gold.mp4` no QuickTime. Confira:
- Áudio sem clicks no splice
- Speaker-follow nos momentos certos
- Cor consistente (não pulou contraste)
- Loudness -14 LUFS (mostra OK em qualquer plataforma)

## 5. Captions

**Estão fora do escopo desta versão do plugin** — vamos investir em referências visuais antes de automatizar.

Para esta fase: caption manual no CapCut / Premiere após o fine cut, ou esperar a v0.2 que vai trazer um pipeline de captions calibrado.

## 6. Erros comuns

| Sintoma | Causa | Fix |
|---|---|---|
| `ffmpeg: filter 'showwavespic' not found` | ffmpeg homebrew default sem libass | Reodar installer; vai trocar pra ffmpeg-full |
| `pipx: command not found` | PATH não atualizado | `source ~/.zshrc` ou `pipx ensurepath` |
| `ELEVENLABS_API_KEY not set` | Esqueceu de exportar | Adicionar no `.zshrc` |
| Output em slow motion | EDL com fps != source fps | Verificar `fps` no EDL; usar fps do source ou 30 explícito |
| Speaker errado em tela | Esqueceu de fazer multi-cam reframe | `/nomax-clip-fine` reroda; gerar `sources/<clip>_<speaker>.mp4` |
| Caption mid-sentence | (N/A — captions fora do escopo nesta versão) | — |

## 7. Suporte

- Issues: github.com/vshub-ltda/nomax-video-pipeline/issues
- Skill code: dentro do plugin em `skills/nomax-edit/`
- SOPs: `skills/nomax-edit/sops/`
