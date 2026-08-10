# content-ops

Gerenciador, agendador e criador de posts para blogs — narrativo, com memória,
curadoria, fallback e poucos tokens.

> **Premissa:** posts são **histórias** (setup → conflito → resolução), como no
> LifeLog. Registra o dia a dia (`daylog`) como matéria-prima, sugere o que
> contar sem repetir (memória), gera capa com AI (fallback em cascata) e
> publica **sempre com aprovação humana**.

## Instalação

```bash
# Sem deps (stdlib puro) — basta estar no PATH:
export PATH="$HOME/projetos/content-ops:$PATH"
```

## Uso rápido

```bash
# 1. Vincula um blog (adapter LifeLog é o de referência)
content-ops init --name lifelog --adapter lifelog --repo ~/projetos/lifelog --url https://lifelog-sepia.vercel.app

# 2. Registra o dia a dia (matéria-prima das histórias)
content-ops daylog add "Corrigi o rate limit com CF-Connecting-IP"
content-ops daylog show

# 3. Curadoria — sugere próximos posts (anti-repetição via memória)
content-ops plan

# 4. Memória editorial
content-ops memory

# 5. Rascunho PT+EN (o conteúdo narrativo é completado pela AI/skill)
content-ops draft --slug nova-historia-capivara-2026-08-09 --project capivara --tags '["capivara"]' --icon 🐹

# 6. Capa AI (Cloudflare FLUX → fallback PIL)
content-ops thumbnail --slug nova-historia-capivara-2026-08-09 --project capivara

# 7. Publica com aprovação (build → confirmar → push → verify)
content-ops publish --slug nova-historia-capivara-2026-08-09 --project capivara

# 8. Verifica sync com o site
content-ops verify
```

## Arquitetura

```
content-ops/
├── content_ops/          # Pacote (stdlib puro)
│   ├── cli.py            # Entrypoint argparse
│   ├── state.py          # Config/estado JSON em ~/.content-ops/
│   ├── daylog.py         # Registro do dia a dia
│   ├── memory.py         # Memória editorial (anti-repetição)
│   ├── plan.py           # Curadoria + grade cíclica
│   ├── adapter.py        # Interface genérica de conteúdo
│   └── thumbnail.py      # Capa AI (FLUX → PIL fallback)
├── adapters/
│   └── lifelog.py        # Adapter LifeLog (Astro/MDX, PT+EN)
├── tests/                # unittest (sem deps)
└── examples/
```

## Criando um adapter para outro blog

Qualquer blog/site de notícias implementa `ContentAdapter`:

```python
from content_ops.adapter import ContentAdapter

class GhostAdapter(ContentAdapter):
    name = "ghost"
    def init(self, repo_path): ...      # vincula
    def draft_path(self, slug, lang): ...  # caminho do rascunho
    def write_draft(self, slug, lang, content): ...  # salva
    def list_slugs(self): ...           # slugs publicados
    def build(self): ...                # build
    def publish(self, slug): ...        # commit/push ou API
    # verify_live vem pronto (URL + slug no HTML)
```

## Segurança

- Config/estado em `~/.content-ops/` (JSON), **sem secrets no repo**
- `publish` exige confirmação humana (ou `-y` em scripts CI)
- Thumbnail valida saída local, nunca executa código remoto
- Nenhuma dependência externa — stdlib + subprocess

## Evolução planejada

- MCP server (`hermes-content-mcp`) expondo as mesmas tools
- Adapters: Ghost, WordPress, Astro genérico
- Agendador: fila com horários (12h/16h) reusando crons
- Integração com o watchdog LifeLog→Portifólio
