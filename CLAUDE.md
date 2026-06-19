# CLAUDE.md — AI Assistant Guide for github-slideshow

## Project Overview

This is a **Jekyll-based slideshow** built on top of [reveal.js](https://github.com/hakimel/reveal.js/). It was created as a GitHub Learning Lab activity for teaching Git and GitHub. Slides are authored as Jekyll posts and rendered into a reveal.js presentation.

The site is hosted via GitHub Pages at the path `/github-slideshow` (configured via `baseurl` in `_config.yml`).

---

## Repository Structure

```
github-slideshow/
├── _config.yml          # Jekyll configuration + reveal.js settings
├── _posts/              # Slide content (one .md file per slide)
├── _layouts/
│   ├── presentation.html  # Wraps entire slideshow in reveal.js div
│   ├── slide.html         # Single-slide layout (for standalone viewing)
│   └── print.html         # Print layout
├── _includes/
│   ├── slide.html         # Renders a single <section> from a post
│   ├── head.html          # HTML <head> with CSS/JS includes
│   └── script.html        # reveal.js initialization script
├── _sass/
│   ├── fa/                # Font Awesome SCSS
│   ├── solarized/         # Solarized syntax highlighting theme
│   ├── fonts.scss
│   └── mixin.scss
├── assets/
│   ├── css/style.css      # Compiled CSS (do not edit directly)
│   ├── fonts/             # FontAwesome and Droid Serif font files
│   └── js/                # jQuery
├── reveal.js/             # Git submodule — reveal.js presentation framework
├── script/
│   ├── setup              # Bootstrap local environment
│   ├── server             # Run local Jekyll server
│   ├── cibuild            # CI build + HTML validation
│   └── stage              # (staging helper)
├── Gemfile                # Ruby dependencies
├── circle.yml             # CircleCI configuration
├── index.html             # Presentation entry point (iterates _posts)
└── .editorconfig          # Code style rules
```

---

## How Slides Work

1. Each slide is a Markdown file in `_posts/` with a date-prefixed filename (e.g., `0000-01-01-intro.md`).
2. `index.html` iterates `site.posts` in reverse order and includes `_includes/slide.html` for each post, generating `<section>` elements.
3. reveal.js (`reveal.js/` submodule) handles the actual presentation rendering.

### Slide Front Matter

```yaml
---
layout: slide          # always "slide"
title: "Slide Title"   # displayed as <h1>; omit or set "" to hide
slide-id: my-id        # optional: sets id="my-id" on the <section>
classes:               # optional: extra CSS classes on the <section>
  - my-class
data:                  # optional: data-* attributes for reveal.js
  transition: fade
---

Slide content in Markdown here.
```

### Slide Ordering

Jekyll sorts posts by date (filename prefix). Since all slides use `0000-01-01`, ordering is by title/filename alphabetically. `index.html` uses `reversed` to show them in ascending order. To control ordering, use distinct date prefixes in filenames (e.g., `0000-01-01-first.md`, `0000-01-02-second.md`).

---

## Development Setup

### Prerequisites

- Ruby (see `.ruby-version` if present; CircleCI uses 2.3.1)
- Bundler

### Initial Setup

```sh
script/setup
```

This installs gem dependencies and initializes the `reveal.js` git submodule.

**Important:** Always run `git submodule update --init` after cloning or if `reveal.js/` appears empty.

### Local Server

```sh
script/server
# or directly:
bundle exec jekyll serve
```

The site serves at `http://localhost:4000/github-slideshow/` by default.

### CI Build

```sh
script/cibuild
```

Builds the Jekyll site with `baseurl` set to `"."` and runs `htmlproofer` against `_site/index.html` (with `--empty-alt-ignore`).

---

## Configuration (`_config.yml`)

Key settings to be aware of:

| Setting | Value | Notes |
|---|---|---|
| `baseurl` | `/github-slideshow` | Path prefix for all asset URLs |
| `markdown` | `kramdown` | Markdown processor |
| `highlighter` | `rouge` | Syntax highlighting |
| `plugins` | `jemoji` | GitHub-style emoji support |
| `solarized.theme` | `dark` | `dark` or `light` |
| `reveal.transition` | `linear` | Slide transition style |
| `slideNumber.format` | `c/t` | Shows "current/total" slide numbers |

To change the solarized theme, edit `solarized.theme` in `_config.yml` (not in SCSS directly).

---

## Code Style Conventions (`.editorconfig`)

| File type | Indent | Notes |
|---|---|---|
| `*.json`, `*.js`, `*.css`, `*.scss`, `*.yml`, `*.html` | 2 spaces | |
| `*.md`, `*.markdown` | 4 spaces | Trailing whitespace preserved; final newline required |
| All other files | 1 tab (4-wide) | |

All files: UTF-8, LF line endings.

---

## Git Submodule

`reveal.js/` is a git submodule pointing to `https://github.com/hakimel/reveal.js.git`.

- Do **not** directly modify files inside `reveal.js/`.
- To update reveal.js: `git submodule update --remote reveal.js` (then commit the updated ref).
- The following reveal.js files are excluded from Jekyll processing (see `_config.yml`'s `exclude` list): `test/`, `index.html`, `README.md`, `bower.json`, `Gruntfile.js`, `CONTRIBUTING.md`, `LICENSE`, `package.json`.

---

## Dependencies

- **`github-pages` gem (>= 198)**: Pins Jekyll and plugins to GitHub Pages-compatible versions.
- **`html-proofer` (>= 3.11.1)**: Used in CI to validate built HTML.
- **`tzinfo-data`**: Required for Windows platforms only.
- **`jemoji`**: Jekyll plugin for GitHub emoji (`:sparkles:` → ✨).

---

## CI (CircleCI)

Defined in `circle.yml`. Uses Ruby 2.3.1. Pipeline:
1. `script/setup` — install dependencies
2. `script/cibuild` — build site and run HTML proofer

---

## Key Conventions for AI Assistants

1. **Adding a new slide**: Create a new file in `_posts/` with a `YYYY-MM-DD-slug.md` filename and `layout: slide` front matter. Use date prefixes to control order.
2. **Do not edit `assets/css/style.css` directly** — it is generated. Edit SCSS in `_sass/` instead.
3. **Do not modify `reveal.js/`** — it is a third-party submodule.
4. **`baseurl` matters** — all internal links and asset paths must be prefixed with `{{ site.baseurl }}`.
5. **Reveal.js config lives in `_config.yml`** under the `reveal:` key — do not hardcode it in `_includes/script.html` unless adding a new option not supported by the config.
6. **The `exclude` list in `_config.yml`** prevents Jekyll from trying to process reveal.js's own HTML/config files — keep it up to date if new conflicting files appear.
7. **Branch for this session**: `claude/add-claude-documentation-FXrA2`
