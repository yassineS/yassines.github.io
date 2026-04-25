# CLAUDE.md

Project context for Claude Code working in this repo.

## What this is

Personal academic website for Yassine Souilmi, built with **Hugo** using the **hextra** theme. Deployed via GitHub Pages (CNAME → ysouilmi.com). The active GitHub remote is `yassineS/yassines.github.io` (the `ysouilmi-website` URL is a redirect).

## Conventions

- Use **Australian/UK English** in all content, including titles, body copy, and code identifiers.
- Preserve existing code and logic when editing — make minimal changes.
- Be concise.

## Content layout

- `content/news/` — news posts. Each post is a directory `<slug>/` containing `index.md` plus any images referenced from the post.
- News post slug conventions:
  - `ms-YYYY-<short-name>` — manuscripts/publications
  - `media-YYYY-<outlet>-<topic>` — media coverage
  - `talk-YYYY-<event>` — talks/conferences
- `content/publications/`, `content/research/`, etc. — other site sections.
- `layouts/shortcodes/` — custom Hugo shortcodes (e.g. `image-text-wrap`).

## Paper announcement style

Existing posts in `content/news/ms-*` are the template. Standard structure:

1. Frontmatter: `title` (prefixed `New Publication: ...`), `date` (publication date), `draft: false`.
2. Optional `{{< image-text-wrap src="..." >}}` lead paragraph with a figure.
3. One-paragraph framing of the paper and its significance.
4. `<!--more-->` break.
5. **Do not** include the journal abstract verbatim — paraphrase or summarise instead.
6. `## Key Findings` — bullet list with **bolded** lead phrases.
7. `## Significance` — short prose section.
8. `## Data Availability` — links to SRA/ENA/Zenodo/GitHub as relevant.
9. Footer: link to the paper, journal, volume/issue, publication date, DOI.

## Building / previewing

- `hugo server` for local preview.
- `hugo` to build into `public/`.

## Deploy

Pushed to `master` on the GitHub Pages repo; deployment is handled by GitHub.
