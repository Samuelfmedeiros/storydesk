"""CLI do content-ops — entrypoint principal (argparse, sem deps)."""
import argparse
import json
import sys
from datetime import datetime

from . import __version__
from .daylog import add_note, show, recent
from .memory import mark_published, summary, is_covered
from .plan import suggest, weekly_grid
from .state import get_config, save_config

# Registro de adapters (import tardio para não quebrar sem deps)
_ADAPTERS = {}


def _get_adapter(name: str, repo_path: str = ""):
    if name not in _ADAPTERS:
        if name == "lifelog":
            from adapters.lifelog import LifelogAdapter
            _ADAPTERS[name] = LifelogAdapter(repo_path)
        else:
            sys.stderr.write(f"Adapter desconhecido: {name}\n")
            sys.exit(1)
    return _ADAPTERS[name]


def cmd_init(args):
    cfg = get_config()
    blog = {"name": args.name, "adapter": args.adapter,
            "repo_path": args.repo, "url": args.url or ""}
    cfg["blogs"] = [b for b in cfg["blogs"] if b["name"] != args.name]
    cfg["blogs"].append(blog)
    cfg["default_blog"] = cfg.get("default_blog") or args.name
    save_config(cfg)

    adapter = _get_adapter(args.adapter, args.repo)
    ok = adapter.init(args.repo)
    if not ok:
        print(f"⚠️ Repo {args.repo} não parece válido para o adapter {args.adapter}")
    print(f"✅ Blog '{args.name}' vinculado ({args.adapter}) — {args.repo}")
    return 0


def cmd_daylog(args):
    if args.action == "add":
        if not args.text:
            print("Uso: content-ops daylog add \"<nota do dia>\"")
            return 2
        day = add_note(args.text)
        print(f"📝 Registrado em {day}")
    elif args.action == "show":
        notes = show(args.day)
        if not notes:
            print(f"(sem notas em {args.day or 'hoje'})")
        for n in notes:
            print(f"  [{n['time']}] {n['text']}")
    return 0


def cmd_memory(args):
    s = summary()
    print(f"Publicados: {s['published_count']}")
    print(f"Rascunhos:  {s['draft_count']}")
    print("Cobertura por projeto:")
    for proj, slugs in s["covered_projects"].items():
        print(f"  {proj}: {len(slugs)} post(s)")
    if s["last_published"]:
        lp = s["last_published"]
        print(f"Último: {lp['title']} ({lp['project']}, {lp['date'][:10]})")
    return 0


def cmd_plan(args):
    print("🧠 Sugestões (projetos menos cobertos primeiro):\n")
    for s in suggest(args.count):
        print(f"{s['icon']} {s['label']} — {s['pitch']}")
        print(f"   cobertura: {s['covered']} post(s)")
        for h in s["daylog_hints"]:
            print(f"   📌 daylog: {h}")
        print()
    print("📅 Grade cíclica (próximos 7 dias):")
    for g in weekly_grid():
        print(f"   +{g['offset']}d → {g['project']}")
    return 0


def cmd_thumbnail(args):
    cfg = get_config()
    blog = _find_blog(cfg, args.blog)
    if not blog:
        return 2
    from .thumbnail import generate
    path = generate(args.slug, args.project, blog["repo_path"], force=args.force)
    if path:
        print(f"🖼️ Capa: {path}")
    else:
        print("⚠️ Sem capa gerada (Worker e PIL falharam) — post segue sem cover")
    return 0


def _find_blog(cfg, name: str | None):
    blogs = cfg.get("blogs", [])
    if not blogs:
        print("Nenhum blog vinculado. Rode: content-ops init")
        return None
    if name:
        for b in blogs:
            if b["name"] == name:
                return b
        print(f"Blog '{name}' não encontrado")
        return None
    default = cfg.get("default_blog")
    for b in blogs:
        if b["name"] == default:
            return b
    return blogs[0]


def cmd_verify(args):
    cfg = get_config()
    blog = _find_blog(cfg, args.blog)
    if not blog:
        return 2
    adapter = _get_adapter(blog["adapter"], blog["repo_path"])
    if not blog.get("url"):
        print("⚠️ Blog sem URL configurada — impossível verificar live")
        return 0
    # Pega os 3 posts mais recentes (por mtime) e verifica no HTML
    recent = getattr(adapter, "recent_slugs", None)
    slugs = recent(3) if recent else adapter.list_slugs()[-3:]
    results = {s: adapter.verify_live(blog["url"], s) for s in slugs}
    for s, ok in results.items():
        print(f"  {'✅' if ok else '⚠️'} {s}")
    if all(results.values()):
        print("✅ Posts refletidos no site")
    else:
        print("⚠️ Algum post não refletiu (ISR pode demorar até 30min)")
    return 0


