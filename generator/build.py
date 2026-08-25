#!/usr/bin/env python3
"""Build the expanded Road to Dragonflight site: 14 chapters + codex + homepage, with link validation."""
import os, re, sys, shutil
from pathlib import Path
BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))
from content_a import CHAPTERS_A
from content_b import CHAPTERS_B
from codex_data import CODEX, CATS
from visuals import APPEARANCE, WIKI

CHAPTERS = CHAPTERS_A + CHAPTERS_B
OUT = str(BASE.parent / "docs")
os.makedirs(OUT, exist_ok=True)

# ---------------- validation ----------------
errors = []
ids = [c[0] for c in CODEX]
if len(ids) != len(set(ids)):
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    errors.append(f"duplicate codex ids: {dupes}")
idset = set(ids)
nums = [ch["num"] for ch in CHAPTERS]
numset = set(nums)

for ch in CHAPTERS:
    for m in re.finditer(r'codex\.html#([a-z0-9-]+)', ch["content"]):
        if m.group(1) not in idset:
            errors.append(f'chapter {ch["num"]}: link to missing codex id "{m.group(1)}"')

for (cid, name, cat, desc, refs) in CODEX:
    if cat not in {c[0] for c in CATS}:
        errors.append(f'codex {cid}: unknown category {cat}')
    for r in refs:
        if r not in numset:
            errors.append(f'codex {cid}: ref to missing chapter {r}')
    for m in re.finditer(r'codex\.html#([a-z0-9-]+)', desc):
        if m.group(1) not in idset:
            errors.append(f'codex {cid}: link to missing id {m.group(1)}')

if errors:
    print("VALIDATION FAILED:")
    for e in errors:
        print(" -", e)
    sys.exit(1)
for k in list(APPEARANCE) + list(WIKI):
    if k not in idset:
        errors.append(f"visuals.py references unknown codex id: {k}")
missing_wiki = [i for i in ids if i not in WIKI]
if errors:
    print("VALIDATION FAILED:")
    for e in errors:
        print(" -", e)
    sys.exit(1)
print(f"validation OK: {len(CHAPTERS)} chapters, {len(CODEX)} codex entries, all cross-references resolve")
print(f"appearance descriptions: {len(APPEARANCE)}; wiki links: {len(WIKI)}; entries without wiki link: {missing_wiki or 'none'}")

num_to_slug = {ch["num"]: ch["slug"] for ch in CHAPTERS}
num_to_title = {ch["num"]: ch["title"] for ch in CHAPTERS}

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700'
         '&family=Alegreya:ital,wght@0,400;0,500;0,700;1,400&display=swap" rel="stylesheet">')

def nav(current):
    parts = ['<nav><a class="brand" href="index.html">The Road to Dragonflight</a><span class="navlinks">']
    for ch in CHAPTERS:
        cls = ' class="here"' if ch["slug"] == current else ""
        parts.append(f'<a href="{ch["slug"]}.html"{cls} style="--a:{ch["accent"]}" title="{ch["title"]}">{ch["num"]}</a>')
    cls = ' class="here codexlink"' if current == "codex" else ' class="codexlink"'
    parts.append(f'<a href="codex.html"{cls} style="--a:#c9a45c">Codex</a>')
    parts.append('</span></nav>')
    return "".join(parts)

