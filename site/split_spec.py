#!/usr/bin/env python3
"""Split SPEC.md into per-category site pages under content/spec/web/.

The canonical spec is a single document (SPEC.md). This script serves it as
multiple pages, following the spec's own progressive disclosure
recommendation. It:

- splits on H2 boundaries (fence-aware: headings inside ``` / ~~~ code
  blocks are not section boundaries)
- assembles pages per the MANIFEST below
- builds a global anchor map and rewrites intra-document links: same-page
  links stay fragments, cross-page links become absolute URLs (per the
  spec's own `markdown-link-portability` check)
- emits Hugo front matter per page and a contents list at the top of the
  overview page

Usage: split_spec.py <SPEC.md path> <content/spec/web dir>
"""

import re
import sys
from pathlib import Path

BASE_URL = "https://agentdocsspec.com/spec/web/"

# page slug -> (title, description, weight)
PAGES = {
    "_index": (
        "Web Documentation Delivery Spec",
        "How well a documentation site serves coding agents: scope, terminology, and the summary of all 28 checks.",
        0,
    ),
    "content-discoverability": (
        "Category 1: Content Discoverability",
        "Checks for llms.txt existence, validity, size, link quality, and directives that point agents to it.",
        1,
    ),
    "markdown-availability": (
        "Category 2: Markdown Availability",
        "Checks for .md URL variants and content negotiation via Accept headers.",
        2,
    ),
    "page-size": (
        "Category 3: Page Size and Truncation Risk",
        "Checks for rendering strategy, markdown/HTML/transfer size, content start position, and single-fetch completeness.",
        3,
    ),
    "content-structure": (
        "Category 4: Content Structure",
        "Checks for tabbed content serialization, header quality, code fence validity, link portability, and embedded data.",
        4,
    ),
    "url-stability": (
        "Category 5: URL Stability and Redirects",
        "Checks for HTTP status code honesty and redirect behavior.",
        5,
    ),
    "observability": (
        "Category 6: Observability and Content Health",
        "Checks for llms.txt coverage, markdown/HTML content parity, and cache header hygiene.",
        6,
    ),
    "authentication": (
        "Category 7: Authentication and Access",
        "Checks for auth gating, alternative access paths, and bot-protection interference.",
        7,
    ),
    "interaction-effects": (
        "Interaction Effects",
        "How individual check failures combine into non-linear agent experience degradation.",
        8,
    ),
    "appendices": (
        "Appendices",
        "Known platform truncation limits and notable exclusions.",
        9,
    ),
    "changelog": (
        "Changelog",
        "Version history of the Agent-Friendly Documentation Spec.",
        10,
    ),
}

# H2 heading text -> page slug. Headings not listed here go to the overview.
MANIFEST = {
    "Category 1: Content Discoverability": "content-discoverability",
    "Category 2: Markdown Availability": "markdown-availability",
    "Category 3: Page Size and Truncation Risk": "page-size",
    "Category 4: Content Structure": "content-structure",
    "Category 5: URL Stability and Redirects": "url-stability",
    "Category 6: Observability and Content Health": "observability",
    "Category 7: Authentication and Access": "authentication",
    "Interaction Effects": "interaction-effects",
    "Appendix A: Known Platform Truncation Limits": "appendices",
    "Appendix B: Notable Exclusions": "appendices",
    "Changelog": "changelog",
}


def github_anchor(heading: str) -> str:
    """GitHub/Goldmark-style anchor from a heading line's text."""
    text = heading.strip().lstrip("#").strip()
    text = text.replace("`", "")
    text = text.lower()
    text = re.sub(r"[^\w\- ]", "", text)
    text = text.replace(" ", "-")
    return text


def split_sections(lines):
    """Yield (h2_title_or_None, [lines]) fence-aware; first item is preamble."""
    sections = []
    current_title = None
    current = []
    fence = None
    for line in lines:
        m = re.match(r"^(```+|~~~+)", line)
        if m:
            tick = m.group(1)[0] * 3
            if fence is None:
                fence = tick
            elif line.strip().startswith(fence):
                fence = None
        if fence is None and line.startswith("## ") and not line.startswith("###"):
            sections.append((current_title, current))
            current_title = line[3:].strip()
            current = [line]
        else:
            current.append(line)
    sections.append((current_title, current))
    return sections


