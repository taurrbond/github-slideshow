# Skill: add-slide

Create a new slide in `_posts/` following the project's conventions.

## Usage

```
/add-slide "Slide title"
/add-slide "Slide title" --date=2026-07-04
```

## Steps

1. Determine the filename: `_posts/YYYY-MM-DD-slug.md`
    - Date: from `--date` if given, otherwise today.
    - Slug: lowercase title, spaces → hyphens, strip punctuation.
2. Check the file does not already exist; if it does, stop and report.
3. Create the file with this exact front matter shape (matches existing slides):

    ```markdown
    ---
    layout: slide
    title: "<Title>"
    ---

    <slide content goes here>
    ```

4. If the user supplied content, insert it; otherwise leave a one-line
   placeholder such as `New slide — content TBD.`
5. Run `bundle exec jekyll build` to confirm the site still compiles.
6. Report the created path and build result.

## Conventions

- Slides are ordered by date in the filename — earlier dates appear first
  in the deck (the intro slide uses `0000-01-01`).
- Use `<!-- .slide: data-background="..." -->` comments for per-slide
  reveal.js options, not custom HTML wrappers.
- Vertical sub-slides: separate with `<!-- .element: -->` fragments or
  create adjacent posts; do not nest `<section>` tags manually.
- Keep one concept per slide; prefer short bullet lists over paragraphs.
