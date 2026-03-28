# CLAUDE.md

## Overview

This is a Jekyll-based slideshow application built on [reveal.js](https://github.com/hakimel/reveal.js/). It was originally a GitHub Learning Lab course repository ("Introducing GitHub") that teaches Git/GitHub basics through an interactive slideshow. Slides are authored as Jekyll posts and rendered as a reveal.js presentation.

## Repository Structure

```
github-slideshow/
├── _config.yml          # Jekyll configuration + reveal.js settings
├── _posts/              # Slide content (one .md file per slide)
├── _layouts/
│   ├── presentation.html  # Full slideshow layout (wraps all slides)
│   ├── slide.html         # Single slide layout (for standalone viewing)
│   └── print.html         # Print/PDF export layout
├── _includes/
│   ├── head.html          # HTML <head>: CSS links, reveal.js theme
│   ├── slide.html         # Template for rendering each slide <section>
│   └── script.html        # reveal.js JS initialization
├── index.html             # Entry point: iterates posts, includes slide.html
├── node_modules/reveal.js/ # reveal.js library (npm dependency)
├── Gemfile                # Ruby gems (github-pages, html-proofer)
├── script/
│   ├── cibuild            # CI build + HTML proofing
│   ├── server             # Local dev server
│   ├── setup              # One-time environment setup
│   └── stage              # Deploy to internal staging (GHE)
├── .editorconfig          # Code style rules
└── .gitignore             # Ignores _site/, .sass-cache/, .bundle/
```

## How Slides Work

1. Each `.md` file in `_posts/` becomes one slide. Files must use the Jekyll post naming convention (`YYYY-MM-DD-title.md`), but use a dummy date like `0000-01-01` since ordering is the only concern.
2. `index.html` iterates `site.posts` in reverse order (so higher dates appear later) and includes `_includes/slide.html` for each post.
3. `_includes/slide.html` wraps each post's content in a `<section>` element (reveal.js slide unit).
4. The `_layouts/presentation.html` layout places everything inside the reveal.js `.reveal > .slides` DOM structure.

### Slide Front Matter

```yaml
---
layout: slide
title: "Slide Title"
slide-id: optional-anchor-id      # optional: sets id="" on the <section>
classes:                           # optional: adds CSS classes to <section>
  - my-class
data:                              # optional: adds data-* attributes to <section>
  - [background, "#ff0000"]
---
Slide content here (Markdown or HTML)
```

- Omit `title` or set it to `""` to suppress the `<h1>` heading.
- The default CSS class is `slide`; override with `classes`.

## Development Workflow

### Setup

```sh
script/setup
```

Installs Ruby gems and initializes git submodules. On macOS it also runs `brew bundle` if a Brewfile is present.

### Local Development Server

```sh
script/server
# or directly:
bundle exec jekyll serve
```

Visit `http://localhost:4000` to view the slideshow.

### Build & Validate (CI)

```sh
script/cibuild
```

Builds the site with `bundle exec jekyll build --baseurl "."` then runs `htmlproofer` on `_site/index.html` (empty alt attributes are ignored).

### Staging Deploy

```sh
script/stage [repo-name]
```

Builds with an alternate baseurl and force-pushes `_site/` to a `gh-pages` branch on an internal GHE staging server. Default repo is `caption-this`.

## Configuration (`_config.yml`)

Key settings to know:

| Key | Description |
|-----|-------------|
| `timezone` | Europe/Berlin |
| `markdown` | kramdown |
| `highlighter` | rouge |
| `permalink` | `/:title` |
| `plugins` | `jemoji` (GitHub emoji support) |
| `solarized.theme` | `dark` or `light` — controls `<html>` class |
| `reveal.*` | All reveal.js initialization options (transition, controls, progress, etc.) |
| `baseurl` | Commented out by default; uncomment for subdirectory deployments |

The `exclude` list in `_config.yml` prevents reveal.js's own docs/configs from being processed by Jekyll.

## Code Style

Per `.editorconfig`:

- **General files**: tabs, 4-space tab width, LF line endings, UTF-8, trim trailing whitespace
- **JSON, JS, CSS, SCSS, YML, HTML**: spaces, 2-space indent
- **Markdown**: spaces, 4-space indent, trailing whitespace preserved, newline at EOF

## Dependencies

### Ruby (Gemfile)
- `github-pages >= 207` — Jekyll + GitHub Pages compatible plugins
- `html-proofer >= 3.13.0` — HTML validation in CI
- `tzinfo-data` — timezone data for Windows platforms

### JavaScript (node_modules)
- `reveal.js` — presentation framework (CSS, JS, plugins: markdown, highlight, notes)

## Reveal.js Theme & Assets

CSS loaded in `_includes/head.html`:
- `node_modules/reveal.js/css/reset.css`
- `node_modules/reveal.js/css/reveal.css`
- `node_modules/reveal.js/css/theme/moon.css` (active theme)
- `node_modules/reveal.js/lib/css/monokai.css` (syntax highlighting)

PDF print styles are injected via a script that detects `?print-pdf` in the URL.

Reveal.js plugins initialized in `_includes/script.html`: `marked`, `markdown`, `highlight`, `notes`.

## Adding Slides

1. Create a new file in `_posts/` named `0000-01-NN-slug.md` (increment `NN` to control order, since posts are iterated in reverse).
2. Add the front matter block with `layout: slide` and a `title`.
3. Write slide content in Markdown below the front matter.
4. Run `script/server` to preview.

## Branch Conventions

- Primary branch: `main`
- Development branches use the pattern: `claude/<description>-<suffix>`

## CI Notes

- The CI script uses `--empty-alt-ignore` for htmlproofer, so images without alt text will not fail the build.
- The `_site/` directory is generated and must not be committed (it is in `.gitignore`).
