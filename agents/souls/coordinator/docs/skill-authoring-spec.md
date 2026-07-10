# SKILL.md authoring spec (for blueprint skills)

Authoritative format for every skill we publish in a blueprint, from the official
Anthropic Agent Skills docs (platform.claude.com/docs/en/agents-and-tools/agent-skills,
code.claude.com/docs/en/skills). Researched 2026-06-21 because our first blueprint
skills shipped malformed (no frontmatter). Every skill MUST pass this.

## Required frontmatter (YAML, at the very top)

```yaml
---
name: <kebab-case>
description: <what it does, then when to use it>
---
```

- `name` — REQUIRED. Max 64 chars. Lowercase `a-z`, digits, hyphens ONLY. No XML
  tags. No reserved words (`anthropic`, `claude`). Best practice: match the skill
  directory name; gerund or verb form both valid (`reviewing-code`, `review`).
- `description` — REQUIRED. Max 1024 chars, non-empty, no XML tags. It is injected
  into the system prompt and is the SOLE basis for discovery/triggering. MUST:
  - be THIRD PERSON (never "I can…" / "You can…")
  - state BOTH **what it does** AND **when to use it**, with concrete trigger words
  - Good: `Extract text and tables from PDF files... Use when working with PDFs or when the user mentions PDFs, forms, or document extraction.`
  - Bad: `Helps with documents` (vague, no triggers)
- Only `name` + `description` are part of the core spec. Do not invent other fields.

## Body

- Markdown, starts right after the closing `---`. Convention: a real `# Title`
  heading (NOT `# Skill: x`).
- Under 500 lines.
- Do NOT repeat "when to use" in the body — the frontmatter description covers it.
- Concrete examples over abstract prose. ONE consistent term per concept.
- Forward-slash paths only. No time-sensitive info. No XML tags.
- Progressive disclosure: put deep detail in sibling files referenced ONE level
  deep from SKILL.md; Claude loads them on demand.

## What makes a skill fail to fire

Vague description; missing trigger keywords; first/second-person voice; wrong
filename (must be exactly `SKILL.md`); broken reference paths; deeply nested refs.

## Validate before publishing

- YAML parses: `python3 -c "import yaml,sys; yaml.safe_load(...)"` on the frontmatter.
- `name` <= 64, lowercase+digits+hyphens, not reserved.
- `description` non-empty, <= 1024, third person, what + when, no XML.
- Exactly one `SKILL.md` at the skill dir root; body < 500 lines.
- Functional: drop in `.claude/skills/<name>/`, confirm it appears under `/` and
  auto-triggers on a matching request.

There is no official linter/schema; the runtime enforces the name/description
limits and rejects on load.
