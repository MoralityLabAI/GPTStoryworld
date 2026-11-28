"""Storyworld MCP server: the tools behind the Storyworld GDK app.

Three modes share one workspace of storyworlds:

- ``builder``: whole-world tools for large-context models (the storyworld-builder skill).
- ``small``: one-encounter cards and micro-edits under a fixed packet budget (the small-storyworld skill).
- ``hypergames``: exact hyperworld eval families for frontier models (the hypergames skill).

Every write is validated with the repo's ``sweepweave_validator.py``; a write that would introduce
validator errors is refused and the world is left unchanged.
"""

VERSION = "0.1.0"