def shell(title, body, accent="#c9a45c"):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
{FONTS}
<link rel="stylesheet" href="style.css">
<script src="codex-popup.js" defer></script>
</head>
<body style="--accent:{accent}">
{body}
</body>
</html>"""

def prevnext(i):
    parts = []
    if i > 0:
        p = CHAPTERS[i-1]
        parts.append(f'<a class="pn prev" href="{p["slug"]}.html"><span class="pn-label">Previous</span><span class="pn-title">{p["num"]} · {p["title"]}</span></a>')
    else:
        parts.append('<a class="pn prev" href="index.html"><span class="pn-label">Back to</span><span class="pn-title">The Chronicle</span></a>')
    if i < len(CHAPTERS)-1:
        p = CHAPTERS[i+1]
        parts.append(f'<a class="pn next" href="{p["slug"]}.html"><span class="pn-label">Next</span><span class="pn-title">{p["num"]} · {p["title"]}</span></a>')
    else:
        parts.append('<a class="pn next" href="codex.html"><span class="pn-label">Finished</span><span class="pn-title">Browse the Codex</span></a>')
    return f'<div class="prevnext">{"".join(parts)}</div>'

def sources_block(srcs):
    items = "".join(f'<li><a href="{u}" target="_blank" rel="noopener">{t}</a></li>' for t, u in srcs)
    return ('<div class="sources"><span class="sources-tag">Sources &amp; further reading</span>'
            f'<ul>{items}</ul>'
            '<p class="sources-note">Primary canon for the ancient eras is the <em>World of Warcraft: Chronicle</em> book series (Blizzard/Dark Horse); the wiki pages above summarize and cite it alongside in-game material.</p></div>')

COLOPHON = '<footer class="colophon">A fan-made lore chronicle. Warcraft, World of Warcraft, and all related characters belong to Blizzard Entertainment. Text written for private reference; sources linked per chapter.</footer>'

# ---------------- chapter pages ----------------
for i, ch in enumerate(CHAPTERS):
    body = f"""{nav(ch["slug"])}
<header class="chapter-head">
  <p class="eyebrow"><span class="num">{ch["num"]}</span>{ch["era"]}</p>
  <h1>{ch["title"]}</h1>
  <p class="sub">{ch["sub"]}</p>
</header>
<main class="article">
{ch["content"]}
{sources_block(ch["sources"])}
{prevnext(i)}
</main>
{COLOPHON}"""
    with open(f'{OUT}/{ch["slug"]}.html', "w", encoding="utf-8", newline="\n") as f:
        f.write(shell(f'{ch["title"]} — The Road to Dragonflight', body, ch["accent"]))

# ---------------- codex page ----------------
by_cat = {c[0]: [] for c in CATS}
for entry in CODEX:
    by_cat[entry[2]].append(entry)

cat_secs = []
for code, label in CATS:
    entries = sorted(by_cat[code], key=lambda e: e[1].lower().replace("the ", ""))
    cards = []
    for (cid, name, cat, desc, refs) in entries:
        reflinks = " ".join(
            f'<a class="ref" href="{num_to_slug[r]}.html" title="{num_to_title[r]}">{r}</a>' for r in refs)
        look = APPEARANCE.get(cid)
        lookhtml = f'<p class="look">{look}</p>' if look else ""
        wiki = WIKI.get(cid)
        wikihtml = f' <a class="wiki" href="{wiki}" target="_blank" rel="noopener">Art &amp; full article ↗</a>' if wiki else ""
        cards.append(f'''<article class="codex-entry" id="{cid}">
<h3>{name}</h3>
{lookhtml}<p>{desc}</p>
<p class="refs"><span>Chapters:</span> {reflinks}{wikihtml}</p>
</article>''')
    cat_secs.append(f'<section class="codex-cat"><h2 id="cat-{code}">{label}</h2>{"".join(cards)}</section>')

cat_nav = " · ".join(f'<a href="#cat-{code}">{label}</a>' for code, label in CATS)

codex_body = f"""{nav("codex")}
<header class="chapter-head">
  <p class="eyebrow"><span class="num">✦</span>Reference index</p>
  <h1>The Codex</h1>
  <p class="sub">Every character, people, place, artifact, and term linked from the chapters — with the chapters where each appears. Underlined names throughout the site lead here; your browser's back button returns you to where you were reading.</p>
</header>
<main class="article codex">
<p class="codex-jump">{cat_nav}</p>
{"".join(cat_secs)}
</main>
{COLOPHON}"""
with open(f"{OUT}/codex.html", "w", encoding="utf-8", newline="\n") as f:
    f.write(shell("The Codex — The Road to Dragonflight", codex_body))

# ---------------- homepage ----------------
toc = []
for ch in CHAPTERS:
    toc.append(f"""<a class="entry" href="{ch['slug']}.html" style="--a:{ch['accent']}">
  <span class="entry-node"></span>
  <span class="entry-body">
    <span class="entry-era">{ch['era']}</span>
    <span class="entry-title"><span class="entry-num">{ch['num']}</span> {ch['title']}</span>
    <span class="entry-sub">{ch['sub']}</span>
  </span>
