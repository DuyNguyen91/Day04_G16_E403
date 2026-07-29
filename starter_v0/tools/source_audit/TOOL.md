# source_audit

Audit research items before a digest is published.

## Use when

- The user explicitly asks to check citations, source coverage, or source diversity.
- Research items already exist and need a deterministic quality check.

## Do not use when

- Sources still need to be discovered (`lookup`, `social_search`, or `timeline`).
- A URL needs to be read (`fetch`).
- The user only wants presentation (`format`).

## Contract

`source_audit(items, min_sources=2)` returns counts, unique source domains, item-level
issues, and `ready`. An item should contain a non-empty title, an HTTP(S) URL, and a
summary. `ready` is true only when every item passes and the minimum number of
distinct source domains is met. This tool performs no network requests.
