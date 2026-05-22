---
description: Modo 1 (curadoria pura) — tabela editorial de cortes candidatos. Não extrai MP4. Para editor humano usar depois.
argument-hint: <project_slug> [n_clips=8]
---

Modo 1 do pipeline NÔMAX: curadoria pura. Output = tabela markdown em `edit/clip_candidates.md` no formato canônico da SOP 05.

**Ler antes:** `skills/nomax-edit/sops/05-clip-curation-table.md` para o schema da tabela.

Passos:

1. Verificar pré-requisitos:
   - `~/Movies/NOMAX-podcasts/$1/` existe
   - `edit/transcripts/<source>.json` existe (rodar `/nomax-transcribe` antes se não)

2. **Invocar a skill `clip-selector`** com o transcript completo. Pedir top-`${2:-8}` candidatos com scoring 4-eixos (Insight 35% / Controversy 30% / Engagement 20% / Topic-match 15%).

3. **Gerar tabela markdown** em `edit/clip_candidates.md` com schema canônico:

   ```
   | ID | Início | Fim | Duração | Hook | Payload | Score | Eixos dominantes | Notas editoriais |
   ```

   - `ID`: c01, c02, ... sequencial
   - Hook e Payload: copiar exatamente o que o clip-selector retornou. NÃO reescrever.
   - Score: número exato (não arredondar)
   - Notas editoriais: incluir só se o clip-selector flagou algo (stutter, fade necessário, referência sugerida). Senão deixar `—`.

4. **NÃO extrair MP4.** NÃO rodar reframe. NÃO rodar silence_trim. Só a tabela.

5. Reportar ao usuário:
   - Quantidade de candidatos
   - Range de scores
   - Top-3 com hook completo
   - Path da tabela
   - Pergunta de continuidade: "Quer extrair rough cut de algum? Quais IDs?" (NÃO executar sem resposta.)

Hard rule: **Default em ambiguidade é Modo 1**. Se o usuário disser algo como "vamos olhar esse podcast", "que cortes têm aí", "faz curadoria" — é Modo 1. Só sobe pra Modo 2 ou 3 com confirmação explícita.
