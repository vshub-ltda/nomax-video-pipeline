#!/usr/bin/env bash
# nomax-video-pipeline — installer de dependências de sistema
# Roda 1x por máquina. Idempotente: pode rodar de novo sem quebrar nada.

set -euo pipefail

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'

log()  { printf "${GREEN}[ok]${NC}  %s\n" "$*"; }
warn() { printf "${YELLOW}[!] ${NC}  %s\n" "$*"; }
err()  { printf "${RED}[x] ${NC}  %s\n" "$*"; exit 1; }

# ---------- platform check ----------
if [[ "$(uname -s)" != "Darwin" ]]; then
  err "Este installer é Mac-only por ora. Para Linux, instalar manualmente: ffmpeg (com libass), pipx, openai-whisper, node 20+."
fi

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

# ---------- node (para video-use se ainda não tiver) ----------
if ! command -v node >/dev/null 2>&1; then
  warn "node não encontrado — instalando node 20"
  brew install node@20
fi
log "node $(node -v) ok"

# ---------- video-use ----------
VIDEO_USE_DIR="${HOME}/Developer/video-use"
if [[ ! -d "$VIDEO_USE_DIR" ]]; then
  warn "video-use não encontrado em $VIDEO_USE_DIR — clonando"
  mkdir -p "${HOME}/Developer"
  git clone https://github.com/anthropics/video-use.git "$VIDEO_USE_DIR"
  pushd "$VIDEO_USE_DIR" >/dev/null
  python3 -m venv .venv
  ./.venv/bin/pip install -r requirements.txt
  popd >/dev/null
fi
log "video-use em $VIDEO_USE_DIR"

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
log "install-deps.sh concluído. Veja docs/ONBOARDING.md para o primeiro corte."
