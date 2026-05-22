---
description: Modo 2 (curadoria + rough cut) — tabela editorial + MP4s extraídos com reframe. Para Modo 1 (só tabela), peça em conversa.
argument-hint: <project_slug> [n_clips=5]
---

Modo 2 do pipeline NÔMAX: curadoria + rough cut para o projeto `~/Movies/NOMAX-podcasts/$1/`.

**Antes de executar este comando**: confirme que o usuário quer extração de MP4 (Modo 2), não apenas a tabela editorial (Modo 1). Default em ambiguidade é Modo 1.

Passos:
1. Verificar pré-requisitos:
   - `edit/transcripts/<source>.json` existe (rodar `/nomax-transcribe` antes se não)
   - Source video acessível
2. **Invocar a skill `clip-selector`** com o transcript. Pedir top-`${2:-5}` cortes com scoring 4-eixos (Insight 35% / Controversy 30% / Engagement 20% / Topic-match 15%).
3. Salvar resultado em `edit/clip_candidates.md` (tabela editorial — ver SOP 05) e em `edit/clip_candidates.json` (machine-readable).
4. Para cada candidato (c01..cN):
   - **Invocar a skill `video-use`** para extrair `[start, end]` do bruto.
   - Reframe 9:16 (face-pan no speaker dominante por candidato) ou keep 16:9 conforme orientação do user.
   - Salvar em `edit/sources/<clip_id>.mp4`.
5. NÃO aplicar trim de silêncios nesta fase — rough cut preserva o trecho bruto com reframe.
6. Reportar tabela: clip_id, start-end, score total, top-axis driver, source file path.

Não decide cortes editoriais sem confirmação. Se o clip-selector ranking não estiver claro, listar os top 10 e perguntar ao user.

Próximo passo após review do user: `/nomax-clip-fine <project_slug> <clip_id>` para cada clip aprovado.
