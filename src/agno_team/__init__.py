"""agno-team CLI: ask the Contract Review Team to analyze a contract.

The contract is passed by reference (URL). The team leader delegates to the
remote Contract Analyzer, which fetches and analyzes the file. If that remote
agent is unreachable, the team runs with whatever members are up.
"""

from __future__ import annotations

import asyncio

from dotenv import load_dotenv

from agno_team.team import build_team

CONTRACT_URL = (
    "https://poc.viact.ai/contract-clause-analyzer/api/contracts/"
    "cmok2wy1d000gekttf5kue19x/file"
)

DEFAULT_PROMPT = (
    "Review the following contract for risk. Extract the key commercial and "
    "legal clauses, flag red flags and missing protections (liability caps, "
    "indemnity, termination, payment terms, retention, dispute resolution, "
    "force majeure, insurance), and finish with an overall risk rating and "
    "the top suggested fixes.\n\n"
    f"--- CONTRACT: {CONTRACT_URL}"
)


def main() -> None:
    """CLI entrypoint: `uv run agno-team`."""
    load_dotenv()  # GOOGLE_API_KEY + remote agent config from .env

    team = build_team()
    # Async path is required: a RemoteAgent member only implements arun(), and
    # aprint_response is a coroutine — it must be awaited or nothing executes.
    asyncio.run(team.aprint_response(DEFAULT_PROMPT, stream=True))


__all__ = ["build_team", "main"]
