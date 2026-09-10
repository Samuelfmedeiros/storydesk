# Storydesk

**Sua mesa de histórias** — transforma o dia a dia em posts de blog.

O Storydesk é o estúdio editorial por trás do LifeLog. Você anota o que fez no dia em 10 segundos; ele guarda tudo, lembra o que já foi publicado, sugere a próxima história sem repetir, escreve o rascunho em PT+EN, gera a capa com IA e publica — sempre com sua aprovação.

Python puro, zero dependências, roda da sua máquina.

## O fluxo

```
daylog (anota o dia)
   |
plan (sugere a próxima história, sem repetir)
   |
draft (rascunho PT+EN no formato do blog)
   |
thumbnail (capa: Cloudflare FLUX -> fallback PIL)
   |
publish (build -> sua confirmação -> push -> verify)
```

## Instalação

Sem dependências — só precisa estar no PATH:

```bash
export PATH="$HOME/projetos/storydesk/bin:$PATH"
```

Dica: coloque a linha no `~/.bashrc` para valer em toda sessão.

## Comandos

| Comando | O que faz |
|---|---|
| `storydesk init` | Vincula um blog (adapter LifeLog é o de referência) |
| `storydesk daylog add "..."` | Registra uma nota do dia (a matéria-prima) |
| `storydesk daylog show` | Mostra as notas de hoje |
| `storydesk plan` | Sugere os próximos posts (anti-repetição via memória) |
| `storydesk memory` | Mostra o que já foi publicado/coberto |
| `storydesk draft --slug S` | Gera o rascunho PT+EN |
| `storydesk thumbnail --slug S` | Gera a capa com IA |
| `storydesk publish --slug S` | Publica: build, confirmação humana, push, verificação |
| `storydesk verify` | Confere o sync blog -> site ao vivo |

Exemplo de uma tarde completa:

```bash
storydesk init --name lifelog --adapter lifelog \
  --repo ~/projetos/lifelog --url https://lifelog-sepia.vercel.app

storydesk daylog add "Corrigi o rate limit com CF-Connecting-IP"
storydesk plan
storydesk draft --slug rate-limit-cf-connecting-ip --project lifelog
storydesk thumbnail --slug rate-limit-cf-connecting-ip --project lifelog
storydesk publish --slug rate-limit-cf-connecting-ip --project lifelog
storydesk verify
```

## Onde vive o estado

Config, memória editorial e daylog ficam em `~/.storydesk/` (JSON puro):

| Arquivo | Conteúdo |
|---|---|
| `config.json` | Blogs vinculados (nome, adapter, repo, URL) |
| `state.json` | Histórico de publicações e rascunhos |
| `daylog.json` | Notas do dia a dia |

**Nada disso vai pro repositório** — o repo contém só código.

## Criando um adapter para outro blog

Qualquer blog implementa a interface `ContentAdapter`:

```python
from storydesk.adapter import ContentAdapter

class GhostAdapter(ContentAdapter):
    name = "ghost"
    def init(self, repo_path): ...                    # vincula
    def draft_path(self, slug, lang): ...             # caminho do rascunho
    def write_draft(self, slug, lang, content): ...   # salva
    def list_slugs(self): ...                         # slugs publicados
    def build(self): ...                              # build
    def publish(self, slug): ...                      # commit/push ou API
    # verify_live vem pronto (URL + slug no HTML)
```

## Segurança

- Estado em `~/.storydesk/`, sem secrets no repo
- `publish` exige confirmação humana (ou `-y` em scripts CI)
- Capa valida a saída local, nunca executa código remoto
- Zero dependências: stdlib + subprocess

## Migração do content-ops (v0.2.0)

O projeto se chamava **content-ops**; foi renomeado para **storydesk**. Se você usava a versão antiga:

| Antes | Agora |
|---|---|
| comando `content-ops` | `storydesk` (`bin/storydesk`) |
| pacote `content_ops` | `storydesk` |
| estado `~/.content-ops/` | `~/.storydesk/` (copiado automaticamente na 1ª execução) |
| variável `CONTENT_OPS_HOME` | `STORYDESK_HOME` |

## Evolução planejada

- MCP server (`hermes-storydesk-mcp`) expondo as mesmas tools
- Adapters: Ghost, WordPress, Astro genérico
- Agendador: fila com horários (12h/16h) reusando crons
- Integração com o watchdog LifeLog -> Portifólio

## Desenvolvimento

```bash
# testes (sem deps):
python3 -m unittest discover -s tests

# rodar direto do repo:
./bin/storydesk --help
```
