# SOP — Tabela de cortes (entregável de curadoria)

## Contexto

Boa parte do trabalho de podcast clips para no estágio de **curadoria** — levantar quais momentos merecem virar corte, sem necessariamente cortar. O entregável é uma tabela editorial que um editor humano pega depois para executar o fine cut.

Esta SOP define o formato canônico dessa tabela.

## Quando usar

Quando o pedido do usuário for um destes:
- "Quero levantar os melhores cortes desse podcast"
- "Faz uma curadoria para revisarmos com o editor"
- "Quais são os candidatos a corte?"
- "Tabela de cortes do podcast X"

E o usuário NÃO mencionou explicitamente rough cut, extração de MP4, fine cut, ou render. Quando há ambiguidade, perguntar antes de extrair MP4 — extração é trabalho computacional que pode ser desnecessário.

## Schema canônico

```markdown
| ID  | Início    | Fim       | Duração | Hook                       | Payload                                      | Score | Eixos dominantes      | Notas editoriais                        |
|-----|-----------|-----------|---------|----------------------------|----------------------------------------------|-------|------------------------|------------------------------------------|
| c01 | 00:07:23  | 00:08:15  | 52s     | "..." (1 linha, ≤80 chars) | "..." (resumo do payload, 1-2 linhas)        | 87    | Insight + Controversy  | "..." (preferências de cut, refs, etc.)  |
```

### Campos

| Campo | Descrição |
|---|---|
| `ID` | `c01`, `c02`, ... — sequencial dentro do projeto |
| `Início` / `Fim` | Timestamp source no formato `HH:MM:SS` |
| `Duração` | Resultado calculado, formato `Ns` ou `Nm Xs` |
| `Hook` | Frase de abertura ou tese do corte. Citação ou paráfrase enxuta. |
| `Payload` | O que o corte entrega — argumento, controversia, ensinamento, frase de impacto |
| `Score` | 0-100, scoring 4-eixos (Insight 35% + Controversy 30% + Engagement 20% + Topic-match 15%) |
| `Eixos dominantes` | Top 1-2 eixos que justificam o score (ex.: "Insight + Engagement") |
| `Notas editoriais` | Sinalizações do que o editor humano precisa saber: stutters, sugestões de fade, referência de estilo, observação de timing |

## Output

Por padrão, gravar em `edit/clip_candidates.md` no project root.

Variantes:
- Se o usuário pedir, exportar como CSV em `edit/clip_candidates.csv`
- Se for solicitado push para Notion, criar página no database "Cortes em Curadoria" (a definir, ver Próximos passos)
- Se for solicitado Google Sheets, criar planilha (a definir)

## Procedure

1. Transcrição existe? Se não, rodar Scribe primeiro.
2. Invocar a skill `clip-selector` com o transcript completo.
3. Listar top N candidatos (default 8-10; perguntar se o usuário não disse).
4. Para cada candidato, preencher os campos acima. **Não chutar score** — usar exatamente o que clip-selector devolve.
5. Gravar a tabela markdown.
6. Reportar ao usuário: quantidade, range de scores, top-3 com hook completo.
7. **Não extrair MP4** sem confirmação. Sugerir o próximo passo: "Quer que eu extraia rough cut de algum? Quais IDs?"

## Anti-pattern

- Extrair MP4 sem confirmação só porque tem MP4 no source path.
- Editar/melhorar o hook ou payload — devolve o que o clip-selector disse. Editor humano pode reescrever depois.
- Score arredondado ou estimado. Se o clip-selector não rodou, não há score.
- Tabela com menos campos. Se algum não tem dado, deixar em branco com `—`, não omitir a coluna.

## Próximos passos (não bloqueia v0.1)

- Criar database Notion canônico "Cortes em Curadoria" com schema acima
- Slash command `/nomax-curate <slug> [n]` que para no Modo 1 (sem MP4)
- Push automático da tabela markdown para o database Notion

## Origem

Feedback NÔMAX (2026-05-22): "em dados casos, nem irá evoluir para corte. será mesmo um trabalho de curadoria dentro do podcast, e criação de uma tabela de cortes que será utilizada posteriormente por editores."
