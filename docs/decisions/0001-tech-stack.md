---
parent: Decisions
nav_order: 100
title: Tech Stack

<!-- markdownlint-disable-next-line MD025 -->
# Use a known tech stack to speed up development

## Context and Problem Statement

We want to get to a POC quickly. Decide on a tech stack that will get us there and be flexible enough to work.

## Considered Options

* Rust (faster, learning)
* Django for the web side
* React for the web interface (learning)
* toml or yaml for the config
* Tailwind for styling

## Decision Outcome

Chosen options:

* Python, because it's easy
* python-fuse, because it has all the tools
* flask or just files put together with python-fuse
* Vue for frontend
* Bootstrap

### Consequences

* Fast dev
* Simple to understand
