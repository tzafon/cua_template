# CUA Template

A browser automation agent using Tzafon's computer use API.

## Setup

```bash
uv sync
```

## Configuration

Set your Tzafon API key as an environment variable:

```bash
export TZAFON_API_KEY="your_api_key_here"
```

## Usage

```bash
TZAFON_API_KEY="your_key" uv run python -m core.main
```

Or modify the task in `src/core/main.py`:

```python
agent_loop("Your task here", start_url="https://example.com")
```

