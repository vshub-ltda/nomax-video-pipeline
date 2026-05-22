# SOP — Speaker-following reframe (no blind voice)

## Problema raiz

Voz cega = áudio do locutor A sobre imagem fixa do locutor B. Acontece quando o reframe 9:16 é feito uma vez no início (focando o speaker dominante) e nunca atualiza. Resultado: quando o segundo participante fala, o espectador ouve sem ver — fica estranho, parece erro de continuidade.

Editor sênior NUNCA deixa isso passar.

## Regra

**Toda fala substantiva (>800ms) deve ter o crop seguindo o locutor.**

Por que 800ms: reações curtas tipo "É.", "Sim", "Pô", "Hum" não justificam cut — quebram o ritmo e cansam o olho. Quando alguém intervém com >800ms de conteúdo (frase completa, pergunta), cortar.

## Procedure

1. **Detectar speakers** via Scribe diarization (`speaker_id` em cada word).
2. **Agrupar em turnos** — palavras consecutivas do mesmo speaker com gap < 0.5s viram um turno.
3. **Filtrar** turnos curtos (≤ 800ms): manter speaker anterior em tela.
4. **Antecipar cut**: cortar pro novo speaker 100ms ANTES da primeira palavra começar (regra clássica de editing — olho chega antes do ouvido).
5. **Crop por speaker**:
   - Detectar face position em PARTE_1 (sample frame médio)
   - Definir crop_x para cada speaker (608px width pra 9:16 a partir de 1080 height)
   - Aplicar no extract de cada segment

## Implementação

Script `scripts/build_speaker_segments.py` (ver script):
- Input: Scribe transcript JSON + clip range + speaker→crop map
- Output: lista de ranges com `source` apontando pra arquivo do speaker correto
- Pode ser injetado direto no EDL

## Anti-pattern

- Cortar pra speaker que dá só "É." de 300ms. Fica frenético.
- Cut atrasado (depois da palavra começar): olho sente "tic" temporal.
- Mais de 1 cut a cada 4s sem motivo (rule of thumb: respiração visual entre cuts).

## Edge cases

- **Speakers falando em cima** (overlap): manter quem começou primeiro até o outro consolidar (>500ms contínuo).
- **Speaker fora do frame** (host atrás da câmera, fora do plano): nesse caso só temos um speaker visualmente, então não cut — usar B-roll ou caption emphasis.
- **Clipes muito curtos (< 6s)**: ignorar speaker-follow se gerar mais de 1 cut. Quebra o ritmo.

## Origem

NÔMAX c04 (2026-05-14): user flagou "no c04 a Fernanda ficou fixa na tela 100% do tempo, mesmo quando o outro hoster falava. isso é estranho, pois fica uma voz cega."
