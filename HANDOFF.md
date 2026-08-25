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
  style_base.css    base stylesheet; build.py copies it and appends v2 additions
docs/               the built site (16 HTML pages + style.css + .nojekyll) — serve this
```

## Deployment — done (2026-08-25)

- **Live site:** https://theclockblocks.github.io/road-to-dragonflight/
- **Repo:** https://github.com/theclockblocks/road-to-dragonflight (public)
- **Pages source:** `main` branch, `/docs` folder. First build succeeded on commit `48e08af`.
- Collaborators: none added yet.

To publish an update: edit the generator modules, run `python generator/build.py`,
then commit and push `docs/`. Pages rebuilds automatically on push to `main`.

### Windows note
`build.py` writes its output explicitly as **UTF-8 with LF newlines**. Keep it that
way. Before this was pinned, the script used the platform default codec, so on
Windows it crashed partway through the Codex (`UnicodeEncodeError` on `✦`) and left
mojibake — `—` rendered as `?` — in the chapter files it had already written.
`.gitattributes` pins `* text=auto eol=lf` for the same reason: without it, the
global `core.autocrlf=true` makes every rebuild look like a full-file diff.
A clean rebuild should be **byte-identical** to the committed `docs/` — if it isn't,
something is wrong with the encoding settings, not the content.

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
  `<a class="cx" href="codex.html#the-id">Name</a>`.
- Audience is WoW-oblivious: plain language, explain everything, no unexplained
  jargon. No FFXIV references anywhere on the site (user's explicit request).
- Chapter XIV's spoiler content stays inside the `<details class="spoiler">` block.
- Content accuracy matters to the user: for new lore claims, verify against
  warcraft.wiki.gg and add the page to that chapter's `sources` list.
