# Skill: code-review

Perform a structured code review of changed files according to team standards for this Jekyll/reveal.js project.

## Usage

```
/code-review
/code-review --focus=liquid
/code-review --focus=scss
```

## What to Review

### 1. Correctness
- Liquid syntax is valid (check `{% %}` and `{{ }}` tags are balanced and properly closed)
- YAML front matter in `_posts/` files has required fields: `layout`, `title`, `date`
- Jekyll `_config.yml` values match valid reveal.js option names and types
- No broken internal links or missing `_includes` partials

### 2. Code Style
- **Ruby**: 2-space indentation, no trailing whitespace
- **HTML/Liquid**: 2-space indentation; attributes on one line unless > 120 chars
- **SCSS**: BEM naming (`block__element--modifier`); max 3 levels of nesting
- **Markdown**: ATX headings (`#`), blank line before and after fenced code blocks
- **Commit messages**: imperative mood, present tense (e.g. `Add slide`, not `Added slide`)

### 3. Jekyll Conventions
- New slides live in `_posts/` with filename `YYYY-MM-DD-slug.md`
- Layouts are referenced by name, not path (`layout: slide`, not `layout: _layouts/slide.html`)
- Includes use `{% include filename.html %}` with variables passed as named params

### 4. Security & Hygiene
- No secrets, tokens, or `.env` values committed
- No `curl`, `wget`, or raw HTTP calls embedded in scripts
- External links in Markdown use HTTPS

### 5. Performance
- Images are referenced from CDN or `assets/` — no binary blobs > 200 KB committed
- SCSS avoids `@import` of large unused libraries

## Output Format

Report findings grouped by severity:

```
## Critical
- <file>:<line> — <issue>

## Warning
- <file>:<line> — <issue>

## Suggestion
- <file>:<line> — <note>
```

If nothing to report in a category, omit it. End with a one-line summary.

## Agent Instructions

1. Run `git diff main...HEAD` to get the changeset.
2. Read each changed file fully before commenting.
3. Apply the checklist above — report only real findings, not style opinions.
4. Do not suggest rewrites beyond what the task requires.
5. Do not auto-fix; report only. Auto-fix only if the user passes `--fix`.
