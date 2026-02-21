# Agent-Friendly Documentation Spec

|              |                                                              |
|--------------|--------------------------------------------------------------|
| **Status**   | Draft                                                        |
| **Version**  | 0.1.0                                                        |
| **Date**     | 2026-02-21                                                   |
| **Author**   | Dachary Carey                                                |
| **URL**      | https://agentdocsspec.com                                    |
| **Repository** | https://github.com/dacharyc/agent-docs-spec                |

## Abstract

Documentation sites are increasingly consumed by coding agents rather than
human readers, but most sites are not built for this access pattern. Agents
hit truncation limits, get walls of CSS instead of content, can't follow
cross-host redirects, and don't know about emerging discovery mechanisms like
`llms.txt`. This spec defines 16 checks across 6 categories that evaluate how
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
  ingest content at build time, not at query time, so truncation limits and
  real-time fetch behavior are less relevant.

The findings and checks in this spec are grounded in empirical observation of
coding agents. Some recommendations (like providing `llms.txt` and serving
markdown) will benefit other consumers too, but the pass/warn/fail criteria
are calibrated for the coding agent use case.

## Background

Agents don't use docs like humans. They retrieve URLs from training data rather
than navigating table-of-contents structures. They struggle with HTML-heavy
pages, silently lose content to truncation, and don't know about emerging
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

- **Normative sections**: Category 1-6 check definitions, Checks Summary
  table.
- **Informational sections**: Background, Scope, Start Here, "How Agents Get
  Content", "Who Actually Uses llms.txt?", Progressive Disclosure
  recommendation, Appendices.

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
   Anthropic does this; it works.
   Check: `llms-txt-directive`

5. **Don't break your URLs.** If you must move content, use same-host HTTP
   redirects. Avoid cross-host redirects, JavaScript redirects, and soft 404s.
   Checks: `http-status-codes`, `redirect-behavior`

## Spec Structure

Each check has:

- **ID**: A short identifier (e.g., `llms-txt-exists`).
- **Category**: The area of agent-friendliness it evaluates.
- **What it checks**: A description of what the check evaluates.
- **Why it matters**: The observed agent behavior that motivates the check.
- **Result levels**: What constitutes a pass, warn, or fail.
- **Automation**: Whether the check can be fully automated, partially automated
  (heuristic), or is advisory only.

### Check Dependencies

Some checks depend on the results of others:

- `llms-txt-valid`, `llms-txt-size`, `llms-txt-links-resolve`, and
  `llms-txt-links-markdown` only run if `llms-txt-exists` passes.
- `page-size-markdown` only runs if `markdown-url-support` or
  `content-negotiation` passes (the site must serve markdown for this check
  to apply).
- `section-header-quality` is most relevant when `tabbed-content-serialization`
  detects tabbed content.
- `markdown-code-fence-validity` only runs if `markdown-url-support` or
  `content-negotiation` passes (the site must serve markdown for this check
  to apply). It also runs against any discovered `llms.txt` files.

Implementations should run checks in category order (1 through 6) and skip
dependent checks when their prerequisites fail.

### A Note on Responsible Use

This spec describes checks that involve making HTTP requests to documentation
sites. Implementations should be respectful of the sites being evaluated:
introduce delays between requests, cap concurrent connections, honor
`Retry-After` headers, and avoid overwhelming sites with traffic. The goal is
to help documentation teams improve agent accessibility, not to load-test
their infrastructure.

---

## Category 1: llms.txt

