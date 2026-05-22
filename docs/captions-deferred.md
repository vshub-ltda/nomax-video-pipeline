# Decisão: Captions fora do escopo da v0.1

## Contexto

Durante o piloto Bureau Social (2026-05-13/14) testamos um pipeline de captions kinéticas via Remotion (React-based video composition), com Montserrat 800 white + Playfair Display Italic 800 lime green (#C7F232), multi-line layout, hero scale 1.55x para climax.

Funcionou tecnicamente — produziu ProRes 4444 alpha, com sync de Whisper word timing.

## Por que ficou fora

Apesar de tecnicamente operacional, a qualidade visual ainda **não bate as referências premium** (Diary of a CEO, Hormozi, PBD). Faltava:

1. Calibragem fina de spacing, tracking, line-height per chunk
2. Repertório de referências visuais para padrões diferentes (clip de impacto vs clip didático vs clip de bordão)
3. Forced alignment texto-Scribe ↔ timing (Whisper text tem ~5-10% erro em PT-BR, Scribe tem timing burst)
4. Critérios claros de quando usar emphasis solo vs emphasis multi-line vs hero scale

User feedback (2026-05-14): "vamos ter que gastar mais tempo criando referências e instruções claras para chegar no resultado que queremos. logo, vamos deixar o fator legenda para depois."

## O que ficou pronto e fica guardado para v0.2

Em `~/Developer/nomax-captions/` (não bundled neste plugin):
- Remotion project com `CaptionTrack` + `LowerThird` compositions
- Multi-line layout via `groupByEmphasis`
- HERO_SCALE multiplier
- Pre-calibrated styles (Montserrat / Playfair / #C7F232)

Em `~/.claude/skills/nomax-edit/` (skill pessoal do usuário):
- `validate_text.py` — checa truncamento + perda de keywords
- `sops/03-forced-alignment-text.md` — strategy (manual + planejamento whisperX)

Quando voltarmos a captions:
1. Coletar 5-10 referências de captions premium aprovadas pelo time
2. Calibrar Remotion styles contra cada uma
3. Implementar forced alignment (whisperX) para resolver Whisper-text errors
4. Definir critérios editoriais (emphasis, hero, multi-line) em SOP
5. Re-empacotar como `nomax-captions` skill no plugin

## Workaround interino

Para clipes que precisam de caption hoje:
- CapCut: usar template Opus/Karaoke/Minimal pre-burnt
- Premiere: caption manual seguindo o stylesheet provisório acima
- Não fazer caption inline neste plugin
