"""Smoke-test the remote Contract Analyzer over A2A.

Loads .env, builds the authenticated RemoteAgent proxy, confirms the remote
agent card is reachable, then sends one real query and prints the response.
"""

from __future__ import annotations

import asyncio
import os

from dotenv import load_dotenv

from agno_team.agents import contract_analyzer_remote

TEST_QUERY = (
    "Quick test: in one sentence, what kinds of contract clauses do you analyze?"
)


async def main() -> None:
    load_dotenv()
    print(f"[test] URL   : {os.getenv('CONTRACT_REMOTE_AGENT_URL')}")
    print(f"[test] ID    : {os.getenv('CONTRACT_REMOTE_AGENT_ID', 'contract-clause-analyzer')}")
    print(f"[test] Token : {'set' if os.getenv('CONTRACT_REMOTE_AGENT_TOKEN') else 'MISSING'}")

    agent = contract_analyzer_remote()
    if agent is None:
        print("[test] FAIL — remote agent unreachable (see message above).")
        return

    print(f"[test] OK — connected. Remote agent name: {agent.name!r}")
    print(f"[test] Sending query: {TEST_QUERY!r}\n")

    resp = await agent.arun(TEST_QUERY)
    content = getattr(resp, "content", resp)
    print("[test] Response:\n")
    print(content)


if __name__ == "__main__":
    asyncio.run(main())