These checks evaluate whether the site provides an `llms.txt` file and whether
that file is useful to agents.

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
- **Automation**: Full.
- **Recommendation**: See [Progressive Disclosure for Large Documentation
  Sets](#progressive-disclosure-for-large-documentation-sets) below.

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
- **Automation**: Full.

---

## Category 3: Page Size and Truncation Risk

These checks evaluate whether page content fits within the processing limits of
agent web fetch pipelines. Truncation is silent: the agent doesn't know it's
working with partial data.

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
- **Automation**: Full.
- **Notes**: If the site doesn't serve markdown at all, this check is skipped
  and `page-size-html` becomes the primary size check. The report should note
  that the site relies entirely on the HTML path.

### `page-size-html`

- **What it checks**: The character count of the HTML response, and the
  character count after simulating an HTML-to-markdown conversion (using a
  Turndown-equivalent pipeline). Reports both numbers.
- **Why it matters**: Most agents receive HTML, not markdown. The raw HTML size
  determines whether the page even fits in the fetch buffer (Claude Code caps
  at ~10MB). The post-conversion size is closer to what the agent's
  summarization model actually sees, but conversion is lossy and
  unpredictable. A 500KB HTML page might convert to 50KB of useful markdown
  (safe) or 400KB of markdown including raw CSS text that survived conversion
  (not safe). Both numbers matter.
- **Result levels** (based on post-conversion size, since that's what the
  model receives):
  - **Pass**: Converted content under 50,000 characters.
  - **Warn**: Converted content between 50,000 and 100,000 characters.
  - **Fail**: Converted content over 100,000 characters.
- **Automation**: Full. Use a Turndown-equivalent library with default
  configuration (no explicit `<style>`/`<script>` stripping) to match observed
  agent behavior.
- **Report details**: Show both the raw HTML size and the post-conversion size.
  A large gap between the two indicates heavy boilerplate. Report the
  conversion ratio (e.g., "505KB HTML -> 12KB markdown (98% boilerplate)")
  as a useful signal for site owners.

### `content-start-position`

- **What it checks**: How far into the **post-conversion** content (by character
  count and as a percentage) the actual documentation content begins.
- **Why it matters**: Even after HTML-to-markdown conversion, boilerplate can
  survive. Turndown's default configuration doesn't strip `<style>` tag
  contents; it dumps CSS rules as raw text into the markdown output. If inline
  CSS and JavaScript consume most of the truncation budget, the summarization
  model never sees the documentation content. In one observed case, actual
  content didn't start until 87% of the way through the HTML response (441K
  characters of CSS before the first paragraph), and the post-conversion
  output was still dominated by CSS text.
- **Result levels**:
  - **Pass**: Content starts within the first 10% of the post-conversion
    output.
  - **Warn**: Content starts between 10% and 50%.
  - **Fail**: Content starts after 50%.
- **Automation**: Heuristic. Detect first meaningful content element (heading,
  paragraph with prose) after stripping obvious boilerplate patterns (CSS
  rules, JavaScript, navigation text).
- **Notes**: This check only applies to the HTML path. Markdown served directly
  by the site should not have boilerplate preamble; if it does, that's a
  separate issue worth flagging but not something this check targets.

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
- **Result levels**:
  - **Pass**: Headers within serialized tabbed sections include variant context.
  - **Warn**: Headers are present but generic/repeated across variants.
  - **Fail**: No distinguishing headers in serialized tabbed content.
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
  - **Warn**: Code fences are technically balanced but use inconsistent
    delimiters (e.g., opening with `` ``` `` and closing with `~~~`), which
    some parsers may not match correctly.
  - **Fail**: One or more unclosed code fences detected.
- **Automation**: Full. Parse the markdown for fence delimiters (`` ``` `` and
  `~~~`, with optional info strings) and verify each opening delimiter has a
  matching close. Run against markdown served via `.md` URLs, content
  negotiation responses, and `llms.txt` files.
- **Notes**: This check applies to markdown the site authors and serves
  directly. Code fences broken by an HTML-to-markdown conversion pipeline are
  outside the site owner's control, though implementations may optionally flag
  them as informational findings.

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
- **Automation**: Partial. HTTP redirects are detectable. JavaScript redirects
  require fetching the page and scanning for `window.location`, `meta refresh`,
  or similar patterns.

---

## Category 6: Agent Discoverability Directives

These checks evaluate whether the site includes signals that help agents find
and navigate content effectively.

### `llms-txt-directive`

- **What it checks**: Whether documentation pages include a visible directive
  pointing agents to `llms.txt` or another discovery resource.
- **Why it matters**: Anthropic embeds a directive at the top of every Claude
  Code docs page: a blockquote telling agents to fetch the documentation index
  at `llms.txt`. In practice, agents see this directive, follow it, and use the
  index to find what they need. It's simple, low-effort, and observed to work in
  real agent workflows. This is the agent equivalent of a "You Are Here" marker.
- **Result levels**:
  - **Pass**: A directive pointing to `llms.txt` (or equivalent index) is
    present in page content, ideally near the top.
  - **Warn**: A directive exists but is buried deep in the page (may be past
    truncation).
  - **Fail**: No agent-facing directive detected.
