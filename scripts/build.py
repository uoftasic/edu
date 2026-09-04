#!/usr/bin/env python3
"""Generate the edu hub index.html from data/courses.json.

The palette, typefaces and masthead below are lifted from uoftasic.com's
assets/css/asic-theme.css so the hub reads as part of the same site. They are
copied rather than linked: the hub must not break if the main site reorganises
its CSS. If the brand changes, resync the :root block and the masthead markup.
"""

from __future__ import annotations

import html
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "courses.json"
OUT = ROOT / "index.html"

MARK = (
    '<svg class="mark" viewBox="0 0 13 13" role="img" aria-label="UofT ASIC" '
    'focusable="false"><path fill="currentColor" d="M6 0h1v1h-1zM5 1h1v1h-1zM6 1h1v1h-1z'
    'M7 1h1v1h-1zM2 2h1v1h-1zM5 2h1v1h-1zM6 2h1v1h-1zM7 2h1v1h-1zM10 2h1v1h-1zM2 3h1v1h-1z'
    'M3 3h1v1h-1zM5 3h1v1h-1zM6 3h1v1h-1zM7 3h1v1h-1zM9 3h1v1h-1zM10 3h1v1h-1zM2 4h1v1h-1z'
    'M3 4h1v1h-1zM4 4h1v1h-1zM5 4h1v1h-1zM6 4h1v1h-1zM7 4h1v1h-1zM8 4h1v1h-1zM9 4h1v1h-1z'
    'M10 4h1v1h-1zM0 5h1v1h-1zM2 5h1v1h-1zM3 5h1v1h-1zM4 5h1v1h-1zM5 5h1v1h-1zM6 5h1v1h-1z'
    'M7 5h1v1h-1zM8 5h1v1h-1zM9 5h1v1h-1zM10 5h1v1h-1zM12 5h1v1h-1zM0 6h1v1h-1zM1 6h1v1h-1z'
    'M2 6h1v1h-1zM3 6h1v1h-1zM4 6h1v1h-1zM5 6h1v1h-1zM6 6h1v1h-1zM7 6h1v1h-1zM8 6h1v1h-1z'
    'M9 6h1v1h-1zM10 6h1v1h-1zM11 6h1v1h-1zM12 6h1v1h-1zM1 7h1v1h-1zM2 7h1v1h-1zM3 7h1v1h-1z'
    'M4 7h1v1h-1zM5 7h1v1h-1zM6 7h1v1h-1zM7 7h1v1h-1zM8 7h1v1h-1zM9 7h1v1h-1zM10 7h1v1h-1z'
    'M11 7h1v1h-1zM3 8h1v1h-1zM4 8h1v1h-1zM5 8h1v1h-1zM6 8h1v1h-1zM7 8h1v1h-1zM8 8h1v1h-1z'
    'M9 8h1v1h-1zM4 9h1v1h-1zM5 9h1v1h-1zM6 9h1v1h-1zM7 9h1v1h-1zM8 9h1v1h-1zM6 10h1v1h-1z'
    'M6 11h1v1h-1zM6 12h1v1h-1z"/></svg>'
)

TRACKS = [
    ("Analog", "analog",
     "From a waveform on a screen to transistors you have drawn yourself."),
    ("Digital", "digital",
     "From a truth table to a hardened GDSII, and proof that it works."),
]


def url(cid):
    return "https://uoftasic.com/" + html.escape(cid) + "/"


def code_of(course):
    return course["id"].upper()


def name_of(course):
    """The part after the em dash, which is the course's actual name."""
    title = course["title"]
    for sep in ("—", "–", " - "):
        if sep in title:
            return title.split(sep, 1)[1].strip()
    return title


def levels_for(courses, track):
    """Group a track into prerequisite depth levels.

    Depth is the real structure: a course sits one level below whatever it
    requires. Two courses on the same level are genuine alternatives, which is
    why DD104 and the 200-level stretch courses render side by side - they all
    require DD103 and none requires another.
    """
    by_id = {c["id"]: c for c in courses}
    depth = {}

    def depth_of(cid):
        if cid in depth:
            return depth[cid]
        course = by_id.get(cid)
        if course is None or not course["prereqs"]:
            depth[cid] = 0
        else:
            depth[cid] = 1 + max(depth_of(p) for p in course["prereqs"])
        return depth[cid]

    grouped = defaultdict(list)
    for c in courses:
        if c["track"] == track:
            grouped[depth_of(c["id"])].append(c)
    return [grouped[d] for d in sorted(grouped)]