</a>""")

grad = ", ".join(ch["accent"] for ch in CHAPTERS)

home_body = f"""{nav("index")}
<header class="hero">
  <p class="eyebrow">A chronicle of Azeroth, from the birth of the cosmos to the Dragon Isles</p>
  <h1>The Road to<br>Dragonflight</h1>
  <p class="sub">Everything World of Warcraft never tells you in order — assembled, in order, in fourteen chapters. Written for readers starting from zero.</p>
</header>
<main class="article home">
<section class="howto">
<h2>How to read this</h2>
<p>Warcraft's storytelling problem isn't that the lore is bad — it's that it's scattered across three strategy games, ten expansions, a shelf of novels, and quest text nobody reads. This site assembles it into one continuous chronicle. Read front to back like a book, or jump around; every chapter stands on its own, and each carries its own era-color through the site.</p>
<p><strong>Underlined names are Codex links.</strong> Any character, place, or artifact you don't recognize is one click from its entry in <a href="codex.html">the Codex</a> — a full reference index — and your back button returns you to your place. Each chapter ends with its sources, so any claim can be chased upstream to the wikis and the <em>Chronicle</em> books.</p>
<p>If you only read three chapters before playing Dragonflight: <strong>III</strong> (who the Aspects and Incarnates are), <strong>XI</strong> (how the Aspects lost their power), and <strong>XIV</strong> (the table as the expansion opens).</p>
</section>
<section class="chronicle" style="--grad: linear-gradient(180deg, {grad})">
{"".join(toc)}
<a class="entry codex-promo" href="codex.html" style="--a:#c9a45c">
  <span class="entry-node"></span>
  <span class="entry-body">
    <span class="entry-era">Reference index</span>
    <span class="entry-title"><span class="entry-num">✦</span> The Codex</span>
    <span class="entry-sub">{len(CODEX)} entries — every character, people, place, artifact, and term, cross-referenced by chapter</span>
  </span>
</a>
</section>
<section class="tldr">
<h2>The five-minute version</h2>
<p>A baby god sleeps inside the planet, and everyone cosmic wants her. The Void hurled four eldritch parasites into the world to corrupt her in her sleep; the titans buried them and ordered the world; and the fallen titan Sargeras built an army of demons to burn every such world before the Void could win one. The titans' keepers raised five dragons as the world's permanent guardians — and the buried gods spent ten thousand years whispering one of them, the Earth-Warder, into becoming Deathwing, the world's own shield turned against it.</p>
<p>An ancient elf queen's bargain broke the first continent. A corrupted orc race was fired through a portal like a weapon. A golden prince chased a plague until it swallowed him, and his undead kingdom nearly ate the world. The demons came back twice more and were finally destroyed at their own doorstep — but their master left a sword in the planet on his way down. The factions fought a war over the god-blood that wound bled. A banshee queen tore open the sky, and the heroes chased her through the afterlife itself.</p>
<p>And then, for the first time in twenty years — quiet. Into that quiet, the dragons' ancient homeland relights its beacon. The five guardians, mortal now, their god-given purpose spent killing their own brother, fly home to find out who they are without it — just as the elemental dragons who refused the titans' gift in the first place break out of prison to ask them, pointedly, whether that purpose was ever theirs to begin with.</p>
<p><em>That's Dragonflight. Welcome home.</em></p>
</section>
</main>
{COLOPHON}"""
with open(f"{OUT}/index.html", "w", encoding="utf-8", newline="\n") as f:
    f.write(shell("The Road to Dragonflight — a Warcraft lore chronicle", home_body))

# ---------------- stylesheet ----------------
shutil.copy(str(BASE / "style_base.css"), f"{OUT}/style.css")
shutil.copy(str(BASE / "codex_popup.js"), f"{OUT}/codex-popup.js")
EXTRA = """
/* ---------- v2 additions: codex, sources, spoilers, cx links ---------- */

