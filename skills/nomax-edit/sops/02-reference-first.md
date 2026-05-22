# SOP — Reference-first design (Gap 6)

## Problema raiz

Sem referência visual, design vira chute. Vai 10 iterações, todas mediocres, até alguém mandar uma imagem-norte. Aí em 1 iteração vira o caminho certo. Tempo perdido = caro.

## Regra

**Antes de qualquer decisão estética não-óbvia, exigir referência ou estilo nomeado.**

## Decisões que requerem referência

- Cor de caption (especialmente emphasis/accent)
- Fonte específica (família + peso + estilo)
- Posição vertical da caption
- Tamanho relativo emphasis vs base
- Estilo de animação (entrada/saída)
- Tratamento de background (rounded corners, borders, vignette)
- Color grade criativo (não auto-grade)

## Decisões que NÃO precisam referência

- Posição respeitando safe zone (regra de plataforma, não estética)
- Sync de captions ao áudio (correção técnica)
- Loudnorm target (standard de plataforma)
- Word boundary snapping (regra técnica de video-use)

## Procedimento

1. Receber pedido estético
2. Perguntar UMA vez (não mais que isso):
   - "Tem referência visual? URL, screenshot, ou print de qualquer clipe que você considere o padrão"
   - OU "Quer estilo X / Y / Z?" (Hormozi sans bold / Diary of CEO minimal / kinetic typography MFCast lime green)
3. Esperar resposta antes de gerar primeiro draft
4. Calibrar contra a referência: lista lado-a-lado dos elementos
5. **Default refusal**: se user disser "faz como achar melhor" — DEVOLVER 2-3 estilos diferentes em preview de 5s pra ele escolher, NÃO inventar um

## Anti-patterns

- "Achei que isso ficaria bom" — não. Calibre.
- "Vou tentar X, se não funcionar mudo" — não. Pergunte ANTES.
- "Tem 4 estilos rotacionando" sem referência pedir isso — não.
- Rainbow tipográfico (multi-font multi-color sem propósito) — sinal de design from scratch.

## Quando referência não existe

Se user explicitamente diz "não tenho ref":
1. Mostrar 3 estilos pré-definidos como contact-sheet (Hormozi-bold / kinetic-MFCast / Lex-minimal)
2. User escolhe um pra calibrar
3. Daí itera