def cmd_draft(args):
    """Escreve o rascunho. O conteúdo real é gerado pela AI/skill — aqui
    criamos o esqueleto com frontmatter válido e instruções."""
    cfg = get_config()
    blog = _find_blog(cfg, args.blog)
    if not blog:
        return 2
    adapter = _get_adapter(blog["adapter"], blog["repo_path"])

    slug = args.slug
    title = args.title or f"Nova história do {args.project}"
    today = datetime.now().strftime("%Y-%m-%d")

    frontmatter = (
        "---\n"
        f"title: \"{title}\"\n"
        f"description: \"Resumo de 1-2 frases\"\n"
        f"date: {today} 12:00:00 -03:00\n"
        f"pubDate: {today} 16:00:00 -03:00\n"
        f"project: {args.project}\n"
        f"tags: [{args.tags}]\n"
        f"icon: \"{args.icon or '💡'}\"\n"
        f"cover: /covers/{slug}.webp\n"
        "featured: false\n"
        "---\n\n"
        "## ⚡ Abertura (gancho)\n\n"
        "<!-- Escreva aqui o gancho da história (setup → conflito → resolução) -->\n\n"
        "## 🧠 Contexto\n\n"
        "## 🛠️ Detalhes técnicos\n\n"
        "| Item | Antes | Depois |\n"
        "|------|-------|--------|\n"
        "| | | |\n"
    )
    pt_path = adapter.write_draft(slug, "pt", frontmatter)
    en_path = adapter.write_draft(slug, "en",
        frontmatter.replace('"Resumo de 1-2 frases"', '"One or two sentence summary"')
                   .replace("## ⚡ Abertura (gancho)", "## ⚡ Hook opening")
                   .replace("## 🧠 Contexto", "## 🧠 Context")
                   .replace("## 🛠️ Detalhes técnicos", "## 🛠️ Technical details")
                   .replace("| Item | Antes | Depois |", "| Item | Before | After |"))
    print(f"📝 Rascunho criado:\n  PT: {pt_path}\n  EN: {en_path}")
    print("→ Preencha o conteúdo narrativo (a skill/AI completa).")
    return 0


def cmd_publish(args):
    """Publica após aprovação. Sem aprovação = nada é enviado."""
    cfg = get_config()
    blog = _find_blog(cfg, args.blog)
    if not blog:
        return 2
    adapter = _get_adapter(blog["adapter"], blog["repo_path"])

    print(f"📦 Publicando '{args.slug}' em '{blog['name']}'")
    print("1. Build do blog...")
    if not adapter.build():
        print("❌ Build falhou — abortando")
        return 1
    print("   ✅ Build OK")

    if not args.yes:
        resp = input("2. Commit+push? [s/N] ").strip().lower()
        if resp not in ("s", "sim", "y", "yes"):
            print("Cancelado")
            return 0

    print("3. Commit+push...")
    if not adapter.publish(args.slug):
        print("❌ Push falhou")
        return 1
    print("   ✅ Publicado")

    if blog.get("url"):
        print("4. Verificando no ar...")
        import time
        time.sleep(20)
        ok = adapter.verify_live(blog["url"], args.slug)
        print("   ✅ No ar" if ok else "   ⚠️ Ainda não detectado (ISR pode demorar)")

    from .memory import mark_published
    mark_published(args.slug, args.title or args.slug, args.project or "", blog["name"])
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="content-ops",
        description="Gerenciador, agendador e criador de posts (narrativo, com memória).")
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="cmd")

    p_init = sub.add_parser("init", help="Vincula um blog")
    p_init.add_argument("--name", required=True)
    p_init.add_argument("--adapter", default="lifelog")
    p_init.add_argument("--repo", required=True)
    p_init.add_argument("--url", default="")

    p_day = sub.add_parser("daylog", help="Registra/mostra o dia a dia")
    p_day.add_argument("action", choices=["add", "show"])
    p_day.add_argument("text", nargs="?")
    p_day.add_argument("--day")

    sub.add_parser("memory", help="Mostra memória editorial")

    p_plan = sub.add_parser("plan", help="Sugere próximos posts")
    p_plan.add_argument("--count", type=int, default=3)

    p_thumb = sub.add_parser("thumbnail", help="Gera capa")
    p_thumb.add_argument("--slug", required=True)
    p_thumb.add_argument("--project", required=True)
    p_thumb.add_argument("--blog", default="")
    p_thumb.add_argument("--force", action="store_true")

    p_draft = sub.add_parser("draft", help="Cria rascunho PT+EN")
    p_draft.add_argument("--slug", required=True)
    p_draft.add_argument("--title", default="")
    p_draft.add_argument("--project", required=True)
    p_draft.add_argument("--tags", default="")
    p_draft.add_argument("--icon", default="")
    p_draft.add_argument("--blog", default="")

    p_pub = sub.add_parser("publish", help="Publica com aprovação")
    p_pub.add_argument("--slug", required=True)
    p_pub.add_argument("--title", default="")
    p_pub.add_argument("--project", default="")
    p_pub.add_argument("--blog", default="")
    p_pub.add_argument("-y", "--yes", action="store_true", help="pula confirmação (scripts)")

    p_ver = sub.add_parser("verify", help="Verifica sync com o site")
    p_ver.add_argument("--blog", default="")

    args = parser.parse_args(argv)
    if not args.cmd:
        parser.print_help()
        return 0

    handlers = {
        "init": cmd_init,
        "daylog": cmd_daylog,
        "memory": cmd_memory,
        "plan": cmd_plan,
        "thumbnail": cmd_thumbnail,
        "draft": cmd_draft,
        "publish": cmd_publish,
        "verify": cmd_verify,
    }
    return handlers[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
