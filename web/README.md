# Outorga — interface web

React 19 + Vite + TypeScript + Tailwind CSS v4. Compila para `web/dist`, servido pela própria API em `/`.

```bash
pnpm install
pnpm build          # gera web/dist (a API serve em http://127.0.0.1:8765)
pnpm dev            # desenvolvimento em http://localhost:5173 (proxy de /api -> 127.0.0.1:8765)
```

Telas: Demonstração (38 cenários), Nova análise (upload), Análise ao vivo (SSE do agente), Resultado
(Decisão § 7º, Grafo de poderes, Linha do tempo, Documentos com destaques, Cláusulas, Parecer, Revisão,
"E se…?"), Faixa intermediária (calibração), Auditoria, Histórico e Como funciona. Tema claro/escuro.
