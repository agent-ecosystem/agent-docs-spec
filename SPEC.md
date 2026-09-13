# Agent-Friendly Documentation Spec

|              |                                                              |
|--------------|--------------------------------------------------------------|
| **Status**   | Draft                                                        |
| **Version**  | 0.6.0                                                        |
| **Date**     | 2026-09-13                                                   |
| **Author**   | Dachary Carey + community contributors                       |
| **URL**      | https://agentdocsspec.com                                    |
| **Repository** | https://github.com/agent-ecosystem/agent-docs-spec                |
| **Reference Implementation** | [`afdocs`](https://afdocs.dev) · [npm](https://www.npmjs.com/package/afdocs) · [GitHub](https://github.com/agent-ecosystem/afdocs) |

## Abstract

Documentation sites are increasingly consumed by coding agents rather than
human readers, but most sites are not built for this access pattern. Agents
hit truncation limits, get walls of CSS instead of content, can't follow
cross-host redirects, and don't know about emerging discovery mechanisms like
`llms.txt`. This spec defines 28 checks across 7 categories that evaluate how
well a documentation site serves agent consumers. It is grounded in empirical
observation of real agent workflows and is intended as a shared standard for
documentation teams, tool builders, and platform providers.

## Scope

This spec targets **coding agents that fetch documentation during real-time
development workflows.** These are tools like Claude Code, Cursor, GitHub
Copilot, and similar IDE-integrated or CLI-based agents that a developer uses
while writing code. The agent fetches a docs page, extracts information, and
uses it to complete a task, all in a single session.

This spec does **not** target:

- **Training crawlers** (GPTBot, ClaudeBot, etc.) that scrape content for model
  training. These have different access patterns, different user-agents, and
  different concerns. See [Appendix B](#appendix-b-notable-exclusions).
- **Answer engines** (Perplexity, Google AI Overviews, ChatGPT search) that
  retrieve content to generate responses to user queries. These systems have
  their own retrieval pipelines that may or may not resemble the web fetch
  pipelines described here.
- **RAG pipelines** that pre-index documentation into vector stores. These
  retrieve at query time from an index built ahead of time, so truncation
  limits and real-time fetch behavior are less relevant. Their *ingestion*
  step is a different matter: it fetches from the site like any automated
  client, and many of this spec's checks serve it directly. See
  [Serving RAG Ingestion Pipelines](#serving-rag-ingestion-pipelines).

The findings and checks in this spec are grounded in empirical observation of
coding agents. Some recommendations (like providing `llms.txt` and serving
markdown) will benefit other consumers too, but the pass/warn/fail criteria
are calibrated for the coding agent use case.

### Related Surfaces

This spec covers the **delivery** of web-served documentation: whether agents
can discover, fetch, and receive content intact. Agent-friendly documentation
has at least two other surfaces, deliberately out of scope here and planned
as companion specifications as the evidence base for them matures:

- **Content composition**: what documentation should *contain* to serve
  agents well. Factual consistency across pages, structure and density
  suited to machine consumption, and how representation across a corpus
  shapes what agents effectively know about a product. These properties
  require semantic evaluation rather than the mechanical verification this
  spec's checks are built on.
- **Repository-local documentation**: docs serving a coding agent that
  works *inside* a repository (`README`, `docs/` directories, agent-facing
  instruction files). The agent discovers content with local tools (grep,
  find, directory listings) and consumes it through file reads, so almost
  none of the web spec's checks transfer: there is no fetch pipeline, no
  truncation-by-summarizer, and no llms.txt; greppability and file layout
  do the work that discovery checks do on the web.

Keeping these separate protects what makes each credible: this spec's checks
are mechanically verifiable against a live site, and that property should
not be diluted as adjacent guidance develops.

## Background

Agents don't use docs like humans. They retrieve URLs from training data rather
than navigating table-of-contents structures. They struggle with HTML-heavy
pages, lose content to truncation with no indication anything was cut, and
don't know about emerging
standards like `llms.txt` unless explicitly told. These checks codify the
patterns that empirically help or hinder agent access to documentation content.

## Terminology

- **Agent**: An LLM operating in an agentic coding workflow (e.g., Claude Code,
  Cursor, Copilot) that fetches and consumes documentation as part of a
  development task. See [Scope](#scope) for what this spec does and does not
  cover.
- **Web fetch pipeline**: The chain of processing between "agent requests a URL"
  and "model sees content." Typically involves HTTP fetch, HTML-to-markdown
  conversion, truncation, and sometimes a summarization model.
- **Trusted site**: A domain hardcoded into an agent platform's web fetch
  implementation that receives more favorable processing (e.g., bypassing
  summarization).
- **Truncation**: The silent removal of content that exceeds a platform's size
  limit. The agent receives partial content with no indication that anything
  was cut. See [Appendix A](#appendix-a-known-platform-truncation-limits) for
  known limits by platform.

## Conventions

This spec uses the following language to distinguish between requirements and
recommendations:

- **Must** / **Required**: The item is an absolute requirement of the spec.
  Used sparingly; most checks in this spec are recommendations rather than
  hard requirements, because agent-friendliness is a spectrum.
- **Should** / **Recommended**: The item is a strong recommendation. There may
  be valid reasons to deviate, but the implications should be understood.
- **May** / **Optional**: The item is genuinely optional. Implementing it
  provides additional benefit but omitting it is not a deficiency.

Sections of this spec are either **normative** (defining checks and their
pass/warn/fail criteria) or **informational** (providing context, evidence,
and recommendations). The distinction is noted where it matters:

- **Normative sections**: Category 1-7 check definitions, Checks Summary
  table.
- **Informational sections**: Background, Scope, Start Here, "How Agents Get
  Content", "Who Actually Uses llms.txt?", Progressive Disclosure
  recommendation, "Making Private Docs Agent-Accessible", Appendices.

The progressive disclosure pattern for `llms.txt` is a recommendation from
this spec, not a normative requirement. Sites that keep their `llms.txt` under
50,000 characters don't need it.

## Start Here: Top Recommendations

If you're a documentarian and can only do a few things, start with these. They
are ordered by impact based on observed agent behavior:

1. **Create an `llms.txt` that fits in a single agent fetch** (under 50K
   characters). This is the single highest-impact action. Agents that find an
   `llms.txt` navigate documentation dramatically better. If your docs set is
   large, use the [nested pattern](#progressive-disclosure-for-large-documentation-sets)
   to keep each file under the limit.
   Checks: `llms-txt-exists`, `llms-txt-size`

2. **Serve markdown versions of your pages.** Either via `.md` URL variants or
   content negotiation. Markdown is what agents actually want; HTML conversion
   is lossy and unpredictable.
   Checks: `markdown-url-support`, `content-negotiation`

3. **Keep pages under 50,000 characters of content.** If a page has tabbed or
   dropdown content that serializes into a massive blob, break it into separate
   pages or ensure the markdown version stays under the limit.
   Checks: `page-size-markdown`, `page-size-html`, `tabbed-content-serialization`

4. **Put a pointer to your `llms.txt` at the top of every docs page.** A simple
   blockquote directive that tells agents where to find the documentation index.
   Anthropic does this; it works. Include it in both the HTML DOM and in
   markdown versions of pages.
   Checks: `llms-txt-directive-html`, `llms-txt-directive-md`

5. **Don't break your URLs.** If you must move content, use same-host HTTP
   redirects. Avoid cross-host redirects, JavaScript redirects, and soft 404s.
   Checks: `http-status-codes`, `redirect-behavior`

6. **Monitor your agent-facing resources.** Treat `llms.txt` and markdown
   endpoints like any other production surface: check freshness, verify
   content parity with HTML, and ensure cache headers allow timely updates.
   Checks: `llms-txt-coverage`, `markdown-content-parity`,
   `cache-header-hygiene`

## Spec Structure

Each check has:

- **ID**: A short identifier (e.g., `llms-txt-exists`).
- **Category**: The area of agent-friendliness it evaluates.
- **What it checks**: A description of what the check evaluates.
- **Why it matters**: The observed agent behavior that motivates the check.
- **Result levels**: What constitutes a pass, warn, or fail.
- **Recommended action**: What to do to resolve a warn or failure state.
- **Automation**: Whether the check can be fully automated, partially automated
  (heuristic), or is advisory only.

The canonical source of this spec is a single document
([SPEC.md](https://github.com/agent-ecosystem/agent-docs-spec/blob/main/SPEC.md)
in the repository). The website serves it as per-category pages under
[agentdocsspec.com/spec/web/](https://agentdocsspec.com/spec/web/), following
this spec's own progressive disclosure recommendation: the full document
outgrew the 100,000-character truncation threshold its own checks are built
around, so it now practices what it prescribes. Each page stays well under
the 50,000-character pass threshold.

### Check Dependencies

Some checks depend on the results of others:

- `llms-txt-valid`, `llms-txt-size`, `llms-txt-links-resolve`, and
  `llms-txt-links-markdown` only run if `llms-txt-exists` passes.
- `page-size-markdown` only runs if `markdown-url-support` or
  `content-negotiation` passes (the site must serve markdown for this check
  to apply).
- `page-size-html` and `content-start-position` results should be flagged as
  unreliable if `rendering-strategy` fails (the measurements reflect a shell,
  not actual content).
- `section-header-quality` is most relevant when `tabbed-content-serialization`
  detects tabbed content.
- `markdown-code-fence-validity` only runs if `markdown-url-support` or
  `content-negotiation` passes (the site must serve markdown for this check
  to apply). It also runs against any discovered `llms.txt` files.
- `llms-txt-coverage` only runs if `llms-txt-exists` passes.
- `auth-alternative-access` only runs if `auth-gate-detection` returns warn
  or fail (the site must have auth-gated content for alternative access paths
  to be relevant).
- `bot-protection-interference` has no prerequisites, but it inverts the
  usual dependency direction: when it returns warn or fail, results from
  every multi-page check should be flagged as computed from a partial sample
  (see the [Bot Protection Degrading Scan Reliability](#bot-protection-degrading-scan-reliability)
  interaction effect). It is also evaluated from evidence gathered across the
  entire scan rather than run as a discrete Category 7 step.
- `markdown-content-parity` only runs if `markdown-url-support` or
  `content-negotiation` passes (the site must serve markdown for this check
  to apply).
- `single-fetch-completeness` and `markdown-link-portability` only run if
  `markdown-url-support` or `content-negotiation` passes (both evaluate
  properties of served markdown).

Implementations should run checks in category order (1 through 7) and skip
dependent checks when their prerequisites fail.

### A Note on Responsible Use

This spec describes checks that involve making HTTP requests to documentation
sites. Implementations should be respectful of the sites being evaluated:
introduce delays between requests, cap concurrent connections, honor
`Retry-After` headers, and avoid overwhelming sites with traffic. The goal is
to help documentation teams improve agent accessibility, not to load-test
their infrastructure.

---

## Category 1: Content Discoverability

These checks evaluate whether agents can find and navigate the site's
documentation content. This includes whether the site provides an `llms.txt`
file, whether that file is useful to agents, and whether documentation pages
include signals that direct agents to discovery resources.

### Location Discovery

The [llmstxt.org proposal](https://llmstxt.org) specifies that `llms.txt`
should be at the root path (`/llms.txt`), mirroring `robots.txt` and
`sitemap.xml`. In practice, the location varies significantly across sites:

| Site | Root `/llms.txt` | `/docs/llms.txt` | Notes |
|------|:-:|:-:|-------|
| MongoDB | 200 | 200 | Both locations, different content |
| Neon | 200 | 200 | Both locations |
| Stripe | 200 | 301 -> docs.stripe.com | Root + docs subdomain |
| Vercel | 200 | 308 -> root | Root only, /docs redirects |
| React | 200 | -- | Root only |
| GitHub Docs | 200 | -- | Root only |
| Claude Code | 302 -> product page | 200 | /docs only; root is not docs |
| Anthropic (old) | 301 -> 404 | -- | Moved domain, redirect breaks |

The proposal does not address whether sites should serve `llms.txt` at subpaths,
or whether a site with docs at `/docs/` should place it at `/docs/llms.txt` vs
`/llms.txt`. In practice, both patterns exist. Implementations should check
multiple candidate locations.

**Discovery algorithm**: Given a base URL, check for `llms.txt` at:

1. `{base_url}/llms.txt` (the exact URL the user provided, plus llms.txt)
2. `{origin}/llms.txt` (site root, per the proposal)
3. `{origin}/docs/llms.txt` (common docs subpath)

Where `{origin}` is the scheme + host of the base URL, and `{base_url}` is
the full URL the user provided (which might be `https://example.com/docs` or
`https://example.com` or `https://docs.example.com`). Duplicate URLs are
deduplicated before checking.

For each location, record whether `llms.txt` exists and whether the response
involved a redirect (and if so, what kind). All subsequent llms.txt checks run
against every discovered `llms.txt` file.

### `llms-txt-exists`

- **What it checks**: Whether `llms.txt` is discoverable at any of the candidate
  locations described above.
- **Why it matters**: `llms.txt` was the single most effective discovery
  mechanism observed. When agents found one, it fundamentally changed their
  ability to navigate a documentation site. Agents don't know to look for
  `llms.txt` by default, but when pointed at one, they treat it as a primary
  navigation resource.
- **Result levels**:
  - **Pass**: `llms.txt` exists at one or more candidate locations, returning
    200 with text content (direct or after same-host redirect).
  - **Warn**: `llms.txt` exists but is only reachable via cross-host redirect
    (agents may not follow it).
  - **Fail**: `llms.txt` not found at any candidate location.
- **Recommended action**:
  - **Warn**: Serve `llms.txt` directly from the same host as your
    documentation, or use a same-host redirect. Cross-host redirects are
    not followed by some agents.
  - **Fail**: Create an `llms.txt` file at your site root containing an H1
    title, a blockquote summary, and markdown links to your key documentation
    pages. This is the single highest-impact improvement for agent access.
- **Automation**: Full.
- **Report details**: List all candidate URLs checked and their status
  (200, 404, redirect chain). When multiple locations return `llms.txt`, note
  whether they serve the same or different content.

### `llms-txt-valid`

- **What it checks**: Whether the `llms.txt` follows the structure described in
  the [llmstxt.org proposal](https://llmstxt.org). The proposal specifies:
  - An H1 with the project/site name.
  - A blockquote with a short summary.
  - H2-delimited sections containing markdown link lists.
  - Each link entry: `[name](url)` optionally followed by `: description`.
  - An optional H2 "Optional" section for secondary content.
  - Optional companion file `llms-full.txt` with complete content.
- **Why it matters**: A well-structured `llms.txt` gives agents a reliable map
  of the documentation. Inconsistent implementations reduce its value. That
  said, even a non-standard `llms.txt` that contains useful links is better
  than nothing.
- **Result levels**:
  - **Pass**: Follows the proposed structure with H1, summary blockquote, and
    heading-delimited link sections.
  - **Warn**: Contains parseable markdown links but doesn't follow the proposed
    structure (still useful, just non-standard).
  - **Fail**: Exists but contains no parseable links, or is empty.
- **Recommended action**:
  - **Warn**: Add an H1 title as the first line and a blockquote summary
    (lines starting with `>`) to improve agent parsing.
  - **Fail**: Add links in `[name](url): description` format under
    heading-delimited sections.
- **Automation**: Full.
- **Checks in detail**:
  - H1 present (first line starts with `# `).
  - Blockquote summary present (line starting with `> `).
  - At least one heading-delimited section with markdown links.
  - Links follow `[name](url)` format.
  - Optional: check for `llms-full.txt` companion file.
- **Notes on heading levels**: The llmstxt.org proposal specifies H2 (`##`) for
  section delimiters. In practice, some implementations (notably MongoDB) use
  H1 (`#`) for sections instead. Implementations should accept any heading
  level for section delimiters when evaluating structure. The important thing
  is that sections exist and contain parseable links, not that they use a
  specific heading level.

### `llms-txt-links-resolve`

- **What it checks**: Whether the URLs listed in `llms.txt` actually resolve
  (return 200).
- **Why it matters**: A stale `llms.txt` with broken links is worse than no
  `llms.txt` at all. It sends agents down dead ends with high confidence.
- **Result levels**:
  - **Pass**: All links resolve (200, following same-host redirects).
  - **Warn**: >90% of links resolve.
  - **Fail**: <=90% of links resolve.
- **Recommended action**: Audit and fix or remove broken URLs. A stale
  `llms.txt` with broken links is worse than no `llms.txt` at all because
  it sends agents down dead ends with high confidence.
- **Automation**: Full.
- **Notes**: Requires making HTTP requests to each URL. For large files,
  implementations may choose to test a random subset rather than every link.

### `llms-txt-size`

- **What it checks**: The character count of the `llms.txt` file, and whether
  it exceeds the truncation limits of known agent web fetch pipelines.
- **Why it matters**: An `llms.txt` that exceeds an agent's truncation limit
  defeats its own purpose. The agent sees only a fraction of the index and
  may miss the section it needs entirely. This is the same truncation problem
  that affects documentation pages, but arguably worse because `llms.txt` is
  supposed to be the *solution* to discovery.

  Real-world sizes vary enormously:

  | Site | Size | Links | Notes |
  |------|------|-------|-------|
  | MongoDB `/docs/llms.txt` | 4.56 MB | 21,891 | Every version of every product |
  | Vercel | 287 KB | ~3,000 | Single file |
  | Stripe | 89 KB | ~1,000 | Single file |
  | Neon | 75 KB | ~600 | Points to .md URLs |
  | React | 14 KB | ~150 | Single file |
  | Claude Code | 11 KB | ~60 | Small, focused |
  | GitHub Docs | 2 KB | ~30 | Small index |
  | MongoDB `/llms.txt` (root) | 1.5 KB | 6 | Top-level index only |

  Claude Code's web fetch pipeline truncates at ~100KB. A 4.56MB file means
  the agent sees roughly 2% of it. Even Vercel's 287KB file would be heavily
  truncated. Only the files under ~100KB are reliably consumable in their
  entirety by current agent implementations.

- **Result levels**:
  - **Pass**: Under 50,000 characters (fits comfortably within all known
    truncation limits, even accounting for overhead).
  - **Warn**: Between 50,000 and 100,000 characters (fits within Claude Code's
    limit but may not fit others; consider splitting).
  - **Fail**: Over 100,000 characters (will be truncated by Claude Code and
    likely all other agent platforms).
- **Recommended action**:
  - **Warn**: If the file grows further, split into nested `llms.txt` files
    with a root index under 50,000 characters.
  - **Fail**: Split into a root index linking to section-level `llms.txt`
    files, each under 50,000 characters. See [Progressive Disclosure for
    Large Documentation Sets](#progressive-disclosure-for-large-documentation-sets)
    below.
- **Automation**: Full.

### `llms-txt-links-markdown`

- **What it checks**: Whether the URLs in `llms.txt` point to markdown content
  (`.md` extension in the URL, or response with `Content-Type: text/markdown`).
- **Why it matters**: Markdown content is dramatically more useful to agents than
  HTML. An `llms.txt` that points agents to HTML pages misses an opportunity to
  deliver content in the most agent-friendly format. The best implementations
  (like Neon's) point to `.md` URLs that serve clean markdown directly.
- **Result levels**:
  - **Pass**: All or most links point to markdown content.
  - **Warn**: Links point to HTML, but markdown versions are available (detected
    by trying `.md` variants of the URLs).
  - **Fail**: Links point to HTML and no markdown alternatives are detected.
- **Recommended action**: Update `llms.txt` links to use `.md` URL variants
  so agents receive markdown instead of converted HTML.
- **Automation**: Full.

### Progressive Disclosure for Large Documentation Sets

The llmstxt.org proposal does not address what to do when a documentation site
is too large for a single `llms.txt` file to fit within agent truncation limits.
In practice, large documentation sets (like MongoDB's, with 185 products/versions
and 21,891 links) produce `llms.txt` files that are orders of magnitude beyond
what any current agent can consume in a single fetch.

#### Who Actually Uses llms.txt?

The original framing of `llms.txt` drew analogies to `robots.txt` and
`sitemap.xml`, suggesting it would serve AI crawlers gathering training data.
The evidence shows this hasn't happened:

- An audit of 1,000 domains over 30 days found zero visits to `llms.txt`
  from GPTBot, ClaudeBot, or PerplexityBot ([Longato, August
  2025](https://www.longato.ch/llms-recommendation-2025-august/)).
- A 90-day study tracking 62,100+ AI bot visits found only 84 requests
  (0.1%) to `/llms.txt`, roughly 3x fewer visits than an average content
  page ([OtterlyAI GEO
  Study](https://otterly.ai/blog/the-llms-txt-experiment/)).
- John Mueller from Google stated directly: "no AI system currently uses
  llms.txt."

Training crawlers don't use `llms.txt` because they have their own
discovery mechanisms (sitemaps, link following, pre-built datasets) and
probing `/llms.txt` on every domain would waste crawl budget for an
unestablished standard.

The real consumers of `llms.txt` are **agents in real-time workflows**:
a developer's coding assistant fetching documentation to verify an API
pattern, an agent following a directive on a docs page that points it to
`llms.txt`, or a user explicitly handing their agent an `llms.txt` URL as
a discovery starting point. These are fetch-once, use-now interactions
subject to the truncation limits of web fetch pipelines.

This distinction matters for our recommendation. A progressive disclosure
pattern that splits `llms.txt` into nested files has no practical impact on
crawler consumption (since crawlers aren't consuming it). It directly
benefits the agent use case, which is where `llms.txt` actually provides
value today.

#### Recommendation

We recommend a **nested `llms.txt` pattern** for progressive disclosure:

#### Structure

A **root `llms.txt`** serves as a table of contents, listing the major sections
of the documentation with links to **section-level `llms.txt` files**. Each
section-level file contains the actual page links for that section.

```
# MongoDB Documentation

> MongoDB is the leading document database. This index covers all MongoDB
> products, drivers, and tools documentation.

## Products

- [Atlas](https://www.mongodb.com/docs/atlas/llms.txt): MongoDB Atlas cloud database
- [Atlas CLI](https://www.mongodb.com/docs/atlas-cli/llms.txt): Command-line interface for Atlas
- [Compass](https://www.mongodb.com/docs/compass/llms.txt): GUI for MongoDB
- [MongoDB Server](https://www.mongodb.com/docs/manual/llms.txt): Server documentation

## Drivers

- [Python Driver](https://www.mongodb.com/docs/drivers/pymongo/llms.txt): PyMongo driver
- [Node.js Driver](https://www.mongodb.com/docs/drivers/node/llms.txt): Node.js driver
- [Java Driver](https://www.mongodb.com/docs/drivers/java/llms.txt): Java sync and reactive drivers
```

Each linked `llms.txt` then contains the actual page listings for that product
or driver, scoped to the current version (or with a small number of version
variants).

#### Design Principles

1. **The root `llms.txt` should fit in a single agent fetch.** Target under
   50,000 characters. This is the entry point that agents will discover first,
   and it must be fully consumable. It should contain enough descriptive context
   for an agent to identify which section-level file to fetch next.

2. **Section-level files should also fit in a single agent fetch.** If a
   section is still too large (e.g., a product with hundreds of pages across
   many versions), consider further nesting or limiting the index to the
   current version only.

3. **Version sprawl is the primary size driver.** The MongoDB `/docs/llms.txt`
   lists every version of every product. Linking to every historical version
   in the index provides diminishing returns for agents, who almost always want
   the current version. Historical versions could be listed in a separate
   `llms-versions.txt` or under the "Optional" H2 section that the proposal
   already defines for secondary content.

4. **Links between levels should use absolute URLs.** An agent following a link
   from root `llms.txt` to a section `llms.txt` needs to resolve it without
   ambiguity.

5. **Each `llms.txt` should be self-describing.** Include the H1 and blockquote
   summary at every level so an agent landing on a section-level file (via
   direct URL from training data, for example) has enough context to understand
   what it's looking at.

#### Compatibility Note

This nested pattern is a recommendation from this spec, not part of the
llmstxt.org proposal as of February 2026. It is fully compatible with the
existing proposal (which doesn't prohibit linking to other `llms.txt` files)
but would benefit from formal standardization. The proposal's existing
"Optional" H2 section could be leveraged for secondary/versioned content, but
the nesting pattern goes further by distributing content across multiple files.

### `llms-txt-directive-html`

- **What it checks**: Whether the HTML version of documentation pages includes
  a directive, visible to agents but not necessarily to human readers, pointing
  to `llms.txt` or another discovery resource.
- **Why it matters**: Agents that fetch rendered HTML pages have no built-in
  way to discover that a documentation index exists at `/llms.txt` or that
  markdown versions of pages may be available. An in-page directive serves as
  an agent "You Are Here" marker that points them to the index. The directive
  can be visually hidden (e.g., using a CSS clip-rect technique or `sr-only`
  class) as long as it remains in the DOM and survives HTML-to-markdown
  conversion. Avoid `display: none`, which some converters strip. The
  directive should be present in server-rendered HTML; avoid relying solely
  on client-side JavaScript injection, since most agents fetch pages without
  executing JS.
- **Detection considerations**: Implementations must distinguish intentional
  agent-facing directives from incidental mentions of `llms.txt`. Navigation
  items (e.g., sidebar links to a page *about* `llms.txt`), JSON-LD metadata,
  `<script>` blocks, and page content that merely discusses `llms.txt` as a
  feature do not count as directives. A directive is a standalone element in
  the page content area whose purpose is to tell agents where to find the
  documentation index.
- **Result levels**:
  - **Pass**: A directive pointing to `llms.txt` (or equivalent index) is
    present in the HTML DOM of all (or nearly all) documentation pages,
    ideally near the top of the content.
  - **Warn**: A directive exists in the HTML of some pages but is missing from
    others, or is present but buried deep in the page (past 50% of content,
    where it may be past truncation).
  - **Fail**: No agent-facing directive detected in the HTML of any tested
    page.
- **Recommended action**:
  - **Warn**: Ensure the directive appears near the top of every documentation
    page's HTML, not just some.
  - **Fail**: Add a visually-hidden element near the top of each page (e.g.,
    a `<div>` with CSS clip-rect) containing text like "For AI agents: a
    documentation index is available at /llms.txt" and, if applicable, a note
    that markdown versions are available.
- **Automation**: Heuristic. Search the page HTML for patterns like links to
  `llms.txt`, phrases like "documentation index", or directives near the top
  of the content area. Check both visible text and visually-hidden elements.
  Exclude matches in navigation, metadata, script blocks, and content that
  discusses `llms.txt` as a topic rather than directing agents to it.

### `llms-txt-directive-md`

- **What it checks**: Whether the markdown version of documentation pages
  includes a directive pointing to `llms.txt` or another discovery resource.
- **Why it matters**: Agents that fetch markdown versions of pages (via `.md`
  URLs or content negotiation) benefit from a directive that points them to
  the documentation index. Anthropic's Claude Code documentation
  (`code.claude.com/docs`, hosted on Mintlify) includes a blockquote at the
  top of every markdown page telling agents to fetch the documentation index
  at `llms.txt`. In practice, agents that encounter this directive may follow
  it to discover the full documentation index. It's simple, low-effort, and
  has been observed to work in real agent workflows.
- **Result levels**:
  - **Pass**: A directive pointing to `llms.txt` (or equivalent index) is
    present in the markdown of all (or nearly all) documentation pages,
    ideally near the top of the content.
  - **Warn**: A directive exists in the markdown of some pages but is missing
    from others, or is present but buried deep in the page (past 50% of
    content, where it may be past truncation).
  - **Fail**: No agent-facing directive detected in the markdown of any tested
    page.
- **Recommended action**:
  - **Warn**: Ensure the directive appears near the top of every markdown
    page, not just some.
  - **Fail**: Add a blockquote near the top of each markdown page (e.g.,
    "> For the complete documentation index, see
    [llms.txt](https://example.com/llms.txt)"). Use an absolute URL; see
    `markdown-link-portability` for why relative links are fragile in
    served markdown.
- **Automation**: Heuristic. Fetch the markdown version of sampled pages (via
  `.md` URL or content negotiation) and search for patterns like links to
  `llms.txt`, phrases like "documentation index", or blockquote directives
  near the top of the content. This check depends on markdown being available
  via `markdown-url-support` or `content-negotiation`; if neither passes,
  this check is skipped.

---

## Category 2: Markdown Availability

These checks evaluate whether the site serves documentation in markdown format,
which agents consume far more effectively than HTML.

### `markdown-url-support`

- **What it checks**: Whether appending `.md` to documentation page URLs returns
  valid markdown content.
- **Why it matters**: Agents work dramatically better with markdown than HTML.
  The HTML-to-markdown conversion in web fetch pipelines is lossy and
  unpredictable. Sites that serve markdown directly bypass conversion issues
  entirely. However, agents don't discover this pattern on their own; it needs
  to be signaled.
- **Result levels**:
  - **Pass**: `.md` URLs return valid markdown with 200 status.
  - **Warn**: Some pages support `.md` but not consistently.
  - **Fail**: `.md` URLs return errors or HTML.
- **Recommended action**:
  - **Warn**: Ensure all documentation pages serve markdown when `.md` is
    appended to the URL, not just some.
  - **Fail**: Configure your docs platform to serve `.md` variants for all
    documentation pages.
- **Automation**: Full. Test against a sample of page URLs (from `llms.txt`,
  sitemap, or user-provided list).

### `content-negotiation`

- **What it checks**: Whether the server responds to `Accept: text/markdown`
  with markdown content and an appropriate `Content-Type` header.
- **Why it matters**: Some agents (Claude Code, Cursor, OpenCode) send
  `Accept: text/markdown` as their preferred content type. If the server
  honors this, the agent gets clean markdown without needing to know about
  `.md` URL patterns. Most agents don't request markdown, but the ones that
  do should get it.
- **Result levels**:
  - **Pass**: Server returns markdown content with `Content-Type: text/markdown`
    when requested.
  - **Warn**: Server returns markdown content but with incorrect `Content-Type`.
  - **Fail**: Server ignores the `Accept` header and returns HTML regardless.
- **Recommended action**:
  - **Warn**: Set the response `Content-Type` to `text/markdown` when serving
    markdown content. The correct header enables optimizations in some agent
    pipelines.
  - **Fail**: Configure your server to honor `Accept: text/markdown` requests
    and return markdown content. Some agents (Claude Code, Cursor, OpenCode)
    request markdown this way.
- **Automation**: Full.

---

## Category 3: Page Size and Truncation Risk

These checks evaluate whether page content fits within the transfer and
processing limits of agent web fetch pipelines. Truncation is silent: the
agent doesn't know it's working with partial data.

### How Agents Get Content

Not all agents see the same thing. The format an agent receives depends on the
request it makes and the server's response:

1. **Agents that request markdown** (Claude Code, Cursor, OpenCode send
   `Accept: text/markdown`). If the server honors this and returns markdown,
   the agent gets clean content. If the server also returns
   `Content-Type: text/markdown` and the content is under 100K characters,
   Claude Code bypasses its summarization model entirely, delivering the
   content directly to the agent. This is the best-case path.

2. **Agents that request HTML** (most agents, including Gemini, Copilot, and
   others, send `Accept: text/html` or `*/*`). These agents receive the full
   HTML response. Some pipelines convert HTML to markdown before truncation
   (Claude Code uses Turndown); others may truncate raw HTML or use their own
   processing. The HTML path is where boilerplate CSS/JS causes the most
   damage.

3. **Agents that use `.md` URL variants.** If an agent knows to append `.md`
   to a URL (because `llms.txt` told it, or a directive on the page, or
   persistent context), it gets markdown directly regardless of Accept headers.

Because different agents hit different paths, this spec defines size checks for
**both** the markdown response (if available) and the HTML response. A site
that's only optimized for the markdown path is leaving most agents behind.

Pipelines also differ in **when** they cut oversized content, and the order
determines which measurement predicts the agent's experience:

1. **Convert, then truncate.** Scripts and styles are stripped, HTML is
   converted to markdown, and the size limit applies to the converted output.
   Post-conversion size (`page-size-html`) predicts these pipelines.
2. **Truncate, then convert** (or ingest raw HTML directly). The size limit
   applies to the bytes as served, so inline scripts and serialized data
   consume the budget before any content does. Served size
   (`page-size-transfer`) predicts these pipelines.
3. **Capped fetch.** Independent of processing order, some tools cap the
   response bytes they will read, so a page can fail at the transfer layer
   before any conversion happens. Served size predicts this too.

A page can score well on one measurement while failing agents on the other,
which is why the spec measures both.

For empirical observations of how specific platforms (Claude, Cursor, Copilot,
Gemini, Windsurf Cascade, and others) handle retrieval, truncation, and
summarization in practice, see [Agent platform comparisons](https://agentdocsspec.com/platforms/).

### `rendering-strategy`

- **What it checks**: Whether the HTTP response contains the page's actual
  content, or whether content requires JavaScript execution to render
  (client-side rendering / SPA).
- **Why it matters**: Most coding agents fetch pages using HTTP libraries that
  do not execute JavaScript. GitHub Copilot is the only major agent observed
  to use headless browser rendering. When a site relies on client-side
  rendering, agents see an empty shell containing framework boilerplate,
  inline CSS, and navigation chrome, but none of the documentation content.

  This is not a truncation problem. It is a zero-content problem. The page
  returns HTTP 200, so the agent doesn't know anything is wrong. It attempts
  to extract information from whatever text is in the shell (typically nav
  links and footer text) and produces nonsensical results, or falls back on
  training data that may be outdated.

  The rendering strategy is a property of the framework configuration, not
  the framework itself. The same framework can produce either server-rendered
  or client-rendered output. Sites built with Next.js, Gatsby, and Nuxt
  appear on both sides: react.dev (Next.js) and docs.github.com (Next.js)
  are fully agent-accessible, while other sites using the same frameworks
  deliver empty shells. Text-to-HTML ratio alone is not a reliable signal;
  GitHub docs and Stripe docs have low ratios due to heavy bundled assets
  but contain real page content. The distinction is whether page-specific
  content is present in the response.

  A subtler variant exists where a page is statically generated but a
  specific component defers content rendering to JavaScript based on user
  selections (e.g., query parameters choosing a language or deployment type).
  The static HTML contains the page structure (title, navigation, selector
  UI) but none of the substantive content. From an agent's perspective, the
  effect is the same as a full SPA shell.

- **Result levels**:
  - **Pass**: HTTP response contains substantive page content. Detected by
    the presence of multiple page-specific headings, paragraphs with prose
    content, or other content elements beyond navigation chrome.
  - **Warn**: HTTP response contains some content but appears sparse relative
    to the page's apparent scope. This covers client-side content population
    (statically generated pages where a component defers content to
    JavaScript), partial hydration or lazy loading, and legitimately minimal
    pages.
  - **Fail**: HTTP response is an SPA shell. Detected by the combination of
    known framework markers (e.g., `id="___gatsby"`, `id="__next"`,
    `id="__nuxt"`, `id="root"`), minimal visible text content, and absence
    of page-specific content elements.
- **Recommended action**:
  - **Warn**: Verify that key content is present in the server-rendered HTML
    response. Pages with sparse content may rely on client-side JavaScript
    to populate.
  - **Fail**: Enable server-side rendering or pre-rendering for documentation
    pages. If only specific page templates use client-side content loading,
    target those templates rather than rebuilding the entire site.
- **Automation**: Heuristic. Combine framework marker detection with content
  signal analysis (headings, paragraphs, code blocks after stripping
  `<script>`, `<style>`, and `<noscript>` elements). Framework markers alone
  are not conclusive since SSR sites share the same markers.
- **Notes**: If this check fails, size-related checks (`page-size-html`,
  `content-start-position`) still run but their results should be
  interpreted with caution, since they are measuring a shell rather than
  actual content. This is a recommendation for report consumers and
  implementations presenting results; it does not require downstream
  checks to declare a dependency on `rendering-strategy` or alter their
  own pass/warn/fail logic. If the site passes `markdown-url-support` or
  `content-negotiation`, that provides partial mitigation: agents that
  request markdown may still get content even when the HTML path is broken.

### `page-size-markdown`

- **What it checks**: The character count of the page when served as markdown,
  via either the `.md` URL variant or content negotiation with
  `Accept: text/markdown`. Only runs if the site serves markdown (as detected
  by Category 2 checks).
- **Why it matters**: This is the best-case scenario for agent consumption.
  Markdown is what agents actually want, and it's the format where page size
  most directly corresponds to what the model sees. If the markdown version
  fits within truncation limits, agents that can request it will get the full
  content.
- **Result levels**:
  - **Pass**: Under 50,000 characters (fits comfortably within all known
    limits, including Claude Code's direct-delivery threshold for trusted
    sites).
  - **Warn**: Between 50,000 and 100,000 characters (fits within Claude Code's
    truncation limit but may exceed others; also exceeds the direct-delivery
    threshold, meaning a summarization model may process it).
  - **Fail**: Over 100,000 characters (will be truncated by Claude Code and
    likely all other platforms).
- **Recommended action**:
  - **Warn**: Consider splitting large pages. Pages in this range may be
    truncated on some platforms or routed through a summarization model.
  - **Fail**: Break oversized pages into smaller ones, or restructure
    serialized tabbed content that inflates page size.
- **Automation**: Full.
- **Notes**: If the site doesn't serve markdown at all, this check is skipped
  and `page-size-html` becomes the primary size check. The report should note
  that the site relies entirely on the HTML path.

### `page-size-html`

- **What it checks**: The character count of the HTML response, and the
  character count after converting HTML to markdown (simulating what an
  agent's processing pipeline produces). Reports both numbers.
- **Why it matters**: Most agents receive HTML, not markdown. The raw HTML size
  determines whether the page even fits in the fetch buffer (Claude Code caps
  at ~10MB). The post-conversion size is closer to what the agent actually
  processes, but conversion pipelines vary across agents and are lossy and
  unpredictable. Navigation boilerplate, serialized tabbed content, and
  deeply nested page structure can all inflate the converted output well
  beyond the documentation content itself. Both raw and post-conversion
  sizes matter.
- **Result levels** (based on post-conversion size, since that's what the
  model receives):
  - **Pass**: Converted content under 50,000 characters.
  - **Warn**: Converted content between 50,000 and 100,000 characters.
  - **Fail**: Converted content over 100,000 characters.
- **Recommended action**:
  - **Warn**: Review pages for reducible boilerplate (navigation, serialized
    tabbed content). Consider providing markdown versions as a smaller
    alternative path for agents.
  - **Fail**: Break large pages into smaller units, reduce navigation
    boilerplate, or provide markdown versions that bypass the HTML conversion
    overhead.
  - Markdown availability helps agents that request it but does not reduce
    the HTML page size itself; fixing the HTML remains important.
- **Automation**: Full. Convert HTML to markdown using a pipeline that
  approximates what agents see after their own processing. Agent pipelines
  vary (some strip `<script>`/`<style>` elements before conversion, others
  don't; some use Turndown, others use different converters or visit pages
  in-browser). Implementations should document their conversion approach.
- **Report details**: Show both the raw HTML size and the post-conversion size.
  A large gap between the two indicates heavy boilerplate. Report the
  conversion ratio (e.g., "505KB HTML -> 12KB markdown (98% boilerplate)")
  as a useful signal for site owners.

### `page-size-transfer`

- **What it checks**: The served byte size of the HTML document response:
  the response body after transfer decoding (decompression), which is what
  an agent's HTTP client hands to its processing pipeline. Subresources
  (linked CSS, JavaScript, images) are not counted, because agents generally
  don't fetch them. Inline scripts, styles, and serialized data payloads
  embedded in the document are counted, because agents can't avoid receiving
  them.
- **Why it matters**: `page-size-html` measures what survives HTML-to-markdown
  conversion, which models pipelines that strip scripts and convert before
  truncating. Served size measures what every agent pays before any
  processing happens, and it fails differently:
  - **Truncate-first and raw-ingestion pipelines** consume script payload as
    content. For them, serialization overhead isn't invisible; it is the
    page.
  - **Fetch caps** apply to response bytes, not converted output. A page can
    convert to a few kilobytes of clean markdown and still exceed the byte
    budget of the tool fetching it (Claude Code's fetch buffer caps at
    ~10MB).
  - **Bandwidth and latency costs** apply to every fetch regardless of
    pipeline, and multi-page reading sessions multiply them.

  Modern server-rendering frameworks can make the gap between served bytes
  and content arbitrarily large. In measurements of production documentation
  sites on one hosted platform, pages shipped 75-84% of their bytes as
  serialized framework payloads inside inline script tags: component trees,
  resolved metadata, and a complete duplicate of the page's markdown source.
  Served-bytes-to-content ratios ran from 40:1 to 200:1. Those pages score
  well on `page-size-html` because conversion strips the payload, while
  every agent fetching them transfers half a megabyte to several megabytes
  per page.
- **Result levels**:
  - **Pass**: Served size under 1MB.
  - **Warn**: Served size between 1MB and 10MB. No documented cap is
    exceeded, but truncate-first and raw-ingestion pipelines are consuming
    mostly non-content bytes, and multi-page sessions pay a real bandwidth
    and latency cost.
  - **Fail**: Served size over 10MB. This exceeds the only well-documented
    transfer cap (Claude Code's fetch buffer); content beyond the cap is
    unreachable regardless of how the pipeline processes it.
- **Recommended action**:
  - **Warn**: Identify what the non-content bytes are; in practice they are
    usually inline serialization (framework hydration payloads, embedded
    duplicate page source, resolved data objects) visible in the page
    source. Avoid shipping the same content twice in different formats,
    load large data payloads on demand, and confirm markdown variants are
    available and discoverable so agents have a cheaper path.
  - **Fail**: Same actions, urgently. At this size, at least one major
    platform cuts the page off at the transfer layer.
  - Markdown availability gives agents that discover it an escape hatch but
    does not reduce what HTML-path agents transfer; fixing the served
    payload remains important.
- **Automation**: Full. Fetch with an `Accept-Encoding` typical of agent
  HTTP clients, decode the response, and measure the decoded body.
  Implementations may also report the on-the-wire (compressed) size where
  available; serialized payloads compress well, so wire size understates
  the processing burden.
- **Report details**: Show served bytes alongside the post-conversion
  content size from `page-size-html`, and report the ratio between them
  (e.g., "3.4MB served -> 29KB content (~120:1)"). A high ratio on a large
  page is an architecture signature (hydration payloads, embedded duplicate
  content) rather than a content problem; it tells the site owner the fix
  lives in framework configuration, not in the docs themselves.
- **Notes**: This check complements `rendering-strategy`, which catches pages
  that ship too little server-rendered content. This check catches the
  opposite failure: pages that render content fine but ship many times its
  weight in serialization overhead. Byte-level caps are less documented than
  character-level truncation limits, so the default thresholds here are
  conservative and should be configurable (see
  [Appendix A](#appendix-a-known-platform-truncation-limits)).

### `content-start-position`

- **What it checks**: How far into the **post-conversion** content (by character
  count and as a percentage) the actual documentation content begins.
- **Why it matters**: After HTML-to-markdown conversion, boilerplate often
  survives. Navigation menus, breadcrumbs, sidebars, and footer content all
  convert to text that precedes or surrounds the actual documentation. Depending
  on the agent's conversion pipeline, inline CSS and JavaScript may also survive
  as raw text. If this boilerplate consumes most of the truncation budget, the
  agent never sees the documentation content. In one observed case, actual
  content didn't start until 87% of the way through the output (441K characters
  of CSS before the first paragraph).
- **Result levels**:
  - **Pass**: Content starts within the first 10% of the post-conversion
    output.
  - **Warn**: Content starts between 10% and 50%.
  - **Fail**: Content starts after 50%.
- **Recommended action**: Reduce navigation, breadcrumb, and sidebar markup
  that precedes the content area. Agents may never see the documentation
  content if boilerplate consumes most of the truncation budget.
- **Automation**: Heuristic. Use the same conversion pipeline as
  `page-size-html`, then detect the first meaningful content element (heading,
  paragraph with prose) past any boilerplate (navigation text, breadcrumbs,
  sidebar content, inline CSS/JS that survived conversion).
- **Notes**: This check only applies to the HTML path. Markdown served directly
  by the site should not have boilerplate preamble; if it does, that's a
  separate issue worth flagging but not something this check targets.

### `single-fetch-completeness`

- **What it checks**: Whether a markdown response delivers its complete
  content in one fetch, and when it doesn't, whether the continuation is
  machine-followable: declared where agents will see it, linked with an
  absolute URL, and actually working.
- **Why it matters**: Pagination is application-level truncation, and it is
  quieter than the platform truncation this category otherwise measures. A
  paginated markdown response looks complete: it is well-formed, ends
  cleanly, and returns 200. The signals that it is partial are easy for
  agent pipelines to lose:
  - **Summarization pipelines** process fetched content through a smaller
    model before the orchestrating agent sees it. A pagination note may or
    may not survive summarization, and the summarizer cannot perform a
    follow-up fetch itself; the orchestrator would have to notice the note
    and choose to fetch again.
  - **Trailing pagination notes** sit at the end of the content, which is
    the first region lost to platform truncation. A truncated response
    loses the only indication that it was also paginated.
  - **RAG pipelines** chunk fetched content for retrieval. A pagination
    marker lands in one chunk, unrelated to the content it describes, and
    effectively disappears.

  This failure was observed in production on a model catalog's markdown
  variant: 100 of 102 entries shown, a pagination note at the bottom of the
  file, a continuation URL that was root-relative rather than absolute, and,
  when fetched, a continuation response that returned an empty body. An
  agent fetching that page gets 98% of the catalog and no working way to
  learn what's missing.

  Notably, pagination in a markdown variant is often inherited from the
  HTML UI rather than needed by the markdown itself. The catalog above
  paginates at 100 entries per page, but the complete set serializes to
  roughly 32,000 characters, comfortably under this spec's 50,000-character
  pass threshold. The markdown variant imported an interaction pattern from
  a surface that has interaction; markdown doesn't.
- **Result levels**:
  - **Pass**: The response is complete in one fetch (no pagination signals
    detected), or pagination exists and the continuation is declared at the
    top of the content with an absolute URL that resolves to the next
    segment.
  - **Warn**: Pagination exists and the continuation works, but is fragile:
    declared only at the bottom of the content, linked with a relative URL,
    or discoverable only from response headers.
  - **Fail**: The content is partial and the continuation is missing,
    relative and unresolvable, or broken (non-success status, empty body,
    or a soft 404).
- **Recommended action**:
  - **Warn**: Move the continuation declaration to the top of the content
    (before anything truncation could remove) and make continuation links
    absolute.
  - **Fail**: First ask whether the markdown variant needs pagination at
    all: complete content that fits within this spec's size thresholds
    should be served in one response, even when the HTML UI paginates. If
    pagination is genuinely necessary, declare it at the top with absolute
    links, and verify the continuation URLs actually serve content.
- **Automation**: Heuristic. Detect pagination signals in markdown
  responses: "N of M" phrasing, links or instructions containing pagination
  query parameters (`?page=`, `?offset=`), "next page" link text, and
  `Link: rel="next"` response headers. When signals are found, fetch the
  continuation and verify it returns substantive content of the expected
  representation. Absence of signals is treated as complete; a page that
  omits content with no marker at all is not detectable by this
  check (see `markdown-content-parity` for the cross-representation
  comparison that can catch it).
- **Notes**: Only applies to markdown responses (`.md` variants, content
  negotiation, and `llms.txt`-linked markdown). HTML pagination is an
  interaction pattern agents share with human readers and is out of scope
  here.

---

## Category 4: Content Structure

These checks evaluate whether page content is structured in ways that agents can
effectively consume. These are harder to fully automate and rely more on
heuristics.

### `tabbed-content-serialization`

- **What it checks**: Whether pages use tabbed, accordion, or dropdown UI
  patterns that serialize into long sequential content in the source, and if
  so, how large the serialized output is.
- **Why it matters**: Tabbed content is great for humans but can be catastrophic
  for agents. A tutorial with 11 language variants serializes into a single
  massive document where an agent might see only the first 1-3 variants. Source
  order determines what the agent sees; everything past the truncation point is
  invisible. Asking for a specific variant (e.g., Python) does not help if that
  variant is beyond the truncation point.
- **Result levels**:
  - **Pass**: No tabbed content, or tabbed content that serializes to under
    50,000 characters total.
  - **Warn**: Tabbed content serializes to 50,000-100,000 characters.
  - **Fail**: Tabbed content serializes to over 100,000 characters.
- **Recommended action**: Break tab variants into separate pages, or provide
  a mechanism for agents to request specific variants. Agents see only the
  first few variants; content in later tabs is truncated.
- **Automation**: Heuristic. Detect common tab/accordion component patterns
  (e.g., `<Tab>`, `<Tabs>`, role="tabpanel", common CSS class patterns) and
  estimate serialized size.

### `section-header-quality`

- **What it checks**: Whether section headers contain enough context to be
  meaningful without the surrounding UI. Specifically, when tabbed content is
  serialized, do headers distinguish which variant (language, platform,
  deployment type) a section belongs to?
- **Why it matters**: When an agent sees serialized tabbed content, descriptive
  headers are the only way it can tell which section applies to which context.
  Generic headers like "Step 1" repeated across all variants are
  indistinguishable. Headers like "Step 1 (Python/PyMongo)" preserve the
  filtering context that the UI provided to human readers.
- **Result levels** (evaluated both within individual tab groups and across
  tab groups on the same page; the overall result is the worst of both):
  - **Pass**: <=25% of headers within tabbed sections are generic (repeated
    across variants without distinguishing context).
  - **Warn**: 25-50% of headers are generic across variants.
  - **Fail**: >50% of headers are generic, or identical header sets are
    repeated across separate tab groups on the same page with no variant
    context.
  These thresholds are defaults; implementations should allow them to be
  configured.
- **Recommended action**: Add variant context to headers (e.g., "Step 1
  (Python)" instead of "Step 1") so agents can distinguish which section
  belongs to which variant when content is serialized.
- **Automation**: Heuristic. Requires detecting tabbed sections and analyzing
  header patterns within them.

### `markdown-code-fence-validity`

- **What it checks**: Whether markdown content contains unclosed or improperly
  nested code fences (`` ``` `` or `~~~` blocks without a matching closing
  delimiter).
- **Why it matters**: An unclosed code fence causes everything after it to be
  interpreted as code rather than prose. The agent sees documentation text,
  API descriptions, and instructions as if they were inside a code block,
  which fundamentally changes how it processes the content. A model treats
  code blocks as literal content to reproduce or analyze, not as natural
  language instructions to follow. If an unclosed fence appears early in a
  page, the agent effectively loses the rest of the document's meaning. This
  applies to any markdown the site serves directly: pages via `.md` URLs or
  content negotiation, and `llms.txt` files themselves.
- **Result levels**:
  - **Pass**: All code fences in the markdown content are properly opened and
    closed.
  - **Fail**: One or more unclosed code fences detected.
- **Recommended action**: Ensure every opening `` ``` `` or `~~~` has a
  matching closing delimiter. Everything after an unclosed fence is
  interpreted as code, causing agents to misread documentation as literal
  content.
- **Notes on delimiter matching**: Per the CommonMark spec, a backtick fence
  (`` ``` ``) can only be closed by another backtick fence of equal or greater
  length, and likewise for tilde fences (`~~~`). Opening with `` ``` `` and
  attempting to close with `~~~` leaves the backtick fence unclosed. There is
  no intermediate "mismatched but balanced" state; mismatched delimiters
  produce unclosed fences and should be reported as failures.
- **Automation**: Full. Parse the markdown for fence delimiters (`` ``` `` and
  `~~~`, with optional info strings) and verify each opening delimiter has a
  matching close. Run against markdown served via `.md` URLs, content
  negotiation responses, and `llms.txt` files.
- **Notes**: This check applies to markdown the site authors and serves
  directly. Code fences broken by an HTML-to-markdown conversion pipeline are
  outside the site owner's control, though implementations may optionally flag
  them as informational findings.

### `markdown-link-portability`

- **What it checks**: Whether links in served markdown are absolute URLs, and
  whether a sample of them resolves to the representation they promise (a
  `.md` link returns markdown content, not an HTML error page).
- **Why it matters**: Relative URL resolution is well-defined (RFC 3986), but
  it requires knowing the base URL, and agent pipelines routinely lose it. A
  browser always carries the base; markdown fetched by an agent passes
  through summarization models, gets chunked for RAG, or gets pasted into a
  context where the source URL is gone. Once the base is lost, a
  root-relative link is unreconstructable and a path-relative link is
  meaningless. This spec already recommends absolute URLs between `llms.txt`
  levels for the same reason; served markdown deserves the same rule.

  Link verification must go beyond status codes. In one observed production
  case, a catalog's markdown variant emitted over 100 well-formatted links
  that all pointed into a wrong internal path prefix, apparently a build-time
  substitution error. Every link returned 200 with a body. The body was an
  HTML SPA shell whose only acknowledgment of failure was a serialized
  framework error digest inside script payload: a soft 404 served as HTML at
  a `.md` URL. A checker (or agent) that tested status codes alone would
  conclude the links worked; checking the `Content-Type` header alone would
  have caught it.
- **Result levels**:
  - **Pass**: Links are absolute URLs, and sampled links resolve to the
    expected representation.
  - **Warn**: Links are root-relative (resolvable while the base URL is
    known, fragile once it isn't), or sampled links resolve with minor
    mismatches (e.g., a `.md` link that redirects to an HTML page with the
    right content).
  - **Fail**: Links are path-relative, or sampled links are broken: hard
    404s, soft 404s, or a content type that contradicts the link (`.md`
    links returning HTML shells).
- **Recommended action**:
  - **Warn**: Emit absolute URLs when generating markdown variants; the
    site's canonical host is known at build time.
  - **Fail**: Fix the link generation first, then make the links absolute.
    Verify generated links in CI by fetching a sample and checking both
    status and content type; a link set that is generated is a link set
    that can break wholesale.
- **Automation**: Full. Parse links from served markdown, classify as
  absolute, root-relative, or path-relative, resolve a sample against the
  fetch URL, and verify status, `Content-Type`, and soft-404 heuristics
  (reusing the detection from `http-status-codes`).
- **Notes**: Applies to markdown served via `.md` URLs and content
  negotiation. `llms.txt` link quality is covered separately by
  `llms-txt-links-resolve`; implementations should apply the same
  representation verification there, since status-code-only resolution
  misses soft 404s.

  **Why this check exempts the HTML path.** Relative links in HTML are
  correct web practice (they are what makes staging domains, mirrors, and
  CDN setups work), and the HTML path does not need the site's help: a
  pipeline converting HTML to markdown still holds the fetch URL at
  conversion time, so resolving relative links is the pipeline's job, with
  full information. The base URL is only lost downstream of conversion.
  Served markdown is different on both ends: the generator knows the
  canonical host, so absolute links are free to produce, and on the
  best-case consumption path (direct delivery of `text/markdown` under the
  summarization threshold) the site's bytes reach the model verbatim, with
  no conversion step where anything could be resolved. Tool builders
  implementing fetch pipelines should resolve relative links during
  HTML-to-markdown conversion, and likewise when ingesting raw HTML;
  converted content with relative links has all the same failure modes as
  served markdown once it leaves the converter.

### `embedded-data-serialization`

- **What it checks**: Whether machine-generated bulk data (large uniform
  tables, inline JSON or data blobs, base64 payloads) dominates a page's
  converted content, and attributes the page's size to the specific elements
  responsible.
- **Why it matters**: Dynamic widgets (compatibility matrices, model
  catalogs, spec browsers, pricing tables) flatten into static content when
  a page is rendered for agents. The result can be a page whose size wildly
  exceeds what its author believes they wrote: the author sees a few
  paragraphs and a widget; the built page carries hundreds of serialized
  rows under them. The size checks in Category 3 catch the symptom but
  don't explain it, and without attribution the person who can fix the page
  has no idea what to fix, or that anything is wrong at all.

  In one measured production case, a reference page served 302KB of HTML of
  which 64% was table markup, including a single generated table of 218
  rows. The page converts to roughly 83,000 characters (this spec's warn
  band), while its non-table prose totals about 17,000 characters. The
  page's truncation risk is entirely a property of its generated tables,
  which is invisible in an aggregate size number.
- **Result levels**:
  - **Pass**: No bulk-data elements detected, or bulk elements are present
    but the page passes the Category 3 size checks regardless.
  - **Warn**: Bulk-data elements are the dominant contributor (for example,
    over half of converted content) to a page that lands in the size
    checks' warn band.
  - **Fail**: Bulk-data elements are the dominant contributor to a page
    that exceeds the size checks' fail threshold. Content after the bulk
    element is beyond the truncation point for most platforms.
- **Recommended action**: Bulk data is often legitimate content (a support
  matrix is the point of a support-matrix page), so the goal is structure,
  not removal. Split large generated tables across per-section pages,
  provide filtered or queryable views, load embedded data blobs on demand,
  and place prose before bulk elements so truncation removes data rows
  rather than explanation. Report the attribution to content authors:
  a page that an author experiences as two paragraphs should not ship as a
  hundred kilobytes without the author knowing.
- **Automation**: Heuristic. After HTML-to-markdown conversion (same
  pipeline as `page-size-html`), detect bulk elements: tables above a row
  threshold with uniform row structure, fenced or inline JSON blobs above a
  size threshold, and base64 runs. Report each element's share of the
  converted content. Thresholds for "bulk" need calibration against real
  pages and should be configurable.
- **Notes**: This is the data-widget sibling of
  `tabbed-content-serialization`, which covers the same flattening failure
  for tab and accordion UI. Together with `content-start-position` (where
  content sits relative to boilerplate), these checks explain *why* a page
  fails the Category 3 size checks, not just that it does.

---

## Category 5: URL Stability and Redirects

These checks evaluate whether documentation URLs behave in ways that agents can
handle, given that agents retrieve URLs from training data and have limited
ability to discover moved content.

### `http-status-codes`

- **What it checks**: Whether pages return correct HTTP status codes. In
  particular, whether "not found" pages return 404 (not 200 with a friendly
  error page).
- **Why it matters**: Soft 404s (200 status with "page not found" content) are
  worse than real 404s for agents. The agent sees a 200 and tries to extract
  information from the error page content rather than recognizing the page
  doesn't exist. A clean 404 tells the agent to try a different approach.
- **Result levels**:
  - **Pass**: Error pages return appropriate 4xx status codes.
  - **Fail**: Error pages return 200 (soft 404).
- **Recommended action**: Configure your server to return 404 status codes
  for pages that don't exist. Agents try to extract information from soft
  404 page content instead of recognizing the page is missing.
- **Automation**: Full. Test known-bad URLs (e.g., append random strings to real
  page paths) and check status codes.

### `redirect-behavior`

- **What it checks**: Whether redirects are same-host (transparent to agents) or
  cross-host (a friction point), and whether redirects use proper HTTP status
  codes (301/302) vs. JavaScript-based redirects.
- **Why it matters**: Same-host redirects work transparently because the HTTP
  client follows them automatically. Cross-host redirects are a known failure
  point; Claude Code, for example, doesn't automatically follow cross-host
  redirects (security measure against open-redirect attacks). JavaScript
  redirects don't work at all because agents don't execute JavaScript.
- **Result levels**:
  - **Pass**: All redirects are same-host HTTP redirects (301/302).
  - **Warn**: Cross-host HTTP redirects are present (agents may or may not
    follow them depending on the platform).
  - **Fail**: JavaScript-based redirects are detected.
- **Recommended action**:
  - **Warn**: Where possible, use same-host redirects or update URLs to point
    directly to the final destination.
  - **Fail**: Replace JavaScript-based redirects with HTTP 301/302 redirects.
    Agents don't execute JavaScript and will not follow these redirects.
- **Automation**: Partial. HTTP redirects are detectable. JavaScript redirects
  require fetching the page and scanning for `window.location`, `meta refresh`,
  or similar patterns.

---

## Category 6: Observability and Content Health

These checks evaluate whether the site's agent-facing resources stay accurate
and up to date over time. Categories 1-5 can be evaluated as point-in-time
audits; this category addresses the ongoing maintenance dimension. `llms.txt`
files and markdown endpoints are secondary outputs that often aren't wired
into existing monitoring, so they can go stale, break, or drift from primary
HTML content without anyone noticing.

### `llms-txt-coverage`

- **What it checks**: How much of the site's documentation is represented
  in `llms.txt`.
- **Why it matters**: `llms.txt` is an agent's primary navigational index
  into a documentation site. Pages missing from the index are effectively
  invisible to agents that rely on it for discovery. Unlike
  `llms-txt-links-resolve` (which catches broken links to pages that are
  listed), this check catches the opposite problem: pages that exist on the
  site but aren't listed at all.
  
  Not every gap is a problem; many sites intentionally curate their
  `llms.txt` to include only a subset of pages. The check's value is
  making the coverage level visible so site owners can confirm it reflects
  their intent.
- **Result levels** (based on coverage of sitemap doc pages, excluding
  non-doc pages like blog posts, pricing, and login pages):
  - **Pass**: `llms.txt` links cover >=95% of the site's primary pages.
  - **Warn**: `llms.txt` links cover 80-95% of primary pages (some live
    pages are missing).
  - **Fail**: `llms.txt` links cover <80% of primary pages (missing large
    sections of the documentation).
  These thresholds are defaults that assume the site intends `llms.txt` to
  mirror the sitemap. Sites that intentionally curate their `llms.txt`
  should adjust thresholds to match their intent (see Notes below).
  Implementations should allow thresholds to be configured.
- **Recommended action**:
  - **Warn**: Review missing pages. If they should be in `llms.txt`, add
    them. If they are intentionally excluded, adjust the coverage threshold
    or add them to an exclusion list so the check reflects your intent.
  - **Fail**: If unintentional, regenerate `llms.txt` from your sitemap or
    build pipeline. If intentional, lower the threshold or set it to 0 to
    make the check informational.
- **Automation**: Heuristic. Compare links in `llms.txt` against a sitemap
  or crawled page list; flag pages present in the sitemap but absent from
  `llms.txt`. Implementations should support exclusion patterns that
  remove known-intentional gaps from the sitemap before calculating
  coverage.
- **Notes**: Not every sitemap page belongs in `llms.txt`. Sites
  intentionally exclude content for good reasons: changelog and
  release notes archives that would bloat the file, older product versions
  that aren't relevant to current development, API reference pages that
  aren't useful in markdown form, or directory pages that just link to
  other pages already listed. This is legitimate curation, not drift.

  The check should accommodate three use cases through configurable
  thresholds and exclusion patterns:

  - **Full parity**: The site intends `llms.txt` to mirror the sitemap.
    Default thresholds (95/80) apply; no exclusions needed.
  - **Curated**: The site intentionally includes only a subset of pages.
    Set thresholds to 0 to make the check informational. It still reports
    coverage percentage and lists what's missing, but never warns or fails.
  - **Hybrid**: The site wants strict coverage but with known exclusions.
    Exclusion patterns remove intentional gaps from the sitemap before
    calculating coverage; remaining pages are held to the default
    thresholds.

  The definition of "primary pages" in the denominator requires judgment.
  Implementations should document how they construct the URL pool from the
  sitemap and what filtering they apply.

### `markdown-content-parity`

- **What it checks**: Whether markdown versions of pages contain the same
  substantive content as their HTML counterparts.
- **Why it matters**: When markdown is generated separately from HTML (rather
  than being the source that HTML is built from), the two can drift. A site
  might update an HTML page but forget to regenerate the markdown version,
  leaving agents with outdated instructions or code examples. This is
  particularly insidious because agents that receive the markdown version
  have no signal that a newer HTML version exists.

  However, in some cases, content divergence may be intentional. Some sites
  intentionally serve different content to different audiences, providing
  agent-optimized markdown alongside human-optimized HTML. In those cases,
  the divergence is deliberate. The check's value is surfacing it so site
  owners can confirm it reflects their intent.
- **Result levels** (based on the percentage of content segments in the
  HTML version that are missing from the markdown version, after
  normalizing whitespace, case, and formatting):
  - **Pass**: <5% of content segments missing (or page has fewer than 10
    segments, which is too small to produce meaningful parity scores).
  - **Warn**: 5-20% of content segments missing (minor differences:
    formatting variations, navigation elements present in one but not the
    other).
  - **Fail**: >=20% of content segments missing (substantive content
    differences: missing sections, outdated code examples, or different
    instructions between the two versions).
  These thresholds are defaults that assume the site intends markdown to
  mirror HTML. Sites that intentionally serve different content per audience
  should adjust thresholds to match their intent (see Notes below).
  Implementations should allow thresholds to be configured.
- **Recommended action**:
  - **Warn**: Review pages with minor differences. If they are formatting
    variations that may affect agent comprehension, fix them. If they
    reflect intentional audience segmentation, adjust thresholds or
    configure the check to account for it.
  - **Fail**: If unintentional, agents receiving the markdown version are
    getting outdated or incomplete content. Regenerate markdown from source
    or fix the build pipeline. If intentional, lower the threshold or set
    it to 0 to make the check informational.
- **Automation**: Heuristic. Fetch both versions, extract text content from
  HTML (strip tags), and compare key sections (headings, code blocks,
  paragraph content) for meaningful differences. Minor formatting
  differences should be ignored. If the HTML contains audience-segmentation
  tags (see Notes), implementations should strip tagged content before
  comparing so that intentionally excluded content does not count as
  missing.
- **Notes**: Sites where markdown is the source format and HTML is generated
  from it are less likely to have parity issues, but the check is still
  valuable as a safety net for build pipeline failures.

  **Audience segmentation.** Some documentation platforms use HTML tags to
  control what content appears in each version. For example, a platform
  might tag certain content as agent-only (included in markdown but not
  rendered in HTML) or human-only (rendered in HTML but excluded from
  markdown). Platforms like Fern and Mintlify have implemented this
  pattern. When the HTML contains recognized audience-segmentation tags,
  implementations should account for them before comparing: content
  explicitly tagged for one audience should not count as missing from the
  other.

  The spec does not define a standard set of segmentation tags or
  prescribe which vendor conventions to recognize. Implementations should
  document which tag conventions they support, and vendors or site owners
  who want their conventions recognized can contribute them to
  implementations directly.

  As with `llms-txt-coverage`, the check should accommodate sites at
  different points on the mirrored-to-curated spectrum:

  - **Mirrored** (default): Markdown should match HTML. Default thresholds
    apply.
  - **Segmented**: The site uses audience-segmentation tags to control
    per-version content. The check strips tagged content before comparing;
    remaining shared content is held to the default thresholds.
  - **Curated**: The site intentionally serves different content with no
    tag-level signal. Set thresholds to 0 to make the check informational.

  **Dynamically generated pages.** Pages built from data (catalogs, model
  listings, compatibility matrices) can diverge between representations
  without anyone deciding they should, because the HTML and markdown
  variants are rendered by different pipelines with different defaults. In
  one observed production case, a catalog's HTML showed 98 items while its
  markdown variant listed 102: the HTML applied a default filter the
  markdown dump didn't, and the markdown was additionally paginated. For
  pages with repeated structure, implementations should compare item counts
  between representations, and should distinguish the likely causes when
  counts differ: a default filter on the dynamic view (divergent by
  configuration), pagination on either side (divergent by windowing, see
  `single-fetch-completeness`), or staleness (one representation generated
  from older data). Each has a different owner and fix.

### `cache-header-hygiene`

- **What it checks**: Whether `llms.txt` and markdown endpoints have cache
  headers that allow timely updates.
- **Why it matters**: Aggressive caching on agent-facing resources means
  that even after a site owner updates their `llms.txt` or markdown content,
  agents (and intermediary CDNs) may continue serving stale versions for
  hours or days. Conversely, no cache headers at all leads to ambiguous
  behavior where different CDN providers apply their own defaults. For
  resources that are relatively small and infrequently fetched, short cache
  lifetimes with revalidation are appropriate.
- **Result levels**:
  - **Pass**: Cache headers allow timely updates (e.g., `max-age` under
    3600, or uses `must-revalidate` with `ETag`/`Last-Modified`).
  - **Warn**: Moderate caching (1-24 hours) that could delay updates.
  - **Fail**: Aggressive caching (over 24 hours) with no revalidation
    mechanism, or no cache-related headers at all (ambiguous behavior).
    An exception: responses that lack `Cache-Control` and `Expires` but
    include `ETag` or `Last-Modified` should pass, since these validation
    headers enable conditional revalidation by browsers and CDNs even
    without explicit cache directives.
- **Recommended action**:
  - **Warn**: Updates to `llms.txt` or markdown content may take hours to
    propagate. Consider reducing cache lifetimes for these resources.
  - **Fail**: Set `max-age` under 3600 or add `must-revalidate` with
    `ETag`/`Last-Modified` so content updates reach agents promptly.
- **Automation**: Full. Inspect `Cache-Control`, `Expires`, `ETag`, and
  `Last-Modified` response headers.

### Ongoing Monitoring Recommendations

The three checks above can be run as one-time audits, but they're most
valuable when run on a schedule. This section offers non-normative guidance
on integrating agent-facing resources into existing monitoring workflows.

**Include `llms.txt` and markdown endpoints in uptime monitoring.** These
resources should be monitored alongside your primary documentation site. A
200 response from your docs homepage doesn't guarantee that `/llms.txt` or
`.md` URL variants are also healthy. Add them to whatever uptime tool you
already use (Pingdom, Uptime Robot, Checkly, etc.) as separate check targets.

**Set up alerting for response time degradation.** If your `llms.txt` or
markdown endpoints start responding slowly, agents may time out before
receiving content. This is especially relevant for dynamically generated
markdown (as opposed to static files), where a backend issue could cause
latency spikes that don't affect the HTML site.

**Run coverage and parity checks on a schedule.** Rather than treating
`llms-txt-coverage` and `markdown-content-parity` as one-time audits, run
them weekly or on every deploy. A CI check that compares `llms.txt` link
coverage against the sitemap can catch missing pages before they reach
production.

**Monitor for silent failures.** A 200 response with empty content, a
generic error message, or a login page is worse than a clean 404, because
agents will try to extract information from the response. Check that
`llms.txt` and markdown responses contain expected content markers (e.g., an
H1, a minimum character count) rather than just checking for a 200 status
code.

---

## Category 7: Authentication and Access

These checks evaluate whether documentation is accessible to agents at all:
without requiring interactive authentication, and without infrastructure-level
barriers aimed at automated clients. Docs behind login walls are effectively
invisible to coding agents, which has significant implications as agent-assisted
development becomes a standard workflow. Bot-protection systems can produce the
same invisibility through a different mechanism, and often without the site
owner realizing documentation is affected.

### Why This Matters

Enterprises often gate documentation behind authentication to protect
intellectual property, enforce licensing terms, or comply with access control
policies. These are legitimate business reasons. However, the tradeoff is
sharper than most organizations realize: authenticated docs are not just
inconvenient for agents, they are completely inaccessible.

When an agent encounters an auth-gated page, it sees one of these:

- A **401 or 403 response**, which tells it nothing useful.
- A **login page returned as 200**, which is a soft 404 from the agent's
  perspective. The agent tries to extract documentation from the login form
  HTML and produces nonsensical results.
- A **redirect to an SSO provider**, which is a cross-host redirect the agent
  cannot follow, even if it wanted to.

In all three cases, the agent may take one of two actions:

- Fall back on whatever it absorbed during training, which may be outdated,
  incomplete, or wrong.
- Leave your official product website and look for secondary sources to learn
  about your product, including blogs or articles which may inaccurate, outdated,
  and not reflect your official best practices.

In these scenarios, the developer either gets bad guidance, or has to manually
copy-paste docs into the conversation, losing the workflow benefits that agents
provide. This may also be completely invisible to the developer, as an agent
may "helpfully" turn to blog posts or secondary references without disclosing
to the human user that it used secondary sources which should be verified.

The competitive dimension is real. If your product's documentation requires a
login and your competitor's doesn't, developers using agents will have a
dramatically better experience with the competitor's product. The agent can
read the competitor's API reference, find code examples, and verify patterns
in real time. For your product, the agent is guessing.

Bot protection produces the same invisibility through a different mechanism,
and usually without a deliberate decision. Auth gating is at least a policy
choice about who may read the docs; bot enforcement is typically configured
site-wide for security reasons, with documentation caught as collateral. It
is also harder for the site owner to see. A login wall fails every request
the same way, but behavioral enforcement can pass a casual spot check and
then throttle, challenge, or stall the sustained multi-page sessions that
real agent work produces. A site owner who verifies their docs by loading a
page in a browser, or fetching a single URL with curl, will conclude
everything works.

### `auth-gate-detection`

- **What it checks**: Whether documentation pages require authentication to
  access content.
- **Why it matters**: A documentation site that returns login pages, 401/403
  responses, or SSO redirects for its content pages is completely opaque to
  agents. This check identifies the problem so site owners can make an
  informed decision about the tradeoff.
- **Result levels**:
  - **Pass**: Documentation pages return content (200 with substantive body)
    without requiring authentication.
  - **Warn**: Some pages are accessible but others require authentication
    (partial gating). This is common for sites that gate advanced content or
    API references while keeping tutorials public.
  - **Fail**: All or most documentation pages require authentication.
- **Recommended action**:
  - **Warn**: Consider ungating reference documentation and API guides.
    Agents can access public pages but will fall back on training data for
    gated content.
  - **Fail**: Agents cannot access your documentation and will rely on
    potentially outdated training data or secondary sources. Consider
    providing alternative access paths (see `auth-alternative-access`).
- **Automation**: Full. Fetch a sample of documentation URLs and classify
  responses: 200 with content (accessible), 401/403 (auth required), 200
  with login form heuristics (soft auth gate), or redirect to known SSO
  providers (auth redirect). Login form detection uses heuristics: look for
  `<input type="password">`, common SSO redirect domains (okta.com,
  auth0.com, login.microsoftonline.com), or page titles containing "sign in"
  or "log in".
- **Notes**: This check is informational for sites that intentionally gate
  content. It doesn't prescribe that all docs must be public. It ensures the
  site owner is aware of the agent accessibility impact and can evaluate
  whether alternative access paths (see below) are warranted.

### `auth-alternative-access`

- **What it checks**: Whether an auth-gated documentation site provides
  alternative access paths that agents can use.
- **Why it matters**: Sites that must gate their primary docs can still serve
  agents through secondary channels. This check looks for evidence that such
  channels exist, giving the site credit for providing agent access even when
  the main docs require a login.
- **Result levels**:
  - **Pass**: At least one alternative access path is detected (see list
    below).
  - **Warn**: The site provides partial alternative access (e.g., an
    `llms.txt` exists but only covers a subset of the gated content).
  - **Fail**: No alternative access paths detected for auth-gated content.
- **Recommended action**:
  - **Warn**: Expand alternative access to cover more of the gated
    documentation.
  - **Fail**: Consider providing a public `llms.txt`, ungating reference
    docs, shipping docs with your SDK, or providing an MCP server for
    authenticated access. See [Making Private Docs Agent-Accessible](#making-private-docs-agent-accessible)
    for options ordered by implementation effort.
- **Automation**: Partial. Some access paths can be detected automatically;
  others require manual verification.
- **Detectable access paths**:
  - **Public `llms.txt`**: The site serves an `llms.txt` file that doesn't
    require authentication, even if the underlying docs pages do. This gives
    agents at least a navigational index.
  - **Public markdown or API endpoint**: Some pages or a content API respond
    to unauthenticated requests even when the main docs UI requires login.
  - **Bundled documentation**: The product ships docs as part of its package
    or SDK (e.g., a `docs/` directory, man pages, or built-in `help`
    subcommands). Agents can read local files without authentication.
  - **CLI-based doc access**: The product provides a CLI command (e.g.,
    `yourproduct docs search "topic"`) that the developer has already
    authenticated, making content available to agents through tool use.
  - **MCP server**: The organization provides an MCP server that exposes
    documentation through tool calls, with authentication handled
    server-side. This is the most capable option for private docs because it
    preserves full content access while keeping credentials out of the agent
    context. (Detection is manual; there's no standard way to discover
    whether a company offers an MCP server.)
- **Notes**: Only applies when `auth-gate-detection` returns warn or fail.
  If docs are publicly accessible, this check is skipped.

### `bot-protection-interference`

- **What it checks**: Whether bot-protection systems (CDN bot management, WAF
  rules, behavioral rate enforcement) interfere with automated fetching of
  documentation content.
- **Why it matters**: Coding agents are automated clients. Bot management tuned
  for scraper and attack traffic frequently cannot distinguish an agent
  fetching docs on a developer's behalf from abuse, and its enforcement modes
  are worse for agents than a clean block because the failures are invisible:
  - **Challenge interstitials served as 200.** A "verifying your browser" page
    returned with a success status is a soft 404 from the agent's perspective;
    the agent extracts challenge boilerplate instead of documentation and may
    present it as an answer.
  - **Tarpits.** The server accepts the connection and returns headers, then
    holds the response body open indefinitely. The agent's fetch stalls until
    its own timeout with no error to reason about, and a multi-page reading
    session dies partway through.
  - **Volume-triggered throttling or blocking.** Enforcement engages only
    after several requests, so the first pages of a session succeed and later
    ones fail. Because enforcement is typically stateful (keyed to IP or
    client fingerprint) and decays over time, single-page spot checks look
    healthy while sustained agent sessions fail.

  These modes are not hypothetical. In one observed production case, a CDN's
  bot management responded to a sustained documentation scan by holding
  response bodies open indefinitely. Single-request probes of the same pages
  looked healthy throughout, and enforcement decayed after a cooldown period.
- **Result levels**:
  - **Pass**: A sustained multi-page scan completes with no evidence of
    interference: no challenge pages, no stalled response bodies, no
    volume-correlated failures. Because detection is heuristic and
    enforcement is stateful, pass means no interference was observed during
    this run, not a guarantee that bot protection will never engage.
  - **Warn**: Intermittent interference. Some requests during a sustained scan
    are challenged, stalled, or blocked while others succeed.
  - **Fail**: Sustained fetching is effectively blocked. Once enforcement
    triggers, most requests are challenged, stalled, or denied.
- **Recommended action**:
  - **Warn**: Identify which bot-management layer is challenging or stalling
    some requests and exempt public documentation routes from behavioral
    enforcement. Intermittent interference means enforcement thresholds sit
    close to normal agent reading cadence, so small configuration changes
    (or ordinary traffic growth) can tip it into sustained blocking.
  - **Fail**: Treat public documentation paths as automation-friendly in
    bot-management configuration. Exempt docs routes from behavioral
    enforcement, or scope enforcement to interactive product surfaces. Where
    limits are genuinely needed, prefer an explicit `429` with `Retry-After`
    over tarpits or silent blocks: a `429` is an error the agent can see,
    report, and react to, while a tarpit or challenge page fails invisibly.
    Never serve challenge interstitials with a 200 status.
- **Automation**: Heuristic. Interference generally cannot be probed directly
  without generating the sustained traffic that triggers it, so implementations
  should detect it as a byproduct of a normal scan: response bodies that stall
  past the request timeout, challenge-page heuristics in fetched content, or
  failure rates that climb as the scan progresses. Unlike other checks, this
  one has no fetch phase of its own; it is evaluated from evidence accumulated
  across the entire run rather than probed as a discrete step.

  A scan that follows this spec's guidance in
  [A Note on Responsible Use](#a-note-on-responsible-use) already resembles a
  realistic multi-page agent reading session, and that is the correct
  calibration, because that workload is exactly what this check predicts. If a
  respectful scan at agent-like cadence triggers enforcement, that is the
  finding, not a scan artifact. Implementations should not escalate traffic to
  deliberately provoke enforcement. Because enforcement is stateful and decays,
  results vary across runs; a clean run does not prove absence.
- **Notes**: When interference is detected mid-scan, results from other
  multi-page checks are computed on whatever sample survived. Implementations
  should surface a run-level warning that scores may not reflect the full site
  (see the [Bot Protection Degrading Scan Reliability](#bot-protection-degrading-scan-reliability)
  interaction effect). This check identifies the condition; it does not
  prescribe that sites disable bot protection. Like auth gating, this is a
  tradeoff the site owner should make deliberately, with awareness that coding
  agents are among the clients being blocked.

  Results are also vantage-point dependent. Enforcement is commonly keyed to
  client reputation (IP range, ASN, TLS fingerprint), so a scan run from
  datacenter infrastructure may trigger enforcement that residential traffic
  would not. This mirrors real agent traffic, which originates from the same
  mix of vantage points: some harnesses fetch from the developer's own
  connection, while others route web fetches through vendor server
  infrastructure or run in cloud-hosted sessions, both of which present
  datacenter IPs to the site. A datacenter-origin scan is representative of
  that second class of agent traffic, not a false positive. Implementations
  should note the scan's network context alongside results; even a coarse
  classification (a developer machine versus CI or cloud infrastructure)
  lets a reader interpret enforcement findings correctly. Reports should
  carry the classification rather than the scanner's raw IP address, since
  reports are often shared.

  This check is distinct from robots.txt and AI user-agent blocking, which
  this spec intentionally excludes (see
  [Appendix B](#robotstxt-and-ai-user-agent-blocking)). Declared crawling
  policy is invisible to most coding agents because they don't identify
  themselves; behavioral enforcement affects them precisely because their
  traffic is indistinguishable from the automated traffic it targets.

### Making Private Docs Agent-Accessible

This section offers non-normative guidance for organizations that gate their
documentation. The options below are ordered roughly by implementation effort,
from lowest to highest.

**1. Ungating reference documentation.** The simplest option: make API
references, SDK docs, and integration guides public while keeping truly
sensitive content (internal architecture, security configurations, pricing
tiers) behind auth. Many enterprises already do this for developer
experience reasons. Agents benefit from the same split.

**2. Shipping docs with the product.** Include documentation as local files
in your SDK, package, or CLI tool. A `docs/` directory with markdown files,
comprehensive README content, or built-in help text is always available to
agents reading the local filesystem. This is particularly effective for
API clients and libraries where the docs are version-specific anyway.

**3. Providing a public `llms.txt`.** Even if page content is gated, a
public `llms.txt` that describes what documentation exists and how it's
organized gives agents a map. They can tell the developer "the rate limiting
docs are at /docs/api/rate-limits, but I can't access them; could you paste
the relevant section?" This is better than the agent having no idea what
docs exist at all.

**4. Supporting token-based access for agent-facing endpoints.** Serve
`llms.txt` and markdown content behind API key or bearer token
authentication rather than browser-based SSO. Agents and their tooling can
be configured to pass static credentials, similar to how `npm` or `pip`
authenticate with private registries. This preserves access control while
enabling programmatic access.

**5. Building an MCP server.** An MCP server gives agents structured,
authenticated access to documentation through tool calls like
`search_docs("rate limiting")` or `get_doc("api/authentication")`. Auth
credentials are configured on the server; the agent never sees them. This
is the richest option because the MCP server can provide search, filtering,
and context-aware responses rather than just serving raw files. It also
allows fine-grained access control (different API keys could see different
content tiers).

**6. Providing a CLI with doc access.** If your product already has a CLI
that developers authenticate with, adding a `docs` subcommand gives agents
access through a channel the developer has already authorized. The agent
calls the CLI tool; the CLI handles authentication using the developer's
existing credentials.

Organizations don't need to implement all of these. A public `llms.txt`
combined with ungated reference docs covers the most common agent use cases
with minimal effort. MCP servers are for organizations that want to provide
a first-class agent experience with their private documentation.

---

## Checks Summary

| ID | Category | Automation | Severity | Depends On |
|----|----------|------------|----------|------------|
| [`llms-txt-exists`](#llms-txt-exists) | Content Discoverability | Full | High | -- |
| [`llms-txt-valid`](#llms-txt-valid) | Content Discoverability | Full | Medium | `llms-txt-exists` |
| [`llms-txt-size`](#llms-txt-size) | Content Discoverability | Full | High | `llms-txt-exists` |
| [`llms-txt-links-resolve`](#llms-txt-links-resolve) | Content Discoverability | Full | High | `llms-txt-exists` |
| [`llms-txt-links-markdown`](#llms-txt-links-markdown) | Content Discoverability | Full | Medium | `llms-txt-exists` |
| [`markdown-url-support`](#markdown-url-support) | Markdown Availability | Full | High | -- |
| [`content-negotiation`](#content-negotiation) | Markdown Availability | Full | Medium | -- |
| [`rendering-strategy`](#rendering-strategy) | Page Size | Heuristic | High | -- |
| [`page-size-markdown`](#page-size-markdown) | Page Size | Full | High | `markdown-url-support` or `content-negotiation` |
| [`page-size-html`](#page-size-html) | Page Size | Full | High | -- |
| [`page-size-transfer`](#page-size-transfer) | Page Size | Full | Medium | -- |
| [`content-start-position`](#content-start-position) | Page Size | Heuristic | High | -- |
| [`single-fetch-completeness`](#single-fetch-completeness) | Page Size | Heuristic | Medium | `markdown-url-support` or `content-negotiation` |
| [`tabbed-content-serialization`](#tabbed-content-serialization) | Content Structure | Heuristic | High | -- |
| [`section-header-quality`](#section-header-quality) | Content Structure | Heuristic | Medium | `tabbed-content-serialization` |
| [`markdown-code-fence-validity`](#markdown-code-fence-validity) | Content Structure | Full | Medium | `markdown-url-support` or `content-negotiation` |
| [`markdown-link-portability`](#markdown-link-portability) | Content Structure | Full | Medium | `markdown-url-support` or `content-negotiation` |
| [`embedded-data-serialization`](#embedded-data-serialization) | Content Structure | Heuristic | Medium | -- |
| [`http-status-codes`](#http-status-codes) | URL Stability | Full | Medium | -- |
| [`redirect-behavior`](#redirect-behavior) | URL Stability | Partial | Medium | -- |
| [`llms-txt-directive-html`](#llms-txt-directive-html) | Content Discoverability | Heuristic | High | -- |
| [`llms-txt-directive-md`](#llms-txt-directive-md) | Content Discoverability | Heuristic | Medium | `markdown-url-support` or `content-negotiation` |
| [`llms-txt-coverage`](#llms-txt-coverage) | Observability | Heuristic | High | `llms-txt-exists` |
| [`markdown-content-parity`](#markdown-content-parity) | Observability | Heuristic | Medium | `markdown-url-support` or `content-negotiation` |
| [`cache-header-hygiene`](#cache-header-hygiene) | Observability | Full | Medium | -- |
| [`auth-gate-detection`](#auth-gate-detection) | Authentication | Full | High | -- |
| [`auth-alternative-access`](#auth-alternative-access) | Authentication | Partial | Medium | `auth-gate-detection` (warn or fail) |
| [`bot-protection-interference`](#bot-protection-interference) | Authentication | Heuristic | High | -- |

## Interaction Effects

Individual checks measure discrete properties, but agent experience can degrade
non-linearly when certain failures combine. A site might pass most checks
individually while still being effectively inaccessible to agents because of how
the failures interact. This section describes known interaction patterns that
implementations should detect and surface. Implementations should evaluate these
after all individual checks have completed.

### Undiscoverable Markdown

**Checks involved**: `markdown-url-support`, `content-negotiation`,
`llms-txt-directive-html`, `llms-txt-directive-md`, `llms-txt-links-markdown`

**Observed behavior**: A site serves markdown at `.md` URLs, but agents have
no way to discover this capability. Without content negotiation, a directive on
pages pointing to llms.txt, or `.md` links in llms.txt, agents default to the
HTML path and never benefit from the markdown support the site provides.

This matters because markdown availability is one of the highest-impact
improvements a site can make, but only if agents can find it. A site in this
state has done the hard work of generating markdown but gets none of the
benefit.

### Truncated Index

**Checks involved**: `llms-txt-exists`, `llms-txt-size`

**Observed behavior**: A site provides llms.txt, but the file exceeds agent
context limits. Agents see the first portion of the file and lose
everything after the truncation point: links, structure, and entire sections
become invisible. Quality assessments of the truncated portion (link
resolution, coverage, markdown links) don't reflect what agents actually
experience.

Sites with large documentation sets are most likely to hit this. The spec's
progressive disclosure recommendation (splitting into a root index linking to
section-level files) directly addresses this pattern.

### Client-Rendered Pages

**Checks involved**: `rendering-strategy`, `page-size-html`,
`content-start-position`

**Observed behavior**: Pages that rely on client-side JavaScript rendering
return an empty shell to agents instead of documentation content. When this
affects a portion of a site's pages, HTML-path measurements (page size, content
start position) for those pages are measuring the shell, not the actual
content. Results from those checks become unreliable for affected pages.

This does not mean the site is entirely inaccessible. If the site also serves
markdown and agents can discover it, the markdown path still works. But agents
on the HTML path receive no usable content from affected pages.

### No Viable Content Path

**Checks involved**: `llms-txt-exists`, `rendering-strategy`,
`markdown-url-support`, plus the undiscoverable markdown pattern above

**Observed behavior**: Agents have no effective way to access the site's
documentation. There is no llms.txt for navigation, no discoverable markdown
path, and HTML responses either don't contain rendered content or weren't
tested. This is the lowest possible agent accessibility state.

This pattern represents a complete access failure rather than a degraded
experience. The single highest-impact action is creating an llms.txt at the
site root. If the site uses client-side rendering, enabling server-side
rendering is the second priority.

### Authenticated Docs Without Alternatives

**Checks involved**: `auth-gate-detection`, `auth-alternative-access`

**Observed behavior**: The site's documentation requires authentication, and no
alternative access paths were detected. Agents that encounter the docs fall
back on training data or seek secondary sources that may be inaccurate or
outdated.

Authentication is a legitimate choice for many documentation sites. This
pattern is notable because it means agents have no path to current content
at all. Even partial alternatives (a public llms.txt
as a navigational index, ungated API references, docs shipped with the
SDK/package) significantly improve the agent experience compared to a complete
access barrier.

### Bot Protection Degrading Scan Reliability

**Checks involved**: `bot-protection-interference`, plus every multi-page check

**Observed behavior**: Behavioral bot enforcement engages partway through a
scan. Requests that would have succeeded in isolation begin to stall, get
challenged, or fail, and every check still running is now scoring whatever
sample survives. The site's scores can look reasonable while being computed
from a fraction of the intended pages.

This pattern has two victims. Agents doing multi-page reading sessions lose
access mid-session, which is the site-side problem the check exists to
surface. And the assessment itself degrades: per-check "failed to fetch"
counts are scattered and easy to miss, so implementations should aggregate
fetch failures at run level and flag results prominently when the failure
rate is high (for example, above 20% of page fetches). A flagged run is
still useful evidence; it just measures a smaller sample than it appears to.

### Oversized Pages Without Markdown Escape

**Checks involved**: `page-size-html`, `markdown-url-support`, plus the
undiscoverable markdown pattern above

**Observed behavior**: Pages exceed agent context limits on the HTML path, and
there is no discoverable markdown path for agents to get smaller
representations. Agents receive truncated content on these pages with no warning and no
alternative available.

When pages are large but markdown is available and discoverable, agents that
support content negotiation or follow llms.txt directives can access smaller
representations. Without that escape hatch, truncation is unavoidable.

### Dynamic Content Rendered Statically

**Checks involved**: `markdown-content-parity`, `single-fetch-completeness`,
`markdown-link-portability`, `embedded-data-serialization`, plus the
Category 3 size checks

**Observed behavior**: A page whose content is dynamic (a filterable
catalog, a data-driven matrix, a widget-rendered listing) is flattened into
static markdown for agents, and the flattening fails in several ways at
once. There are four characteristic failure directions: too much (widget
data dumped wholesale into the content), too little (UI pagination
inherited into a format that didn't need it), inconsistent (default filters
or staleness making representations disagree), and unnavigable (generated
links that assume a browser context, or that are broken wholesale by the
generation pipeline).

One observed production catalog page exhibited all four simultaneously:
the HTML showed 98 items under a default filter while the markdown listed
102, the markdown was paginated with a trailing note and a continuation
URL that returned an empty body, and every entry link pointed into a wrong
generated path prefix that soft-404ed. Each individual check would flag
one symptom; the underlying cause is shared. The markdown variant is a
second rendering pipeline, and it needs the same QA the HTML pipeline
gets. Implementations that detect several of these failures on the same
generated page should present them as one pipeline problem rather than
four independent findings.

---

## Serving RAG Ingestion Pipelines

This section offers non-normative guidance for sites whose documentation is
consumed by retrieval-augmented generation systems: documentation Q&A bots,
docs MCP servers, and internal knowledge bases that chunk and embed content
into a vector store. RAG retrieval happens at query time from that index,
but ingestion has to get the content from somewhere first, and there are
two common paths:

- **Web ingestion** crawls the published site. It fetches like any
  automated client, so the properties that make a site agent-friendly at
  fetch time also make it index-friendly at ingestion time. The check
  mapping below applies to this path.
- **Source ingestion** reads the documentation source files (the markdown
  or MDX in the docs repository) directly, bypassing delivery entirely.
  This is common for teams indexing their own docs, and it is often a
  workaround for a site that is hostile to crawling; a site that passes
  this spec's checks makes web ingestion a viable alternative. Source
  ingestion trades delivery problems for build-system problems: the
  ingester is effectively a second renderer, and build-time constructs
  (component tags, includes, frontmatter, variable substitution) reach the
  index unrendered unless the pipeline handles them the way the site
  generator does. The result can be an index of content nobody publishes.
  These are source-format processability concerns, out of scope for this
  spec; note that they are also distinct from the repository-local
  documentation surface in [Related Surfaces](#related-surfaces), which
  concerns agents working interactively inside a repository, not batch
  pipelines reading its files.

This guidance is informed by consumer reports from production RAG builds.

How existing checks serve web ingestion:

- **Crawl manifest**: `llms-txt-exists` and `llms-txt-coverage` give
  ingesters a complete, curated URL set instead of sitemap heuristics, and
  the descriptions provide per-page metadata for free.
- **Clean source format**: `markdown-url-support` and `content-negotiation`
  let pipelines ingest markdown directly and skip HTML extraction, which is
  the largest source of ingestion noise. Sites failing `rendering-strategy`
  or `content-start-position` poison their own index: boilerplate and empty
  shells get embedded and then retrieved.
- **Chunk boundaries**: `section-header-quality` matters doubly for RAG.
  Chunkers split on section boundaries, and a chunk's header may be the
  only context it carries into retrieval. Self-describing headers produce
  self-describing chunks; generic headers ("Step 1") produce chunks that
  retrieve poorly and confuse whatever reads them. Content that flows
  across section boundaries without markers chunks badly in practice.
- **Incremental re-indexing**: `cache-header-hygiene` is more valuable for
  RAG than for live fetch. `ETag` and `Last-Modified` let pipelines detect
  what changed and re-embed only that, instead of re-crawling wholesale or
  serving a stale index.
- **Complete, navigable content**: `single-fetch-completeness` and
  `markdown-link-portability` failures propagate undetected into an index. A
  paginated catalog ingests as a partial catalog; broken generated links
  embed as broken references.

What this spec does not cover: embedding-friendly prose density, guidance on
writing self-contained sections, and metadata schemas for content
categorization. Those are content-composition concerns; see
[Related Surfaces](#related-surfaces).

## Appendix A: Known Platform Truncation Limits

The thresholds used in this spec's pass/warn/fail levels are derived from
observed and documented platform behavior. This appendix tracks known limits
so that implementations can calibrate their thresholds appropriately, and so
that the spec's default thresholds can be updated as more data becomes
available.

### Thresholds Used in This Spec

The spec uses two threshold tiers across its size-related checks:

- **50,000 characters**: The "pass" threshold. Content under this size fits
  comfortably within all known platform limits.
- **100,000 characters**: The "fail" threshold. Content over this size will be
  truncated by Claude Code and likely by most other platforms.

These are conservative defaults based on the best-documented platform (Claude
Code). Implementations should allow these thresholds to be configurable so
users can evaluate against specific platform limits or adjust as new data
becomes available.

`page-size-transfer` uses byte thresholds (1MB warn, 10MB fail) rather than
character thresholds, because it measures the response before any processing.
The 10MB fail line is anchored to Claude Code's documented fetch buffer;
byte-level caps on other platforms are less documented than character-level
truncation limits, so these defaults are conservative and should likewise be
configurable.

### Known Platform Limits

Compare platform architecture and truncation limits in [Platforms](https://agentdocsspec.com/platforms/).

### What This Means for Threshold Selection

The MCP Fetch reference server's default of 5,000 characters is worth noting.
Many agent setups use MCP-based fetch tools, and if users haven't changed the
default, they're working with a limit 20x smaller than Claude Code's. A page
that passes at the 50K threshold may still be unusable for MCP Fetch users
with default settings.

Implementations may want to support named profiles (e.g., `--profile
claude-code`, `--profile mcp-default`) that set thresholds to match specific
platforms, in addition to allowing custom threshold values.

## Appendix B: Notable Exclusions

This section documents topics that were considered for the spec but
intentionally excluded, along with the rationale.

### robots.txt and AI User-Agent Blocking

`robots.txt` can block known AI training crawlers (`ClaudeBot`, `GPTBot`,
`Google-Extended`, etc.) that identify themselves via user-agent strings.
However, this is a crawling policy concern rather than an agent-friendliness
concern, and the two audiences are distinct.

Training crawlers and coding agents are different request paths with different
user-agents. The agents this spec targets (coding assistants fetching docs
during real-time workflows) are largely invisible to `robots.txt`:

| Agent | User-Agent | Identifiable as AI? |
|-------|-----------|---------------------|
| Claude Code | `axios/1.8.4` | No (generic HTTP library) |
| Cursor | Standard Chrome UA | No |
| OpenCode | Standard Chrome UA | No |
| GitHub Copilot | Electron/VS Code UA | No (looks like normal IDE traffic) |
| OpenAI Codex | `ChatGPT-User/1.0` | Yes |
| Gemini CLI | `GoogleAgent-URLContext` | Yes |
| Windsurf | `colly` | Somewhat (Go scraping library) |

Source: [Checkly, "State of AI Agent Content
Negotiation"](https://www.checklyhq.com/blog/state-of-ai-agent-content-negotation/)

Most coding agents use standard browser user-agent strings and are
indistinguishable from human traffic. A site blocking `ClaudeBot` in
`robots.txt` is blocking Anthropic's training crawler, not Claude Code
fetching a docs page. Since this spec is about making documentation accessible
to agents in real-time workflows, `robots.txt` configuration is out of scope.

Behavioral bot protection is a different matter. Because most coding agents
don't identify themselves, bot-management systems that act on traffic behavior
rather than declared identity affect them even when crawling policy does not.
That failure mode is in scope; see
[`bot-protection-interference`](#bot-protection-interference).

### GitHub Raw URL Fallback

GitHub raw URLs (`raw.githubusercontent.com/...`) were observed to be the
single most reliable documentation access pattern in practice. When official
docs failed (rate-limited, JavaScript-rendered, or hard to navigate), GitHub
was almost always a viable fallback.

However, this is a fallback strategy for agent users rather than a property
of the documentation site itself. Whether a project's docs source happens to be on
GitHub, and whether the raw content there is usable as standalone
documentation, is outside the control of a docs site evaluation. This spec
focuses on what documentation site owners can do to improve agent
accessibility of their own sites.

## Contributing

This spec is a living document. Feedback, corrections, and contributions are
welcome.

- **Discussion and feedback**: Open an issue on the
  [GitHub repository](https://github.com/agent-ecosystem/agent-docs-spec/issues).
- **Proposing changes**: Submit a pull request. For significant changes (new
  checks, changes to pass/warn/fail criteria, new categories), please open an
  issue first to discuss the proposal.
- **Platform truncation data**: If you have data about a platform's web fetch
  truncation limits (from official documentation, reverse engineering, or
  empirical testing), please contribute it to the
  [Known Platform Limits](#known-platform-limits) table via issue or PR.
- **Real-world validation**: If you've run these checks against your own
  documentation site and have findings to share, we'd love to hear about it.

## References

- [llmstxt.org proposal](https://llmstxt.org)
- [Dachary Carey, "Agent-Friendly Docs"](https://dacharycarey.com/2026/02/18/agent-friendly-docs/)
- [Dachary Carey, "Agent Web Fetch Spelunking"](https://dacharycarey.com/2026/02/19/agent-web-fetch-spelunking/)
- [Giuseppe Gurgone, reverse-engineered Claude Code Web Fetch](https://giuseppegurgone.com/claude-webfetch)
- [Mikhail Shilkov, "Claude Code Web Tools"](https://mikhail.io/2025/10/claude-code-web-tools/)
- [Liran Yoffe, "Reverse Engineering Claude Code Web Tools"](https://medium.com/@liranyoffe/reverse-engineering-claude-code-web-tools-1409249316c3)
- [Checkly, "State of AI Agent Content Negotiation"](https://www.checklyhq.com/blog/state-of-ai-agent-content-negotation/)
- [Kody Jackson, "The speculative and soon to be outdated AI consumability scorecard"](https://kody-with-a-k.com/blog/2026/ai-consumability-scorecard/)
- [Longato, "LLMs.txt - Why Almost Every AI Crawler Ignores it"](https://www.longato.ch/llms-recommendation-2025-august/)
- [OtterlyAI, "llms.txt and AI Visibility: Results from OtterlyAI's GEO Study"](https://otterly.ai/blog/the-llms-txt-experiment/)

## Changelog

### v0.6.0 (2026-09-13)

- Added `bot-protection-interference` (Category 7: Authentication and Access).
  Detects bot-protection systems interfering with automated documentation
  fetching: challenge interstitials served as 200, tarpits that return headers
  and then stall the response body indefinitely, and volume-triggered
  throttling or blocking. Grounded in an observed production case where CDN
  bot management responded to a sustained scan by holding response bodies
  open; single-request probes looked healthy throughout, and enforcement
  decayed after a cooldown. Detection is heuristic, observed as a byproduct
  of a normal scan rather than a directed probe.
- Added the [Bot Protection Degrading Scan Reliability](#bot-protection-degrading-scan-reliability)
  interaction effect: when enforcement engages mid-scan, other checks score
  the surviving sample, so implementations should aggregate fetch failures at
  run level and flag results when the failure rate is high.
- Expanded the Category 7 introduction to cover infrastructure-level access
  barriers alongside authentication.
- Added `page-size-transfer` (Category 3: Page Size and Truncation Risk).
  Measures the served byte size of the HTML document response, a failure
  mode `page-size-html`'s post-conversion measurement cannot see. Grounded
  in measurements of production documentation sites where 75-84% of page
  bytes were serialized framework payloads (component trees, resolved
  metadata, embedded duplicate markdown source), with served-bytes-to-content
  ratios from 40:1 to 200:1. Scored on served bytes; the ratio is reported
  as a diagnostic.
- Documented the pipeline distinction in Category 3's "How Agents Get
  Content" section: convert-then-truncate, truncate-then-convert (or raw
  ingestion), and capped fetch, and which size measurement predicts each.
- Added `single-fetch-completeness` (Category 3: Page Size and Truncation
  Risk). Detects pagination in markdown responses and verifies the
  continuation is machine-followable. Grounded in an observed production
  catalog whose markdown variant showed 100 of 102 entries with a trailing
  relative continuation URL that returned an empty body, while the complete
  set would have fit well under the 50,000-character pass threshold.
- Added `markdown-link-portability` (Category 4: Content Structure). Links
  in served markdown should be absolute and should resolve to the
  representation they promise, verified beyond status codes (content type
  and soft-404 heuristics). Grounded in an observed production catalog
  whose generated markdown links all pointed into a wrong path prefix and
  soft-404ed as HTML SPA shells at `.md` URLs while returning 200.
- Added `embedded-data-serialization` (Category 4: Content Structure).
  Attributes page size to machine-generated bulk elements (large uniform
  tables, inline data blobs). Grounded in a measured production reference
  page: 302KB of HTML, 64% table markup including a single 218-row
  generated table, converting to ~83,000 characters while its non-table
  prose totaled ~17,000.
- Extended `markdown-content-parity` notes with guidance for dynamically
  generated pages: compare item counts between representations and
  distinguish default-filter divergence, pagination windowing, and
  staleness as causes.
- Added the [Dynamic Content Rendered Statically](#dynamic-content-rendered-statically)
  interaction effect: the four characteristic ways a dynamic page flattens
  badly into static markdown (too much, too little, inconsistent,
  unnavigable), observed together on a single production catalog page.
- Added the [Related Surfaces](#related-surfaces) subsection to Scope,
  naming the planned companion specifications (content composition,
  repository-local documentation) and the boundary that keeps this spec's
  checks mechanically verifiable.
- Added the [Serving RAG Ingestion Pipelines](#serving-rag-ingestion-pipelines)
  informational section, mapping existing checks to RAG ingestion needs
  (crawl manifest, clean source, chunk boundaries, incremental
  re-indexing), informed by consumer reports from production RAG builds.
  The Scope section's RAG exclusion now distinguishes query-time retrieval
  (out of scope) from ingestion (served by this spec).
- Restructured the website serving of the spec: the full document exceeded
  the 100,000-character truncation threshold its own checks warn about, so
  it is now served as per-category pages under `/spec/web/`, with `/spec/`
  becoming a landing page for this and future companion specifications.
  The canonical source remains a single SPEC.md in the repository. This
  breaks previously published deep URLs deliberately, in exchange for a
  namespace that accommodates the companion specs.
- Check count: 23 → 28.

### v0.5.1 (2026-05-08)

- Moved per-platform truncation data out of Appendix A into a new
  [Platforms](https://agentdocsspec.com/platforms/) comparison page on the
  site. Appendix A retains the spec's threshold rationale and points readers
  to the platforms page for current per-platform observations. Category 3
  (Page Size and Truncation Risk) now references the platforms page so
  readers can connect threshold choices to empirical pipeline behavior. No
  threshold or check definitions changed. Platforms page authored by
  Rhyannon Rodriguez.

### v0.5.0 (2026-04-25)

- Split `llms-txt-directive` into two independent checks:
  `llms-txt-directive-html` and `llms-txt-directive-md`. The original check
  conflated two distinct signals that serve different audiences. The HTML
  check detects directives in the rendered DOM (for agents fetching HTML
  pages); the markdown check detects directives in markdown source (for
  agents fetching `.md` URLs or using content negotiation). The split also
  adds explicit detection guidance: incidental mentions of `llms.txt` in
  navigation, metadata, or page content discussing the feature do not count
  as directives. `llms-txt-directive-md` depends on `markdown-url-support`
  or `content-negotiation`; it is skipped if neither passes. This is a
  breaking change for implementations that reference the old check ID.
- Check count: 22 → 23.

### v0.4.0 (2026-04-21)

- Renamed `llms-txt-freshness` to `llms-txt-coverage`. The check compares
  `llms.txt` URLs against the sitemap to measure how much of the site is
  represented; that's coverage, not freshness. Whether listed URLs still
  resolve is already handled by `llms-txt-links-resolve`. Rewrote the check
  description to match. This is a breaking change for implementations that
  reference the old check ID.
- Revised `page-size-html` and `content-start-position` to be
  pipeline-agnostic. The previous language prescribed a specific conversion
  approach (Turndown with default configuration) based on one agent's
  behavior. Agent HTML processing pipelines vary and continue to evolve;
  the spec now describes the measurement goal (approximate what agents see)
  and leaves conversion details to implementers. Recommended actions now
  cover all boilerplate sources (navigation, sidebars, serialized tabbed
  content) rather than focusing narrowly on inline CSS/JS.
- Expanded `llms-txt-coverage` to account for intentional curation. Many
  sites deliberately include only a subset of pages in `llms.txt` (excluding
  changelogs, old versions, directory pages, etc.). The check now describes
  three use cases (full parity, curated, hybrid) served by configurable
  thresholds and exclusion patterns, rather than treating all gaps as
  problems.
- Expanded `markdown-content-parity` to distinguish intentional audience
  segmentation from unintentional content drift. Some sites intentionally
  serve different content per audience (agent-optimized markdown vs.
  human-optimized HTML). The check now describes audience-segmentation tags
  as a mechanism implementations can recognize, and supports the same
  mirrored/segmented/curated spectrum as `llms-txt-coverage`. The spec does
  not prescribe specific tag conventions; implementations document which
  they support.

### v0.3.0 (2026-03-31)

- Merged Category 6 (Agent Discoverability Directives) into Category 1,
  renamed to "Content Discoverability." The `llms-txt-directive` check (now
  `llms-txt-directive-html` and `llms-txt-directive-md`) answers
  the same fundamental question as the llms.txt checks: can agents find and
  navigate the content? This reduces categories from 8 to 7.
- Renumbered Category 7 (Observability) to 6, Category 8 (Authentication) to 7.
- Added **Recommended action** field to all 22 check definitions. Provides
  1-2 sentence actionable guidance for each warn and fail state, giving
  documentation teams a clear next step rather than just a diagnosis.
- Added **Interaction Effects** section after Checks Summary. Documents six
  patterns where combinations of check results indicate systemic problems
  worse than individual failures suggest (e.g., undiscoverable markdown,
  no viable content path, oversized pages without markdown escape).
- Category count: 8 → 7. Check count unchanged at 22.

### v0.2.1 (2026-03-15)

Clarifications from implementing the `afdocs` conformance tool against the
spec. No new checks; all changes refine existing check definitions.

- `markdown-code-fence-validity`: Removed warn level. Per CommonMark,
  mismatched delimiters (opening ``` closing ~~~) produce unclosed fences,
  not a distinct "mismatched but balanced" state. The described warn case
  was indistinguishable from a fail.
- `llms-txt-directive` (now `llms-txt-directive-html` and
  `llms-txt-directive-md`): Clarified that pass requires the directive in
  all (or nearly all) pages, not just presence in any single page. Clarified
  warn triggers: missing from some pages, or present but buried past 50%.
- `llms-txt-freshness` (now `llms-txt-coverage`): Added default thresholds (>=95% pass, 80-95% warn,
  <80% fail) for sitemap coverage. The previous language was qualitative;
  implementations need concrete defaults for automation.
- `markdown-content-parity`: Added default thresholds (<5% missing pass,
  5-20% warn, >=20% fail) for content segment comparison. Same rationale.
- `section-header-quality`: Added default thresholds (<=25% generic pass,
  25-50% warn, >50% fail) and clarified that evaluation covers both
  within-group and cross-group header repetition.
- `cache-header-hygiene`: Added exception for responses with `ETag` or
  `Last-Modified` but no `Cache-Control`/`Expires`. These validation
  headers enable conditional revalidation and should not be penalized.
- `rendering-strategy`: Clarified that the note about downstream checks
  (`page-size-html`, `content-start-position`) being unreliable is guidance
  for report consumers, not an implementation dependency requirement.

### v0.2.0 (2026-03-15)

- New check: `rendering-strategy` (Category 3). Detects pages that rely on
  client-side JavaScript to render content, which makes them invisible to
  most coding agents. Covers full SPA shells and the subtler case of
  statically generated pages with client-side content population.
- Check count: 21 → 22.

### v0.1.0 (2026-02-22) - Initial Draft

- Initial spec with 21 checks across 8 categories.
- Progressive disclosure recommendation for large `llms.txt` files.
- Authentication and access category: auth gate detection, alternative access
  paths, and guidance for making private docs agent-accessible.
- Known platform truncation limits (Appendix A).
- Notable exclusions with rationale (Appendix B).
