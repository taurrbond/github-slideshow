# CLAUDE.md — github-slideshow

## Project Overview

A GitHub Learning Lab interactive slideshow built with **Jekyll** and **reveal.js**. Used to teach Git and GitHub concepts through a self-paced presentation hosted on GitHub Pages.

## Stack

| Layer | Technology |
|---|---|
| Static site generator | [Jekyll](https://jekyllrb.com/) (Ruby) |
| Presentation engine | [reveal.js](https://revealjs.com/) |
| Templating | Liquid |
| Styling | SCSS (compressed) |
| Syntax highlighting | Rouge (via Kramdown) |
| Dependency management | Bundler (`Gemfile`) |
| Hosting | GitHub Pages |

## Project Structure

```
.
├── _config.yml          # Jekyll + reveal.js configuration
├── _includes/           # Reusable Liquid partials
├── _layouts/            # Page layout templates
├── _posts/              # Slide content (Markdown)
├── index.html           # Entry point / presentation shell
├── script/              # Utility scripts (cibuild, server, setup, stage)
├── Gemfile              # Ruby dependencies
└── .claude/             # Claude Code configuration (this folder)
```

## Building & Running

```bash
# Install dependencies
bundle install

# Serve locally with live reload
bundle exec jekyll serve

# Production build
bundle exec jekyll build

# Run HTML link checker
bundle exec htmlproofer ./_site
```

## Code Style

- **Ruby**: Follow standard Ruby conventions; 2-space indentation.
- **HTML/Liquid**: 2-space indentation; keep templates readable.
- **SCSS**: BEM naming where applicable; avoid deep nesting (max 3 levels).
- **Markdown**: ATX-style headings (`#`); blank line before/after code blocks.
- **Commit messages**: imperative mood, present tense (`Add slide`, `Fix layout`).

## Testing

```bash
bundle exec htmlproofer ./_site --disable-external
```

Run `bundle exec jekyll build` first, then htmlproofer against `_site/`.

## Agent Instructions

- Always prefer editing existing files over creating new ones.
- Do not add comments that explain what code does — only add comments for non-obvious WHY.
- Do not modify `Gemfile.lock` manually; let `bundle install` handle it.
- Do not touch `.env` files or any secrets.
- When adding slides, follow the existing `_posts/` filename convention: `YYYY-MM-DD-title.md`.
- Before editing `_config.yml`, check reveal.js docs for valid option values.
- Do not run `curl`, `wget`, `rm -rf`, or any destructive shell commands.
- Run `bundle exec jekyll build` to verify changes compile before committing.

## /init Command

To regenerate this CLAUDE.md file run:

```
/init
```

This re-reads the project structure and rewrites `.claude/CLAUDE.md` with fresh content.