def collect_anchors(page_lines, slug, anchor_map):
    fence = None
    for line in page_lines:
        m = re.match(r"^(```+|~~~+)", line)
        if m:
            tick = m.group(1)[0] * 3
            if fence is None:
                fence = tick
            elif line.strip().startswith(fence):
                fence = None
            continue
        if fence is None and re.match(r"^#{1,6} ", line):
            anchor = github_anchor(line)
            if anchor in anchor_map and anchor_map[anchor] != slug:
                print(
                    f"WARNING: duplicate anchor '{anchor}' on "
                    f"{anchor_map[anchor]} and {slug}; keeping first",
                    file=sys.stderr,
                )
                continue
            anchor_map[anchor] = slug


def rewrite_links(text, slug, anchor_map, page_title_anchors):
    def repl(m):
        label, anchor = m.group(1), m.group(2)
        target = anchor_map.get(anchor)
        if target is None:
            print(f"WARNING: unresolved anchor '#{anchor}' on {slug}", file=sys.stderr)
            return m.group(0)
        if target == slug:
            return m.group(0)
        page_path = "" if target == "_index" else f"{target}/"
        if anchor in page_title_anchors:
            return f"[{label}]({BASE_URL}{page_path})"
        return f"[{label}]({BASE_URL}{page_path}#{anchor})"

    return re.sub(r"\[([^\]]+)\]\(#([\w\-]+)\)", repl, text)


def main():
    spec_path = Path(sys.argv[1])
    out_dir = Path(sys.argv[2])
    out_dir.mkdir(parents=True, exist_ok=True)

    lines = spec_path.read_text(encoding="utf-8").splitlines()
    sections = split_sections(lines)

    # Assemble pages in source order.
    pages = {slug: [] for slug in PAGES}
    page_title_anchors = set()
    for title, body in sections:
        if title is None:
            # Preamble: drop the document H1 (layout renders the page title).
            body = [ln for ln in body if not ln.startswith("# ")]
            pages["_index"].extend(body)
            continue
        slug = MANIFEST.get(title, "_index")
        if slug != "_index" and title in MANIFEST:
            # The H2 that *is* the page (category pages, interaction
            # effects, changelog) becomes the page title; appendices keep
            # their H2s because two sections share one page.
            if slug not in ("appendices",):
                page_title_anchors.add(github_anchor("## " + title))
                body = body[1:]  # drop the H2 line itself
        pages[slug].extend(body)

    # Global anchor map (title anchors map to their page root).
    anchor_map = {}
    for title, slug in MANIFEST.items():
        anchor_map[github_anchor("## " + title)] = slug
    for slug, body in pages.items():
        collect_anchors(body, slug, anchor_map)

    # Contents list at the top of the overview.
    contents = ["## Spec Contents", ""]
    for slug, (title, desc, weight) in sorted(PAGES.items(), key=lambda i: i[1][2]):
        if slug == "_index":
            continue
        contents.append(f"- [{title}]({BASE_URL}{slug}/): {desc}")
    contents.append("")

    for slug, body in pages.items():
        title, desc, weight = PAGES[slug]
        text = "\n".join(body).strip("\n") + "\n"
        text = rewrite_links(text, slug, anchor_map, page_title_anchors)
        # Strip trailing/leading horizontal rules left over from section joins.
        text = re.sub(r"^\s*---\s*\n", "", text)
        text = re.sub(r"\n---\s*$", "\n", text)
        header = [
            "---",
            f'title: "{title}"',
            f'description: "{desc}"',
            f"weight: {weight}",
            "showTableOfContents: true",
            "---",
            "",
        ]
        if slug == "_index":
            nav = "\n".join(contents) + "\n"
            # Insert contents list right after the status table (before Abstract).
            idx = text.find("## Abstract")
            text = text[:idx] + nav + text[idx:] if idx >= 0 else nav + text
            out_path = out_dir / "_index.md"
        else:
            backlink = (
                f"Part of the [Web Documentation Delivery Spec]({BASE_URL}). "
                f"The [Checks Summary]({BASE_URL}#checks-summary) lists all "
                f"checks with links to their definitions.\n\n"
            )
            text = backlink + text
            out_path = out_dir / f"{slug}.md"
        out_path.write_text("\n".join(header) + text, encoding="utf-8")
        print(f"  {out_path}  ({len(text)} chars)")


if __name__ == "__main__":
    main()
