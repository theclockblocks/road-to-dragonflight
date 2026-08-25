# HANDOFF — Deploy "The Road to Dragonflight" to GitHub Pages

## What this is
A static, fan-made World of Warcraft lore chronicle built for two WoW-newcomers:
14 chapters (birth of the cosmos → eve of the Dragonflight expansion) plus a
cross-referenced Codex of 118 characters, peoples, places, artifacts, and terms.
Chapters link into the Codex via `<a class="cx" href="codex.html#id">` links;
Codex entries link back to chapters. Every chapter cites its sources
(warcraft.wiki.gg + the Chronicle books).

## Repo layout
```
generator/          Python generator — the source of truth
  build.py          builds the site into ../docs, validates all cross-links first
  content_a.py      chapters I–VII   (list of dicts: slug/num/accent/era/title/sub/content/sources)
  content_b.py      chapters VIII–XIV
  codex_data.py     CODEX list of (id, name, category, description, [chapter numerals])
  visuals.py        APPEARANCE dict (one-sentence looks, prepended to codex entries in italics)
                    and WIKI dict (warcraft.wiki.gg article per entry, rendered as an
                    "Art & full article" link — the wiki page's infobox art is the visual
                    reference; do NOT embed Blizzard's images in the site itself)
  style_base.css    base stylesheet; build.py copies it and appends v2 additions
  codex_popup.js    copied to docs/codex-popup.js; opens codex entries in an
                    overlay instead of navigating away (see below)
docs/               the built site (16 HTML pages + style.css + .nojekyll) — serve this
```

## Deployment — live (updated 2026-08-25)

- **Live site:** https://theclockblocks.github.io/road-to-dragonflight/
- **Repo:** https://github.com/theclockblocks/road-to-dragonflight (public)
- **Pages source:** `main` branch, `/docs` folder.
- Collaborators: none, and none wanted — the intended readers don't have GitHub
  accounts, so the public link is the whole distribution plan.

To publish an update: edit the generator modules, run `python generator/build.py`,
then commit and push `docs/`. Pages rebuilds automatically on push to `main`.

**This repo has no `V1/` or `Site V2/` folders — do not add any.** GitHub Pages can
only serve `/` or `/docs` at the repo root, so a nested version folder cannot be
published. Versions live in git history instead: the pre-visual-layer site is
tagged **`v1`**. Start the next revision by editing in place; git holds the old one.

### Windows note — do not undo this
`build.py` must write its output as **UTF-8 with LF newlines** (all four `open()`
calls). Keep it that way. With the platform default codec, the script crashes
partway through the Codex on Windows (`UnicodeEncodeError` on `✦`, and now `↗`)
and leaves mojibake — `—` rendered as `?` — in the chapters it already wrote.
This has now regressed once: the V2 working copy was branched from a pre-fix
`build.py` and the fix had to be re-applied. If you hand a copy of this project to
another machine or another session, check those four `open()` calls first.

`.gitattributes` pins `* text=auto eol=lf` for the same reason: without it, a global
`core.autocrlf=true` makes every rebuild look like a full-file diff and hides real
content changes. A clean rebuild should be **byte-identical** to the committed
`docs/` — if it isn't, suspect encoding settings before content.

## Maintenance rules (for future sessions)
- **Never hand-edit files in `docs/`** except for trivial typo fixes the user asks for
  directly on GitHub. The generator is the source of truth: edit
  `content_a.py` / `content_b.py` / `codex_data.py`, then run
  `python3 generator/build.py` and commit the regenerated `docs/`.
- `build.py` validates before writing: duplicate codex ids, chapter links to missing
  codex ids, codex refs to missing chapters. It exits nonzero with a list of errors
  if anything is broken — fix the content modules, not the validator.
- New chapter = new dict in a content module (keep the accent color distinct; the
  homepage timeline gradient is generated from chapter order). New codex entry =
  new tuple in `codex_data.py`; link it from chapter text with
  `<a class="cx" href="codex.html#the-id">Name</a>`. Give it a one-sentence
  `APPEARANCE` line and a `WIKI` url in `visuals.py` too — `build.py` fails on a
  visuals key that matches no codex id, and reports any entry missing a wiki link.
  Describe the art in prose; never embed Blizzard's images in the site.
- Audience is WoW-oblivious: plain language, explain everything, no unexplained
  jargon. No FFXIV references anywhere on the site (user's explicit request).
- The Codex popup (`codex_popup.js`) is **progressive enhancement, and must stay that
  way**: every codex link keeps a real `href="codex.html#id"`. The script intercepts
  the click, fetches `codex.html` once, and shows the entry in a `<dialog>`; if JS is
  off, the fetch fails, or `<dialog>` is unsupported, the link just navigates as it
  always did. Never replace those hrefs with `#` or a JS-only handler — that would
  make the Codex unreachable for anyone the script doesn't run for.
  It deliberately ignores links with a `target` (the wiki links) and modifier-clicks,
  so open-in-new-tab keeps working, and it only matches `codex.html#...`, so the
  `#cat-XX` category jumps are untouched.
- `build.py` writes `style.css` and `codex-popup.js` **before** it generates the
  pages, hashes them, and references them as `style.css?v=<hash>`. Keep that order —
  the pages need the hashes. Pages serves assets with `max-age=600` and phones cache
  them longer, so without the hash a CSS change can sit unseen behind a stale copy
  for a long time. The hash is content-derived, so rebuilds stay byte-stable.
- Mobile layout: keep the document from ever being wider than the viewport. The
  chapter nav is 15 links and has to scroll inside itself (`min-width: 0` plus
  `overflow-x: auto`); when it stretched the page instead, the page panned sideways
  and dragged the fixed popup off-screen. If something looks clipped on a phone,
  check `document.documentElement.scrollWidth` against `innerWidth` first.
- Chapter XIV's spoiler content stays inside the `<details class="spoiler">` block.
- Content accuracy matters to the user: for new lore claims, verify against
  warcraft.wiki.gg and add the page to that chapter's `sources` list.
