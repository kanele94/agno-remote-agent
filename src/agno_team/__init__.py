"""agno-team: a minimal, runnable example of an Agno multi-agent team."""

from __future__ import annotations

import asyncio
import sys

from dotenv import load_dotenv

from .team import build_team

DEFAULT_PROMPT = (
    "What can I do, suggest some tasks for me? I can analyze contract clauses, write code, and more!"
)


def main() -> None:
    """CLI entrypoint: `uv run agno-team \"your question\"`."""
    load_dotenv()  # load GOOGLE_API_KEY (and optional GEMINI_MODEL) from .env

    prompt = " ".join(sys.argv[1:]).strip() or DEFAULT_PROMPT

    team = build_team()
    # Run async: a RemoteAgent member only implements arun(), so the team's
    # async delegation path is required. The sync path would call member.run()
    # which RemoteAgent does not provide.
    asyncio.run(team.aprint_response(prompt, stream=True))


__all__ = ["build_team", "main"]
