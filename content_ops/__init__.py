"""content-ops — gerenciador, agendador e criador de posts para blogs.

CLI Python puro (stdlib) — poucos tokens, portável, compartilhável.
Segue a premissa narrativa do LifeLog (histórias), com curadoria, fallback,
planejamento e memória.

Comandos principais:
  content-ops init                 — cria/vincula um blog (adapter)
  content-ops daylog add "<texto>" — registra o dia (matéria-prima)
  content-ops daylog show          — mostra o dia de hoje
  content-ops memory               — mostra o que já foi publicado/coberto
  content-ops plan                 — sugere próximos posts (anti-repetição)
  content-ops draft --project X    — gera rascunho narrativo PT+EN
  content-ops thumbnail --slug S   — gera capa (Cloudflare FLUX → PIL fallback)
  content-ops publish --slug S     — build/test/commit/push (com aprovação)
  content-ops verify               — confirma sync LifeLog→Portifólio
"""

__version__ = "0.1.0"
