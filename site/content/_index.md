---
title: "Agent-Friendly Documentation Spec"
description: "A proposed specification for making documentation sites work well for coding agents."
---

Documentation sites are increasingly consumed by coding agents (Claude Code,
Cursor, GitHub Copilot, and others) rather than human readers. But most sites
weren't built for this access pattern. Agents hit truncation limits, get walls
of CSS instead of content, can't follow cross-host redirects, and don't know
about emerging discovery mechanisms like `llms.txt`.

The result: agents frequently fail to get the documentation they need, fall
back on training data, or silently work with partial information.

This spec defines **21 checks across 8 categories** that evaluate how well a
documentation site serves agent consumers.

| Category | Checks | What it evaluates |
|----------|--------|-------------------|
| llms.txt | 5 | Discovery index exists, is valid, fits in a single fetch, links resolve, links point to markdown |
| Markdown Availability | 2 | `.md` URL support, content negotiation via Accept headers |
| Page Size | 3 | Markdown size, HTML size (pre/post conversion), content start position |
| Content Structure | 3 | Tabbed content serialization blowup, section header quality, code fence validity |
| URL Stability | 2 | Soft 404 detection, redirect behavior |
| Agent Discoverability | 1 | Embedded directives pointing agents to `llms.txt` |
| Observability | 3 | `llms.txt` freshness, markdown/HTML content parity, cache header hygiene |
| Authentication | 2 | Auth gate detection, alternative access paths for gated content |

Each check has defined pass/warn/fail criteria, an automation level, and
severity.

**[Read the Full Spec](/spec/)**

## Quick Start for Documentarians

If you can only do a few things, these have the highest impact:

1. **Create an `llms.txt`** under 50K characters. This is the single most
   effective discovery mechanism observed.
2. **Serve markdown versions** of your pages via `.md` URLs or content
   negotiation.
3. **Keep pages under 50K characters** of content. Break up mega-pages.
4. **Add an `llms.txt` pointer** to the top of every docs page.
5. **Don't break your URLs.** Use same-host HTTP redirects if you must move
   content.
6. **Monitor your agent-facing resources.** Keep `llms.txt` fresh, verify
   markdown parity, and check cache headers.

## Background

This spec grew out of findings from two research articles on agent
documentation access patterns:

- [Agent-Friendly Docs](https://dacharycarey.com/2026/02/18/agent-friendly-docs/) -
  Observations from 10+ hours of validating 578 coding patterns with Claude,
  covering URL failure modes, `llms.txt` discovery, markdown benefits, and
  page truncation.
- [Agent Web Fetch Spelunking](https://dacharycarey.com/2026/02/19/agent-web-fetch-spelunking/) -
  Deep dive into how Claude Code's web fetch pipeline processes HTML and
  markdown, including the summarization model, truncation limits, and why
  inline CSS can make a 97-line HTML page invisible to agents.

## Contributing

This spec is open for community review. We welcome feedback, proposed changes,
platform data, and real-world results. See the
[GitHub repository](https://github.com/agent-ecosystem/agent-docs-spec) for details.

## License

This work is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