def step_html(c, slug):
    live = c["status"] == "live"
    inner = (
        '<span class="step__code">' + html.escape(code_of(c)) + '</span>'
        '<span class="step__name">' + html.escape(name_of(c)) + '</span>'
        '<span class="step__summary">' + html.escape(c["summary"]) + '</span>'
    )
    cls = "step step--" + slug + ("" if live else " step--planned")
    if live:
        return ('<li class="' + cls + '"><a class="step__link" href="' + url(c["id"]) + '">'
                + inner + '<span class="step__go" aria-hidden="true">&rarr;</span></a></li>')
    return ('<li class="' + cls + '"><div class="step__link">' + inner
            + '<span class="step__tag">planned</span></div></li>')


def track_html(label, slug, blurb, levels):
    rows = []
    for level in levels:
        steps = "".join(step_html(c, slug) for c in level)
        if len(level) > 1:
            # A level with more than one course is a genuine branch: they share a
            # prerequisite and none requires another, so they can be taken in any
            # order. Say so, or the vertical stack reads as a sequence.
            shared = sorted({p for c in level for p in c["prereqs"]})
            after = " and ".join(p.upper() for p in shared)
            rows.append(
                '      <li class="ladder__level ladder__level--fork">\n'
                '        <p class="ladder__fork">' + str(len(level))
                + ' ways on from ' + html.escape(after)
                + ' &mdash; take them in any order</p>\n'
                '        <ol class="ladder__row">' + steps + '</ol>\n'
                '      </li>'
            )
        else:
            rows.append(
                '      <li class="ladder__level">\n'
                '        <ol class="ladder__row">' + steps + '</ol>\n'
                '      </li>'
            )
    n_live = sum(1 for lv in levels for c in lv if c["status"] == "live")
    n_all = sum(len(lv) for lv in levels)
    return (
        '  <section class="track track--' + slug + '" aria-labelledby="track-' + slug + '">\n'
        '    <header class="track__head">\n'
        '      <h2 class="track__name" id="track-' + slug + '">' + html.escape(label) + '</h2>\n'
        '      <p class="track__blurb">' + html.escape(blurb) + '</p>\n'
        '      <p class="track__count"><span class="track__n">' + str(n_live) + '</span> of '
        + str(n_all) + ' open</p>\n'
        '    </header>\n'
        '    <ol class="ladder">\n' + "\n".join(rows) + '\n    </ol>\n'
        '  </section>'
    )


def render(data):
    courses = data["courses"]
    workspace = html.escape(data["workspace_url"])
    template = html.escape(data["template_url"])
    by_id = {c["id"]: c for c in courses}

    gate = by_id["ic101"]
    gate_cta = (
        '<a class="gate__cta" href="' + url(gate["id"]) + '">Begin &rarr;</a>'
        if gate["status"] == "live" else '<span class="step__tag">planned</span>'
    )
    tracks = "\n".join(
        track_html(label, slug, blurb, levels_for(courses, label))
        for label, slug, blurb in TRACKS
    )
    total_live = sum(1 for c in courses if c["status"] == "live")

    # Plain replacement, not str.format: the template carries a full CSS
    # stylesheet and every brace in it would have to be doubled.
    out = TEMPLATE
    for key, value in (
        ("MARK", MARK),
        ("tracks", tracks),
        ("total_live", str(total_live)),
        ("gate_code", html.escape(code_of(gate))),
        ("gate_name", html.escape(name_of(gate))),
        ("gate_summary", html.escape(gate["summary"])),
        ("gate_cta", gate_cta),
        ("workspace", workspace),
        ("template", template),
    ):
        out = out.replace("{" + key + "}", value)
    return out


TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Education &mdash; UofT ASIC</title>
<meta name="description" content="Self-paced courses that take you from no background to a chip design you hardened yourself, on the open-source tools the team uses.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,400..800&amp;family=IBM+Plex+Mono:wght@400;500&amp;family=Newsreader:ital,opsz,wght@0,6..72,400..700;1,6..72,400..700&amp;display=swap">
<style>
/* Tokens copied from uoftasic.com/assets/css/asic-theme.css - keep in sync. */
:root{
  --blue:#1E3765; --teal:#007FA3; --red:#DC4633; --purple:#6D247A; --yellow:#F1C500;
  --paper:#FFFFFF; --paper-2:#F2F4F7;
  --ink:#14171F; --ink-2:#4C5462; --ink-3:#828B9B;
  --rule:#DDE2EA; --rule-2:#ECEFF4;
  --sans:"Archivo",-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
  --serif:"Newsreader",Georgia,"Times New Roman",serif;
  --mono:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,monospace;
  --shell:1100px; --gutter:24px;
  /* Track accents, taken from the institutional secondaries. */
  --analog:var(--purple); --digital:var(--teal); --gate:var(--yellow);
}
*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans);
  font-size:16px;line-height:1.6;-webkit-font-smoothing:antialiased}
a{color:var(--blue)}
:focus-visible{outline:2px solid var(--blue);outline-offset:2px}
.shell{max-width:var(--shell);margin:0 auto;padding:0 var(--gutter) 88px}

.masthead{border-bottom:1px solid var(--rule);background:var(--paper)}
.masthead__inner{max-width:var(--shell);margin:0 auto;padding:16px var(--gutter);
  display:flex;align-items:center;justify-content:space-between;gap:24px}
.brand{display:flex;align-items:center;gap:10px;text-decoration:none;color:var(--ink);line-height:1}
.mark{width:26px;height:26px;color:var(--blue);flex:none;display:block}
.brand__name{font-weight:700;font-size:16px;letter-spacing:-.018em;white-space:nowrap}
.nav{display:flex;align-items:center;gap:24px;font-size:14px;font-weight:500}
.nav__link{display:inline-flex;align-items:center;padding:6px 0;line-height:1;
  color:var(--ink-2);text-decoration:none}
