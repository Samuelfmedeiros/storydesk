"""storydesk — gerenciador, agendador e criador de posts para blogs.

CLI Python puro (stdlib) — poucos tokens, portável, compartilhável.
Segue a premissa narrativa do LifeLog (histórias), com curadoria, fallback,
planejamento e memória.

Comandos principais:
  storydesk init                 — cria/vincula um blog (adapter)
  storydesk daylog add "<texto>" — registra o dia (matéria-prima)
  storydesk daylog show          — mostra o dia de hoje
  storydesk memory               — mostra o que já foi publicado/coberto
  storydesk plan                 — sugere próximos posts (anti-repetição)
  storydesk draft --project X    — gera rascunho narrativo PT+EN
  storydesk thumbnail --slug S   — gera capa (Cloudflare FLUX → PIL fallback)
  storydesk publish --slug S     — build/test/commit/push (com aprovação)
  storydesk verify               — confirma sync LifeLog→Portifólio
"""

__version__ = "0.2.0"