a.cx {
  color: inherit;
  text-decoration: underline;
  text-decoration-color: color-mix(in srgb, var(--accent) 65%, transparent);
  text-decoration-thickness: 1px;
  text-underline-offset: 3px;
}
a.cx:hover { color: var(--accent); text-decoration-color: var(--accent); }

.sources {
  margin-top: 3rem;
  padding: 1.1rem 1.3rem;
  background: var(--ink-2);
  border: 1px solid var(--line);
  border-radius: 6px;
  font-size: 0.92rem;
}
.sources-tag {
  display: block;
  font-family: "Cinzel", serif;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--muted);
  margin-bottom: 0.5rem;
}
.sources ul { margin: 0; padding-left: 1.1rem; }
.sources li { margin: 0.25rem 0; }
.sources a { color: color-mix(in srgb, var(--text) 75%, var(--accent)); }
.sources a:hover { color: var(--accent); }
.sources-note { color: var(--muted); font-style: italic; margin: 0.7rem 0 0; font-size: 0.85rem; }

details.spoiler {
  margin: 2rem 0;
  border: 1px solid color-mix(in srgb, var(--accent) 45%, var(--line));
  border-radius: 6px;
  background: var(--ink-2);
  overflow: hidden;
}
details.spoiler summary {
  cursor: pointer;
  padding: 0.85rem 1.2rem;
  font-family: "Cinzel", serif;
  font-size: 0.85rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: var(--accent);
}
details.spoiler summary:hover { background: color-mix(in srgb, var(--accent) 8%, transparent); }
details.spoiler[open] summary { border-bottom: 1px solid var(--line); }
details.spoiler > p { padding: 0 1.3rem; }
details.spoiler > p:last-child { padding-bottom: 1rem; }

.codex-jump {
  font-family: "Cinzel", serif;
  font-size: 0.8rem;
  letter-spacing: 0.06em;
  color: var(--muted);
  text-align: center;
}
.codex-jump a { color: var(--accent); text-decoration: none; }
.codex-jump a:hover { text-decoration: underline; }

.codex-cat h2 {
  font-size: 1.5rem;
  border-bottom: 1px solid var(--line);
  padding-bottom: 0.4rem;
}
.codex-entry {
  padding: 0.9rem 1.1rem;
  margin: 0.7rem 0;
  background: var(--ink-2);
  border: 1px solid var(--line);
  border-left: 3px solid color-mix(in srgb, var(--accent) 55%, transparent);
  border-radius: 5px;
  scroll-margin-top: 5rem;
}
.codex-entry:target {
  border-color: var(--accent);
  border-left-color: var(--accent);
  box-shadow: 0 0 18px color-mix(in srgb, var(--accent) 25%, transparent);
}
.codex-entry h3 {
  font-family: "Cinzel", serif;
  font-weight: 700;
  font-size: 1.05rem;
  margin: 0 0 0.35rem;
  color: var(--text);
}
.codex-entry p { margin: 0 0 0.4rem; font-size: 0.98rem; }
.codex-entry .refs { font-size: 0.8rem; color: var(--muted); margin: 0; }
.codex-entry .refs span {
  font-family: "Cinzel", serif;
  font-size: 0.68rem;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}
.codex-entry .refs a.ref {
  font-family: "Cinzel", serif;
  color: var(--accent);
  text-decoration: none;
  border: 1px solid color-mix(in srgb, var(--accent) 45%, transparent);
  border-radius: 3px;
  padding: 0.05rem 0.45rem;
  margin-left: 0.2rem;
}
.codex-entry .refs a.ref:hover { border-color: var(--accent); }