.nav__link:hover{color:var(--ink)}
.nav__link.is-current{color:var(--blue);box-shadow:inset 0 -2px 0 0 var(--blue)}
.nav__link--cta{background:var(--blue);color:var(--paper);padding:8px 15px;border-radius:2px}
.nav__link--cta:hover{background:#16294c;color:var(--paper)}

.hero{padding:64px 0 40px;border-bottom:1px solid var(--rule)}
.hero__eyebrow{font-family:var(--mono);font-size:12px;letter-spacing:.16em;
  text-transform:uppercase;color:var(--blue);margin:0 0 16px}
.hero h1{margin:0;font-size:clamp(38px,6vw,60px);line-height:1.03;font-weight:700;
  letter-spacing:-.028em;max-width:15ch}
.hero__lede{font-family:var(--serif);font-size:20px;line-height:1.55;color:var(--ink-2);
  max-width:56ch;margin:20px 0 0}
.hero__lede strong{color:var(--ink);font-weight:600}

.gate{margin:40px 0 0;border:1px solid var(--rule);border-left:4px solid var(--gate);
  border-radius:2px;background:var(--paper-2);display:grid;
  grid-template-columns:auto 1fr auto;gap:0 24px;align-items:center;padding:22px 26px}
.gate__badge{font-family:var(--mono);font-size:11px;letter-spacing:.14em;text-transform:uppercase;
  color:var(--ink-2);align-self:stretch;display:flex;align-items:center;
  border-right:1px solid var(--rule);padding-right:22px;margin:0}
.gate__body h2{margin:0 0 5px;font-size:22px;font-weight:700;letter-spacing:-.02em}
.gate__code{font-family:var(--mono);font-size:16px;font-weight:500;
  color:var(--blue);margin-right:10px;letter-spacing:0}
.gate__body p{margin:0;color:var(--ink-2);font-size:15.5px;max-width:62ch}
.gate__cta{background:var(--blue);color:var(--paper);text-decoration:none;padding:11px 20px;
  border-radius:2px;font-weight:600;font-size:15px;white-space:nowrap}
.gate__cta:hover{background:#16294c}

.fork-note{display:flex;align-items:center;gap:16px;margin:0;padding:30px 0 10px;
  color:var(--ink-3);font-family:var(--mono);font-size:11.5px;letter-spacing:.14em;
  text-transform:uppercase}
.fork-note::before,.fork-note::after{content:"";height:1px;background:var(--rule);flex:1}

.tracks{display:grid;grid-template-columns:1fr 1fr;gap:40px;margin:8px 0 0;align-items:start}
.track__head{padding:0 0 18px;border-bottom:2px solid currentColor}
.track--analog .track__head{color:var(--analog)}
.track--digital .track__head{color:var(--digital)}
.track__name{margin:0;font-size:27px;font-weight:700;letter-spacing:-.02em;color:inherit}
.track__blurb{margin:7px 0 0;font-size:15px;color:var(--ink-2);max-width:44ch}
.track__count{margin:12px 0 0;font-family:var(--mono);font-size:11.5px;letter-spacing:.13em;
  text-transform:uppercase;color:var(--ink-3)}
.track__n{color:var(--ink);font-weight:500}

.ladder{list-style:none;margin:0;padding:0}
.ladder__level{position:relative;padding-top:24px}
.ladder__level::before{content:"";position:absolute;top:0;left:26px;width:2px;height:24px}
.track--analog .ladder__level::before{background:#c9b4cf}
.track--digital .ladder__level::before{background:#a8cddb}
.ladder__row{list-style:none;margin:0;padding:0;display:grid;gap:10px}

/* A branch: several courses off the same prerequisite, none before another.
   The bracket binds them; the caption says what the bracket means. */
.ladder__fork{margin:0 0 10px 26px;padding:0 0 0 16px;font-family:var(--mono);font-size:11px;
  letter-spacing:.1em;text-transform:uppercase;color:var(--ink-3)}
.ladder__level--fork > .ladder__row{position:relative;padding-left:16px;margin-left:26px;
  border-left:2px solid var(--rule)}
.track--analog .ladder__level--fork > .ladder__row{border-left-color:#c9b4cf}
.track--digital .ladder__level--fork > .ladder__row{border-left-color:#a8cddb}
.ladder__level--fork > .ladder__row > .step::before{content:"";position:absolute;left:0;
  width:16px;height:2px;background:inherit}
.ladder__level--fork .step{position:relative}
.ladder__level--fork .step::before{content:"";position:absolute;left:-16px;top:26px;
  width:16px;height:2px;background:var(--rule)}
.track--analog .ladder__level--fork .step::before{background:#c9b4cf}
.track--digital .ladder__level--fork .step::before{background:#a8cddb}

.step__link{display:grid;grid-template-columns:auto 1fr auto;gap:4px 14px;
  align-items:baseline;text-decoration:none;color:inherit;border:1px solid var(--rule);
  border-radius:2px;padding:15px 17px;background:var(--paper)}
a.step__link:hover{border-color:var(--blue);background:var(--paper-2)}
.step__code{font-family:var(--mono);font-size:13px;font-weight:500;grid-row:1;color:var(--blue)}
.track--analog .step__code{color:var(--analog)}
.track--digital .step__code{color:var(--digital)}
.step__name{grid-row:1;font-weight:600;font-size:17px;letter-spacing:-.012em;color:var(--ink)}
.step__summary{grid-row:2;grid-column:2;font-size:14.5px;color:var(--ink-2);line-height:1.5}
.step__go{grid-row:1;grid-column:3;color:var(--ink-3);font-size:17px}
a.step__link:hover .step__go{color:var(--blue)}
.step__tag{grid-row:1;grid-column:3;font-family:var(--mono);font-size:10px;letter-spacing:.12em;
  text-transform:uppercase;color:var(--ink-3);border:1px solid var(--rule);border-radius:2px;
  padding:3px 7px;align-self:center}
.step--planned .step__link{background:transparent;border-style:dashed}
.step--planned .step__name{color:var(--ink-2)}
.step--planned .step__code{opacity:.7}

.tools{margin:64px 0 0;border-top:1px solid var(--rule);padding:34px 0 0;
  display:grid;grid-template-columns:1fr auto;gap:26px;align-items:center}
.tools h2{margin:0 0 7px;font-size:20px;font-weight:700;letter-spacing:-.018em}
.tools p{margin:0;color:var(--ink-2);font-size:15.5px;max-width:62ch}
.tools__links{display:flex;gap:10px;flex-wrap:wrap}
.btn{border:1px solid var(--rule);border-radius:2px;padding:10px 16px;text-decoration:none;
  font-size:14.5px;font-weight:500;color:var(--ink);white-space:nowrap;background:var(--paper)}
.btn:hover{border-color:var(--blue);color:var(--blue)}

.footer{border-top:1px solid var(--rule);background:var(--paper-2)}
.footer__inner{max-width:var(--shell);margin:0 auto;padding:28px var(--gutter);
  display:flex;align-items:center;justify-content:space-between;gap:20px;flex-wrap:wrap}
.footer__brand{display:flex;align-items:center;gap:10px;color:var(--ink-2);font-size:14px}
.footer__brand .mark{width:20px;height:20px;color:var(--ink-3)}
.footer__note{color:var(--ink-3);font-size:13.5px;margin:0}
.footer__note code{font-family:var(--mono);font-size:12.5px}

@media (max-width:860px){
  .tracks{grid-template-columns:1fr;gap:44px}
  .gate{grid-template-columns:1fr;gap:14px;padding:20px}
  .gate__badge{border-right:0;border-bottom:1px solid var(--rule);padding:0 0 12px}
  .tools{grid-template-columns:1fr}
  .nav{gap:14px;font-size:13px}
}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
</style>
</head>
<body>

<header class="masthead">
  <div class="masthead__inner">
    <a class="brand" href="https://uoftasic.com/">
      {MARK}
      <span class="brand__name">UofT ASIC</span>
    </a>
    <nav class="nav" aria-label="Primary">
      <a href="https://uoftasic.com/projects/" class="nav__link">Projects</a>
      <a href="https://uoftasic.com/blog/" class="nav__link">Writing</a>
      <a href="https://edu.uoftasic.com/" class="nav__link is-current" aria-current="page">Education</a>
      <a href="https://uoftasic.com/about/" class="nav__link">About</a>
      <a href="https://uoftasic.com/join/" class="nav__link nav__link--cta">Join</a>
    </nav>
  </div>
</header>

<main class="shell">

  <section class="hero">
    <p class="hero__eyebrow">Internal education</p>
    <h1>Learn to design a chip.</h1>
    <p class="hero__lede">Self-paced courses that start from no background and end with a
      layout you drew and a design you hardened &mdash; on the same open-source tools the
      team uses for real tapeouts. <strong>{total_live} courses are open now.</strong></p>
  </section>

  <section class="gate" aria-labelledby="gate-h">
    <p class="gate__badge">Start here</p>
    <div class="gate__body">
      <h2 id="gate-h"><span class="gate__code">{gate_code}</span>{gate_name}</h2>
      <p>{gate_summary} Every course below assumes it, so it is the one thing you have to
        do first.</p>
    </div>
    {gate_cta}
  </section>

  <p class="fork-note">Then pick a track</p>

  <div class="tracks">
{tracks}
  </div>

  <section class="tools">
    <div>
      <h2>One workbench, every course</h2>
      <p>Every course mounts into the same container &mdash; XSchem, ngspice, Magic, KLayout,
        Yosys and LibreLane, already configured against the SKY130 process. Set it up once in
        {gate_code} and never install a tool again.</p>
    </div>
    <div class="tools__links">
      <a class="btn" href="{workspace}">Workspace repo</a>
      <a class="btn" href="{template}">Course template</a>
    </div>
  </section>

</main>

<footer class="footer">
  <div class="footer__inner">
    <div class="footer__brand">
      {MARK}
      <span>UofT ASIC &mdash; Education</span>
    </div>
    <p class="footer__note">Edit <code>data/courses.json</code> and run
      <code>python scripts/build.py</code> to refresh this page.</p>
  </div>
</footer>

</body>
</html>
"""


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    OUT.write_text(render(data), encoding="utf-8")
    print("Wrote " + OUT.name)


if __name__ == "__main__":
    main()
