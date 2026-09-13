---
title: "Specifications"
description: "The Agent-Friendly Documentation Spec family: web delivery today, with companion specifications planned for content composition and repository-local docs."
showChildPages: false
---

Agent-friendly documentation has more than one surface. This page is the
home for the specification family; each spec covers one surface and
versions independently.

## Available now

- **[Web Documentation Delivery Spec](https://agentdocsspec.com/spec/web/)**:
  28 checks across 7 categories evaluating whether coding agents can
  discover, fetch, and receive a documentation site's content intact.
  Covers llms.txt discovery, markdown availability, page size and
  truncation risk, content structure, URL stability, observability, and
  authentication/access. This spec was formerly served in full at this
  URL; it now lives at `/spec/web/`, split into per-category pages so that
  each page fits comfortably within agent fetch limits (its own
  recommendation, applied to itself).

## Planned

Companion specifications will be added here as the evidence base for them
matures (see [Related Surfaces](https://agentdocsspec.com/spec/web/#related-surfaces)
in the web delivery spec):

- **Content composition**: what documentation should contain to serve
  agents well: factual consistency across pages, structure and density
  suited to machine consumption.
- **Repository-local documentation**: docs serving coding agents that work
  inside a repository, where discovery happens through grep and file
  listings rather than HTTP.

## Implementation

[afdocs](https://github.com/agent-ecosystem/afdocs) is the reference
implementation of the web delivery spec: `npx afdocs check <url>` tests a
documentation site against it.
