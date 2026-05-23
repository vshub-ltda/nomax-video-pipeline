---
description: Fine cut — surgical stutter removal + speaker-follow + grade + loudnorm. Output em clips/<clip>_gold.mp4
argument-hint: <project_slug> <clip_id>
---

Fine cut do clip `$2` no projeto `~/Movies/NOMAX-podcasts/$1/`.

**OBRIGATÓRIO ler antes de qualquer ação:**
- `skills/nomax-edit/SKILL.md` (pipeline + hard rules)
- `skills/nomax-edit/sops/01-editorial-vs-technical.md`
- `skills/nomax-edit/sops/04-speaker-follow.md`

Passos:

1. **Inspect audio** (Hard Rule #1: nunca chutar cut surgical)
   ```
   scripts/inspect_audio.py <source>.mp4 <start> <end> inspect/<clip>/ \
     --scribe edit/transcripts/<source>.json \
     --scribe-video-start <abs_start_in_source>
   ```
   Resultado: waveform.png + silences.txt + scribe_words.txt + summary.md.

   Scribe (ElevenLabs) já entrega texto + timing word-level + diarização. Whisper local NÃO faz parte do pipeline padrão (anti-pattern do video-use: lento e normaliza fillers). O script `inspect_audio.py` aceita `--whisper` como opcional pra debug de divergência em casos extremos, mas isso é exceção, não default.

   **Apresentar ao user** o dossier e pedir timestamps exatos pra qualquer stutter cut. Não chutar.

2. **Speaker-follow** (Hard Rule #6)
   - Identificar via Scribe `speaker_id` os turnos de cada locutor no range do clip
   - Skip turnos ≤ 800ms (reações curtas)
   - Para cada turno >800ms de speaker secundário, criar `sources/<clip>_<speaker_name>.mp4` com crop apropriado
   - Cut 100ms ANTES da fala começar (lead) e 100ms DEPOIS de terminar (tail)

3. **Build EDL** (`edit/<clip>_edl.json`):
   - `sources`: dict de speaker → arquivo mp4
   - `ranges`: lista declarativa com `{source, start, end, note}`
   - `fps`: explícito (default 30 para social)
   - `grade`: "auto" (color grade matemático bounded)

4. **Render**:
   ```
   scripts/render_local.py <clip>_edl.json -o clips/<clip>_gold.mp4
   ```
   render_local faz: extract por range → concat lossless → auto-grade per segment → 2-pass loudnorm -14 LUFS.

5. **Verify playback** (Hard Rule #2):
   ```
   scripts/verify_playback.py clips/<clip>_gold.mp4 clips/<clip>_verify.png \
     --times "<momentos críticos: stutter seams, speaker swaps, opening, climax>"
   ```
   Apresentar contact sheet ao user antes de declarar pronto.

6. **Inspect seam** (verificação final do corte de stutter no output renderizado):
   ```
   scripts/inspect_audio.py clips/<clip>_gold.mp4 <seam-5s> <seam+5s> inspect/<clip>_gold_seam/
   ```
   Olhar waveform pra confirmar que não há gap audível no splice.

Reportar: duração final, n. de cortes surgicais aplicados, n. de speaker swaps, paths do gold e do contact sheet.