.codex-entry .look {
  font-style: italic;
  color: color-mix(in srgb, var(--text) 72%, var(--accent));
  font-size: 0.95rem;
  margin: 0 0 0.45rem;
}
.codex-entry .refs a.wiki {
  font-family: "Cinzel", serif;
  font-size: 0.72rem;
  color: var(--muted);
  text-decoration: none;
  margin-left: 0.6rem;
}
.codex-entry .refs a.wiki:hover { color: var(--accent); }

/* ---------- Codex popup ---------- */

dialog.cxpop {
  position: fixed;
  inset: 0;
  margin: auto;
  width: min(34rem, calc(100% - 2rem));
  padding: 0;
  border: 0;
  background: transparent;
  max-width: none;
  max-height: none;
  height: auto;
  overflow: hidden;   /* the UA gives dialog overflow:auto; .cxpop-body does the scrolling */
  color: var(--text);
}
dialog.cxpop::backdrop {
  background: color-mix(in srgb, var(--ink) 80%, black);
  backdrop-filter: blur(2px);
}
.cxpop-inner {
  display: flex;
  flex-direction: column;
  max-height: 80vh;
  background: var(--panel);
  border: 1px solid var(--line);
  border-left: 3px solid var(--accent);
  border-radius: 8px;
  box-shadow: 0 18px 50px rgba(0, 0, 0, 0.55);
  padding: 0.5rem 1.3rem 1rem;
}
@keyframes cxpop-rise {
  from { transform: translateY(14px); opacity: 0; }
  to   { transform: none; opacity: 1; }
}
dialog.cxpop[open] .cxpop-inner { animation: cxpop-rise 0.18s ease-out; }

.cxpop-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 2.2rem;
  margin: 0 -0.4rem 0.2rem;
}
.cxpop-back, .cxpop-close {
  background: none;
  border: 0;
  color: var(--muted);
  font-family: "Cinzel", serif;
  cursor: pointer;
  padding: 0.5rem 0.7rem;      /* generous tap target */
  line-height: 1;
}
.cxpop-back { font-size: 0.75rem; letter-spacing: 0.08em; }
.cxpop-close { font-size: 1.5rem; margin-left: auto; }
.cxpop-back:hover, .cxpop-close:hover { color: var(--accent); }

.cxpop-body { overflow-y: auto; outline: none; -webkit-overflow-scrolling: touch; }
.cxpop-wait { color: var(--muted); font-style: italic; margin: 0.5rem 0 1rem; }

/* the cloned entry is already inside the popup card — strip its own card */
.cxpop .codex-entry {
  border: 0;
  background: none;
  padding: 0;
  margin: 0;
  box-shadow: none;
}
.cxpop .codex-entry h3 { font-size: 1.15rem; margin-bottom: 0.4rem; }
.cxpop .codex-entry p { font-size: 1rem; }

.cxpop-foot {
  margin: 0.9rem 0 0;
  padding-top: 0.7rem;
  border-top: 1px solid var(--line);
  font-size: 0.78rem;
}
.cxpop-full {
  font-family: "Cinzel", serif;
  color: var(--muted);
  text-decoration: none;
  letter-spacing: 0.06em;
}
.cxpop-full:hover { color: var(--accent); }

/* Phones: a bottom sheet, thumb-reachable, instead of a centred box. */
@media (max-width: 700px) {
  dialog.cxpop {
    inset: auto 0 0 0;
    margin: 0;
    width: 100%;
  }
  .cxpop-inner {
    max-height: 85vh;
    border-radius: 14px 14px 0 0;
    border-left-width: 1px;
    border-top: 3px solid var(--accent);
    padding-bottom: max(1rem, env(safe-area-inset-bottom));
  }
  @keyframes cxpop-rise {
    from { transform: translateY(100%); }
    to   { transform: none; }
  }
}

nav .navlinks a.codexlink { letter-spacing: 0.1em; }
.chronicle::before { background: var(--grad, linear-gradient(180deg, #9a7bdc, #d9a84e)); }
.codex-promo { border-style: dashed; }
"""
with open(f"{OUT}/style.css", "a", encoding="utf-8", newline="\n") as f:
    f.write(EXTRA)

print("site built:", len(os.listdir(OUT)), "files")
