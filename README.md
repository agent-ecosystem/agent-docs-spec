# Agent-Friendly Documentation Spec

A proposed specification for the documentation community to codify what makes
docs agent-friendly. The spec focuses on meeting the technical constraints of
agent platforms (truncation limits, content negotiation, discovery); it does not
consider qualitative evaluation of content.

**Status**: Draft (v0.1.0)

**Full spec**: [SPEC.md](SPEC.md) | **Website**: [agentdocsspec.com](https://agentdocsspec.com)

## The Problem

Coding agents (Claude Code, Cursor, GitHub Copilot, and others) increasingly
fetch documentation during development workflows. But most documentation sites
were built for human readers, and agent access patterns are fundamentally
different:

- Agents retrieve URLs from training data instead of navigating your site
- Web fetch pipelines silently truncate content (Claude Code at ~100K chars;
  the MCP Fetch reference server at just 5K chars by default)
- HTML-to-markdown conversion is lossy, and inline CSS can consume the
  entire truncation budget before content even starts
- Most agents don't know about `llms.txt` or `.md` URL variants unless told
- Cross-host redirects and JavaScript redirects break agent access entirely

The result: agents frequently fail to get the documentation content they need,
fall back on training data, or silently work with partial information.

## What the Spec Covers

The spec defines **21 checks across 8 categories**:

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
severity. See the [Checks Summary](SPEC.md#checks-summary) in the full spec.

## Quick Start for Documentarians

If you can only do a few things, these have the highest impact:

1. **Create an `llms.txt`** under 50K characters. This is the single most
   effective discovery mechanism observed. ([How](SPEC.md#category-1-llmstxt))
2. **Serve markdown versions** of your pages via `.md` URLs or content
   negotiation. ([How](SPEC.md#category-2-markdown-availability))
3. **Keep pages under 50K characters** of content. Break up mega-pages.
   ([Why](SPEC.md#category-3-page-size-and-truncation-risk))
4. **Add an `llms.txt` pointer** to the top of every docs page.
   ([Example](SPEC.md#llms-txt-directive))
5. **Don't break your URLs.** Use same-host HTTP redirects if you must move
   content. ([Details](SPEC.md#category-5-url-stability-and-redirects))
6. **Monitor your agent-facing resources.** Keep `llms.txt` fresh, verify
   markdown parity, and check cache headers.
   ([Details](SPEC.md#category-7-observability-and-content-health))

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

This spec is open for community review. We welcome:

- **Feedback and discussion**: [Open an issue](https://github.com/agent-ecosystem/agent-docs-spec/issues)
- **Proposed changes**: Submit a pull request (open an issue first for
  significant changes)
- **Platform data**: If you know a platform's truncation limits, contribute to
  the [Known Platform Limits](SPEC.md#known-platform-limits) table
- **Real-world results**: If you've evaluated your docs against this spec,
  we'd love to hear what you found

## License

This work is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
