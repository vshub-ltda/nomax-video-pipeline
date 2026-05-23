# SOP — Editorial vs Technical (Gap 7)

## Problema raiz

Pedidos editoriais ("corta o stutter", "esse trecho ficou estranho", "o ritmo tá ruim") são pedidos de DECISÃO DE EDITOR, não de operação de código. O editor humano tem informação que o assistant não tem: ouvido, contexto narrativo, intenção do projeto.

Quando o assistant trata pedido editorial como pedido técnico, ele CHUTA timestamps, faz cuts errados, gasta iterações resolvendo problemas inventados.

## Regra

**Pedido editorial → retornar inventário de candidates ao editor, não executar.**

## Inputs que distinguem

| Editorial | Technical |
|---|---|
| "tem um stutter" | "cut em 5.43 a 6.12" |
| "essa parte tá lenta" | "cut tudo entre 12s e 15s" |
| "fica estranho" | "fica estranho" + timestamp marcado |
| "a frase ficou truncada" | "a frase ficou truncada — corte no fim do 'documento' não no 'docu'" |

## Procedimento

1. **Detectar**: pedido sem timestamps precisos = editorial
2. **Inventariar**: rodar `inspect_audio.py` no range provável
3. **Retornar**: ao user, devolver:
   - Waveform PNG com markers
   - silencedetect ranges (silêncios reais detectados pelo ffmpeg)
   - Scribe word list com timestamps (texto + timing + speaker_id)
   - (Opcional, casos extremos) Whisper word list para cross-check de timing — uso de exceção, não padrão
4. **Pedir**: marcação precisa (timestamp inicial + final do que cortar)
5. **Só então** rodar `silence_trim.py --extra-cut "A,B"` com os valores marcados

## Exemplos

**Pedido bad-quality:** "corta o stutter aí no começo"
**Resposta correta:** "Rodei inspect_audio nos 4-8s. Anexo waveform.png e lista. Vejo 3 candidatos: (a) [6.84-7.42], (b) [7.20-7.95], (c) [5.96-8.34]. Qual range exato você quer cortar?"

**Pedido good-quality:** "corta entre 6.84 e 7.95"
**Resposta correta:** rodar silence_trim com `--extra-cut "6.84,7.95"`, depois validar com validate_text.py.

## Quando aplicar

- **Sempre** que pedido envolver "está estranho/ruim/lento/com stutter"
- **Sempre** que cut for surgical (sub-segundo)
- **Nunca** quando user fornece timestamp explícito
