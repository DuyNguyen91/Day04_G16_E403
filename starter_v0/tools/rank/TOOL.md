---
name: rank
track: team
kind: local_ranker
requires_env: []
inputs: [items, query, top_k]
outputs: [items, scores, item_count]
side_effect: false
---
# rank

Ranks already-collected research items by keyword overlap with a query.
Does not fetch new data. Use after lookup/fetch/timeline/social_search when the
user wants the most relevant subset.
