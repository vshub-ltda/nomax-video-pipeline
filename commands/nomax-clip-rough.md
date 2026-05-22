---
description: Rough cut — selecionar candidatos via clip-selector e cortar com video-use. Output em clips/<clip>_rough.mp4
argument-hint: <project_slug> [n_clips=5]
---

Rough cut para o projeto `~/Movies/NOMAX-podcasts/$1/`.

Passos:
1. Verificar pré-requisitos:
   - `edit/transcripts/<source>.json` existe (rodar `/nomax-transcribe` antes se não)
   - Source video acessível
2. **Invocar a skill `clip-selector`** com o transcript. Pedir top-`${2:-5}` cortes com scoring 4-eixos (Insight 35% / Controversy 30% / Engagement 20% / Topic-match 15%).
3. Salvar resultado em `edit/clip_candidates.json` (timestamps + score + hook + payload).
4. Para cada candidato (c01..cN):
   - **Invocar a skill `video-use`** para extrair `[start, end]` do bruto.
   - Reframe 9:16 (face-pan no speaker dominante por candidato) ou keep 16:9 conforme orientação do user.
   - Salvar em `edit/sources/<clip_id>.mp4`.
5. NÃO aplicar trim de silêncios nesta fase — rough cut preserva o trecho bruto com reframe.
6. Reportar tabela: clip_id, start-end, score total, top-axis driver, source file path.

Não decide cortes editoriais sem confirmação. Se o clip-selector ranking não estiver claro, listar os top 10 e perguntar ao user.

Próximo passo após review do user: `/nomax-clip-fine <project_slug> <clip_id>` para cada clip aprovado.
