<p align="center">
  <a href="https://github.com/Samuelfmedeiros/storydesk/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/license-MIT-6366f1?style=flat-square" alt="License">
  </a>
  <a href="https://www.python.org/downloads/">
    <img src="https://img.shields.io/badge/python-3.10%2B-3776ab?style=flat-square&logo=python&logoColor=white" alt="Python 3.10+">
  </a>
  <img src="https://img.shields.io/badge/dependencies-0-22c55e?style=flat-square" alt="Zero dependencies">
</p>

<h1 align="center">Storydesk</h1>

<p align="center"><strong>Your story desk</strong> — turns everyday work into blog posts.</p>

> 🌐 **English** · [🇧🇷 Português](README.pt-BR.md)

Storydesk is the editorial studio behind LifeLog. You jot down what you did today in
10 seconds; it stores everything, remembers what has already been published, suggests
the next story without repeating itself, writes the draft in PT+EN, generates the cover
with AI and publishes — always with your approval.

Pure Python, zero dependencies, runs on your machine.

## The flow

```
daylog (jot down the day)
   |
plan (suggests the next story, no repeats)
   |
draft (PT+EN draft in the blog's format)
   |
thumbnail (cover: Cloudflare FLUX -> PIL fallback)
   |
publish (build -> your confirmation -> push -> verify)
```

## Installation

No dependencies — it just needs to be on your PATH:

```bash
export PATH="$HOME/projects/storydesk/bin:$PATH"
```

Tip: put that line in your `~/.bashrc` so it applies to every session.

## Commands

| Command | What it does |
|---|---|
| `storydesk init` | Links a blog (the LifeLog adapter is the reference one) |
| `storydesk daylog add "..."` | Records a note for the day (the raw material) |
| `storydesk daylog show` | Shows today's notes |
| `storydesk plan` | Suggests the next posts (anti-repetition via memory) |
| `storydesk memory` | Shows what has already been published/covered |
| `storydesk draft --slug S` | Generates the PT+EN draft |
| `storydesk thumbnail --slug S` | Generates the cover with AI |
| `storydesk publish --slug S` | Publishes: build, human confirmation, push, verification |
| `storydesk verify` | Checks the blog -> live site sync |

A full afternoon, end to end:

```bash
storydesk init --name lifelog --adapter lifelog \
  --repo ~/projects/lifelog --url https://lifelog-sepia.vercel.app

storydesk daylog add "Fixed the rate limit with CF-Connecting-IP"
storydesk plan
storydesk draft --slug rate-limit-cf-connecting-ip --project lifelog
storydesk thumbnail --slug rate-limit-cf-connecting-ip --project lifelog
storydesk publish --slug rate-limit-cf-connecting-ip --project lifelog
storydesk verify
```

## Where the state lives

Config, editorial memory and daylog live in `~/.storydesk/` (plain JSON):

| File | Content |
|---|---|
| `config.json` | Linked blogs (name, adapter, repo, URL) |
| `state.json` | Publication and draft history |
| `daylog.json` | Day-to-day notes |

**None of it goes into the repository** — the repo contains code only.

## Writing an adapter for another blog

Any blog implements the `ContentAdapter` interface:

```python
from storydesk.adapter import ContentAdapter

class GhostAdapter(ContentAdapter):
    name = "ghost"
    def init(self, repo_path): ...                    # link
    def draft_path(self, slug, lang): ...             # draft path
    def write_draft(self, slug, lang, content): ...   # save
    def list_slugs(self): ...                         # published slugs
    def build(self): ...                              # build
    def publish(self, slug): ...                      # commit/push or API
    # verify_live comes for free (URL + slug in the HTML)
```

## Security

- State in `~/.storydesk/`, no secrets in the repo
- `publish` requires human confirmation (or `-y` inside CI scripts)
- The cover step validates local output, never runs remote code
- Zero dependencies: stdlib + subprocess

## Migrating from content-ops (v0.2.0)

The project used to be called **content-ops**; it was renamed to **storydesk**.
If you were on the old version:

| Before | Now |
|---|---|
| `content-ops` command | `storydesk` (`bin/storydesk`) |
| `content_ops` package | `storydesk` |
| `~/.content-ops/` state | `~/.storydesk/` (copied automatically on first run) |
| `CONTENT_OPS_HOME` variable | `STORYDESK_HOME` |

## Customizing your topics

`plan` suggests posts based on configurable topics. It ships neutral by default
(Devlog, Discoveries, Automation, Security) — personalize it with YOUR projects
in `~/.storydesk/config.json`:

```json
{
  "topics": [
    {"project": "myblog", "label": "My Blog", "icon": "📝",
     "pitch": "What your project is about."},
    {"project": "studies", "label": "Studies", "icon": "📚",
     "pitch": "What you are learning."}
  ]
}
```

Anti-repetition uses the editorial memory: the less coverage a topic has,
the sooner it comes back in the queue.

## Roadmap

- MCP server (`hermes-storydesk-mcp`) exposing the same tools
- Adapters: Ghost, WordPress, generic Astro
- Scheduler: queue with time slots (12h/16h) reusing crons
- LifeLog -> Portifolio watchdog integration

## Development

```bash
# tests (no deps):
python3 -m unittest discover -s tests

# run straight from the repo:
./bin/storydesk --help
```

## License

MIT — see [LICENSE](LICENSE).