- **Automation**: Heuristic. Search for patterns like links to `llms.txt`,
  phrases like "documentation index", or blockquote directives near the top of
  page content.

---

## Checks Summary

| ID | Category | Automation | Severity | Depends On |
|----|----------|------------|----------|------------|
| `llms-txt-exists` | llms.txt | Full | High | -- |
| `llms-txt-valid` | llms.txt | Full | Medium | `llms-txt-exists` |
| `llms-txt-size` | llms.txt | Full | High | `llms-txt-exists` |
| `llms-txt-links-resolve` | llms.txt | Full | High | `llms-txt-exists` |
| `llms-txt-links-markdown` | llms.txt | Full | Medium | `llms-txt-exists` |
| `markdown-url-support` | Markdown Availability | Full | High | -- |
| `content-negotiation` | Markdown Availability | Full | Medium | -- |
| `page-size-markdown` | Page Size | Full | High | `markdown-url-support` or `content-negotiation` |
| `page-size-html` | Page Size | Full | High | -- |
| `content-start-position` | Page Size | Heuristic | High | -- |
| `tabbed-content-serialization` | Content Structure | Heuristic | High | -- |
| `section-header-quality` | Content Structure | Heuristic | Medium | `tabbed-content-serialization` |
| `markdown-code-fence-validity` | Content Structure | Full | Medium | `markdown-url-support` or `content-negotiation` |
| `http-status-codes` | URL Stability | Full | Medium | -- |
| `redirect-behavior` | URL Stability | Partial | Medium | -- |
| `llms-txt-directive` | Agent Discoverability | Heuristic | Medium | -- |

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

### Known Platform Limits

| Platform | Truncation Limit | Source | Confidence | Notes |
|----------|-----------------|--------|------------|-------|
| Claude Code | ~100,000 chars | Reverse engineering | High | Truncates post-HTML-to-markdown conversion. Trusted sites serving `text/markdown` under 100K chars bypass summarization model entirely. |
| MCP Fetch (reference server) | 5,000 chars (default) | [Official docs](https://pypi.org/project/mcp-server-fetch/) | High | Default `max_length` is 5,000 chars. Configurable up to 1,000,000. Supports chunked reading via `start_index`. |
| Claude API (web_fetch tool) | Configurable via `max_content_tokens` | [Official docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool) | High | Distinct implementation from Claude Code client-side tool. |
| Google Gemini (URL context) | 34 MB per URL | [Official docs](https://ai.google.dev/gemini-api/docs/url-context) | Medium | Max fetch size; unclear how much reaches the model after processing. |
| OpenAI (web search) | 128K token context window | [Official docs](https://developers.openai.com/api/docs/guides/tools-web-search) | Medium | `search_context_size` parameter (low/medium/high). Limit applies to the overall context, not per-page. |
| Cursor | Unknown | -- | -- | Requests `text/markdown` via Accept header. No documented truncation limit. |
| GitHub Copilot | Unknown | -- | -- | No documented web fetch or truncation details. |
| Windsurf | Unknown | [Brief docs](https://docs.windsurf.com/windsurf/cascade/web-search) | Low | States it "chunks up web pages" and "skims to the section we want." No specific limits. |

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
However, this is a crawling policy concern, not an agent-friendliness concern,
and the two audiences are distinct.

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

### GitHub Raw URL Fallback

GitHub raw URLs (`raw.githubusercontent.com/...`) were observed to be the
single most reliable documentation access pattern in practice. When official
docs failed (rate-limited, JavaScript-rendered, or hard to navigate), GitHub
was almost always a viable fallback.

However, this is a fallback strategy for agent users, not a property of the
documentation site itself. Whether a project's docs source happens to be on
GitHub, and whether the raw content there is usable as standalone
documentation, is outside the control of a docs site evaluation. This spec
focuses on what documentation site owners can do to improve agent
accessibility of their own sites.

## Contributing

This spec is a living document. Feedback, corrections, and contributions are
welcome.

- **Discussion and feedback**: Open an issue on the
  [GitHub repository](https://github.com/dacharyc/agent-docs-spec/issues).
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

### v0.1.0 (2026-02-21) - Initial Draft

- Initial spec with 16 checks across 6 categories.
- Progressive disclosure recommendation for large `llms.txt` files.
- Known platform truncation limits (Appendix A).
- Notable exclusions with rationale (Appendix B).
