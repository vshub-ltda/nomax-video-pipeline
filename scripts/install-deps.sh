#!/usr/bin/env bash
# nomax-video-pipeline — installer de dependências de sistema
# Roda 1x por máquina. Idempotente: pode rodar de novo sem quebrar nada.
#
# video-use é VENDORED dentro deste plugin em skills/video-use/ —
# este script só instala dependências de sistema e configura o venv interno.

set -euo pipefail

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'

log()  { printf "${GREEN}[ok]${NC}  %s\n" "$*"; }
warn() { printf "${YELLOW}[!] ${NC}  %s\n" "$*"; }
err()  { printf "${RED}[x] ${NC}  %s\n" "$*"; exit 1; }

# ---------- platform check ----------
if [[ "$(uname -s)" != "Darwin" ]]; then
  warn "Este installer automatiza setup via Homebrew (Mac). Em outros OS, instale manualmente:"
  echo "  - Linux:   sudo apt install ffmpeg python3 python3-venv python3-pip nodejs"
  echo "             pipx install openai-whisper"
  echo "  - Windows: choco install ffmpeg python nodejs"
  echo "             pip install openai-whisper"
  echo "  Depois crie venv em skills/video-use/ manualmente:"
  echo "    cd \$(claude plugin path nomax-video-pipeline)/skills/video-use"
  echo "    python3 -m venv .venv && .venv/bin/pip install -e ."
  exit 0
fi

# ---------- localiza plugin root ----------
PLUGIN_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VIDEO_USE_DIR="${PLUGIN_ROOT}/skills/video-use"

if [[ ! -d "$VIDEO_USE_DIR" ]]; then
  err "video-use não encontrado em $VIDEO_USE_DIR — plugin está incompleto. Reinstale: /plugin install vshub-ltda/nomax-video-pipeline"
fi
log "plugin root: $PLUGIN_ROOT"

# ---------- homebrew ----------
if ! command -v brew >/dev/null 2>&1; then
  err "Homebrew não encontrado. Instalar de https://brew.sh primeiro."
fi
log "homebrew presente"

# ---------- ffmpeg-full (com libass, mov-pro-res, etc) ----------
if [[ ! -x /opt/homebrew/opt/ffmpeg-full/bin/ffmpeg ]]; then
  warn "ffmpeg-full não encontrado em /opt/homebrew/opt/ffmpeg-full — instalando (pode demorar)"
  brew tap homebrew-ffmpeg/ffmpeg
  brew install homebrew-ffmpeg/ffmpeg/ffmpeg --with-libass --with-aom --with-x265
fi
log "ffmpeg-full ok"

# ---------- pipx ----------
if ! command -v pipx >/dev/null 2>&1; then
  warn "pipx não encontrado — instalando"
  brew install pipx
  pipx ensurepath
fi
log "pipx ok"

# ---------- openai-whisper (timing word-level para fine cut) ----------
if ! pipx list 2>/dev/null | grep -q openai-whisper; then
  warn "openai-whisper não instalado via pipx — instalando"
  pipx install openai-whisper
fi
log "openai-whisper ok"

# ---------- python3 (para criar venv do video-use) ----------
if ! command -v python3 >/dev/null 2>&1; then
  warn "python3 não encontrado — instalando python via brew"
  brew install python@3.12
fi
log "python3 $(python3 --version | awk '{print $2}') ok"

# ---------- node (para video-use rendering helpers se necessário) ----------
if ! command -v node >/dev/null 2>&1; then
  warn "node não encontrado — instalando node 20"
  brew install node@20
fi
log "node $(node -v) ok"

# ---------- venv do video-use bundled ----------
if [[ ! -d "$VIDEO_USE_DIR/.venv" ]]; then
  warn "criando venv para video-use em $VIDEO_USE_DIR/.venv"
  python3 -m venv "$VIDEO_USE_DIR/.venv"
fi
log "venv do video-use ok"

# instalar/atualizar dependências do video-use
if [[ -f "$VIDEO_USE_DIR/pyproject.toml" ]]; then
  log "instalando video-use no venv interno (~2-3 min na primeira vez)"
  "$VIDEO_USE_DIR/.venv/bin/pip" install --upgrade pip --quiet
  "$VIDEO_USE_DIR/.venv/bin/pip" install -e "$VIDEO_USE_DIR" --quiet
  log "video-use deps instaladas"
fi

# ---------- env keys ----------
echo
echo "Próximo passo — environment:"
if [[ -z "${ELEVENLABS_API_KEY:-}" ]]; then
  warn "ELEVENLABS_API_KEY não setada. Adicione no seu shell rc:"
  echo "    export ELEVENLABS_API_KEY='sk_...'"
else
  log "ELEVENLABS_API_KEY presente"
fi

if [[ -z "${OPENAI_API_KEY:-}" ]]; then
  warn "OPENAI_API_KEY não setada (opcional — usada apenas se quiser Whisper API ao invés de local)."
fi

echo
log "install-deps.sh concluído. video-use bundled em $VIDEO_USE_DIR"
log "Próximo passo: abra Claude Code no diretório do seu projeto e converse."
