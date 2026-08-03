#!/usr/bin/env python3
"""Generate edu hub index.html from data/courses.json."""

from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "courses.json"
OUT = ROOT / "index.html"

TRACK_ORDER = ("Core", "Analog", "Digital")


def course_url(course_id: str) -> str:
    return f"https://uoftasic.com/{html.escape(course_id)}/"


def render(data: dict) -> str:
    courses = data["courses"]
    workspace = html.escape(data["workspace_url"])
    template = html.escape(data["template_url"])

    live = [c for c in courses if c["status"] == "live"]
    planned = [c for c in courses if c["status"] == "planned"]

    live_items = []
    for c in live:
        live_items.append(
            f"""      <li>
        <a href="{course_url(c['id'])}">
          <strong>{html.escape(c['title'])}</strong>
          <span>{html.escape(c['summary'])}</span>
        </a>
      </li>"""
        )

    roadmap_blocks = []
    by_track: dict[str, list] = {t: [] for t in TRACK_ORDER}
    for c in planned:
        by_track.setdefault(c["track"], []).append(c)

    for track in TRACK_ORDER:
        group = by_track.get(track) or []
        if not group:
            continue
        items = "\n".join(
            f"          <li><span class=\"id\">{html.escape(c['id'].upper())}</span>"
            f" {html.escape(c['title'].split(' — ', 1)[-1] if ' — ' in c['title'] else c['title'])}"
            f"<em>{html.escape(c['summary'])}</em></li>"
            for c in group
        )
        roadmap_blocks.append(
            f"""      <div class="track">
        <h3>{html.escape(track)}</h3>
        <ul class="roadmap">
{items}
        </ul>
      </div>"""
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>UofT ASIC Education</title>
  <meta name="description" content="UofT ASIC Team internal education hub — courses, workspace, and roadmap" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,550;9..144,650&family=Source+Sans+3:wght@400;600&display=swap" rel="stylesheet" />
  <style>
    :root {{
      --bg: #f3f6f4;
      --fg: #14201c;
      --muted: #4d5c56;
      --accent: #0b6e4f;
      --accent-soft: #d7ebe2;
      --rule: #c9d5cf;
      --card: rgba(255, 255, 255, 0.72);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-height: 100vh;
      font-family: "Source Sans 3", "Segoe UI", sans-serif;
      color: var(--fg);
      line-height: 1.5;
      background:
        radial-gradient(900px 480px at 0% 0%, #cfe8dc 0%, transparent 55%),
        radial-gradient(700px 420px at 100% 10%, #d9e3f0 0%, transparent 50%),
        linear-gradient(180deg, #eef3f0 0%, var(--bg) 45%, #e7eee9 100%);
    }}
    main {{
      max-width: 42rem;
      margin: 0 auto;
      padding: 4rem 1.5rem 3.5rem;
    }}
    p.brand {{
      margin: 0 0 0.85rem;
      font-size: 0.8rem;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      font-weight: 600;
      color: var(--accent);
      animation: rise 520ms ease both;
    }}
    h1 {{
      margin: 0 0 1rem;
      font-family: Fraunces, Georgia, serif;
      font-size: clamp(2.1rem, 5vw, 2.75rem);
      font-weight: 650;
      line-height: 1.15;
      letter-spacing: -0.02em;
      animation: rise 560ms ease 40ms both;
    }}
    .lede {{
      margin: 0 0 2rem;
      color: var(--muted);
      font-size: 1.08rem;
      max-width: 34rem;
      animation: rise 600ms ease 80ms both;
    }}
    h2 {{
      margin: 2.4rem 0 0.85rem;
      font-family: Fraunces, Georgia, serif;
      font-size: 1.35rem;
      font-weight: 650;
      letter-spacing: -0.01em;
    }}
    h3 {{
      margin: 0 0 0.55rem;
      font-size: 0.78rem;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      font-weight: 600;
      color: var(--accent);
    }}
    .steps {{
      margin: 0;
      padding: 0;
      list-style: none;
      background: var(--card);
      border: 1px solid var(--rule);
      backdrop-filter: blur(8px);
      animation: rise 640ms ease 120ms both;
    }}
    .steps li {{
      display: grid;
      grid-template-columns: 2rem 1fr;
      gap: 0.65rem;
      padding: 0.95rem 1.1rem;
      align-items: start;
    }}
    .steps li + li {{ border-top: 1px solid var(--rule); }}
    .steps .n {{
      font-family: Fraunces, Georgia, serif;
      font-weight: 650;
      color: var(--accent);
      line-height: 1.4;
    }}
    .steps a {{
      color: var(--accent);
      font-weight: 600;
      text-decoration: none;
      border-bottom: 1px solid transparent;
      transition: border-color 160ms ease;
    }}
    .steps a:hover {{ border-bottom-color: var(--accent); }}
    .catalog {{
      list-style: none;
      margin: 0;
      padding: 0;
      background: var(--card);
      border: 1px solid var(--rule);
      backdrop-filter: blur(8px);
      animation: rise 680ms ease 160ms both;
    }}
    .catalog li + li {{ border-top: 1px solid var(--rule); }}
    .catalog a {{
      display: block;
      padding: 1.05rem 1.15rem;
      color: var(--fg);
      text-decoration: none;
      transition: background 160ms ease, color 160ms ease;
    }}
    .catalog a:hover {{
      background: var(--accent-soft);
      color: var(--accent);
    }}
    .catalog a strong {{
      display: block;
      font-size: 1.05rem;
      font-weight: 600;
    }}
    .catalog a span {{
      display: block;
      margin-top: 0.3rem;
      font-size: 0.92rem;
      color: var(--muted);
    }}
    .tracks {{
      display: grid;
      gap: 1.25rem;
      animation: rise 720ms ease 200ms both;
    }}
    @media (min-width: 640px) {{
      .tracks {{ grid-template-columns: 1fr 1fr; }}
    }}
    .track {{
      background: var(--card);
      border: 1px solid var(--rule);
      padding: 1rem 1.1rem 1.05rem;
      backdrop-filter: blur(8px);
    }}
    ul.roadmap {{
      list-style: none;
      margin: 0;
      padding: 0;
    }}
    ul.roadmap li {{
      padding: 0.55rem 0;
      font-size: 0.95rem;
      color: var(--fg);
    }}
    ul.roadmap li + li {{ border-top: 1px solid var(--rule); }}
    ul.roadmap .id {{
      font-weight: 600;
      color: var(--accent);
      margin-right: 0.25rem;
    }}
    ul.roadmap em {{
      display: block;
      margin-top: 0.2rem;
      font-style: normal;
      font-size: 0.86rem;
      color: var(--muted);
    }}
    footer {{
      margin-top: 2.75rem;
      padding-top: 1.25rem;
      border-top: 1px solid var(--rule);
      color: var(--muted);
      font-size: 0.9rem;
      animation: rise 760ms ease 240ms both;
    }}
    footer a {{
      color: var(--accent);
      font-weight: 600;
      text-decoration: none;
    }}
    footer a:hover {{ text-decoration: underline; }}
    @keyframes rise {{
      from {{ opacity: 0; transform: translateY(0.45rem); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}
    @media (prefers-reduced-motion: reduce) {{
      * {{ animation: none !important; transition: none !important; }}
    }}
  </style>
</head>
<body>
  <main>
    <p class="brand">UofT ASIC Team</p>
    <h1>Education</h1>
    <p class="lede">
      Async, hands-on modules for undergraduates — from first tools to GDSII —
      using an open-source toolchain. Start with the shared workspace, then IC101.
    </p>

    <h2>Start here</h2>
    <ol class="steps">
      <li>
        <span class="n">1</span>
        <span>Clone the shared <a href="{workspace}">workspace</a> once (Docker + IIC-OSIC-TOOLS). Later courses drop into <code>modules/</code> via <code>mod add</code>.</span>
      </li>
      <li>
        <span class="n">2</span>
        <span>Complete <a href="{course_url('ic101')}">IC101 — Onboarding onto Tools</a>.</span>
      </li>
      <li>
        <span class="n">3</span>
        <span>Pick Analog or Digital below and work through courses in order.</span>
      </li>
    </ol>

    <h2>Available now</h2>
    <ul class="catalog">
{chr(10).join(live_items)}
    </ul>

    <h2>Roadmap</h2>
    <p class="lede" style="margin-bottom:1rem;font-size:1rem;animation:none;">
      Planned modules — titles only until each course site publishes.
    </p>
    <div class="tracks">
{chr(10).join(roadmap_blocks)}
    </div>

    <footer>
      Maintainers: stamp new courses from the
      <a href="{template}">course template</a>.
      Edit <code>data/courses.json</code> and run <code>python scripts/build.py</code> to refresh this hub.
    </footer>
  </main>
</body>
</html>
"""


def main() -> None:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    for c in data["courses"]:
        if c["status"] not in ("live", "planned"):
            raise SystemExit(f"invalid status for {c['id']}: {c['status']}")
        if c["track"] not in TRACK_ORDER:
            raise SystemExit(f"invalid track for {c['id']}: {c['track']}")
    OUT.write_text(render(data), encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
