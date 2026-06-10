"""Member agents for the contract-review team.

Each agent masters one narrow domain. The team leader (see team.py) decides
which member(s) to delegate to based on the user's request. The deep
Contract Analyzer is a RemoteAgent running in a separate AgentOS process.
"""

from __future__ import annotations
import os
from agno.agent.remote import RemoteAgent


class _AuthenticatedRemoteAgent(RemoteAgent):
    """A RemoteAgent that attaches a bearer token to every request.

    The base RemoteAgent only accepts ``auth_token`` as a per-call argument on
    ``run``/``arun`` — it is NOT a constructor parameter. But the Team invokes
    members via ``arun()`` without forwarding any token, so an authenticated A2A
    server would reject every delegated call. We store the token and inject it
    into each call so the team's delegations carry the Authorization header.
    """

    def __init__(self, *args, auth_token: str, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._auth_token = auth_token

    def run(self, *args, **kwargs):  # type: ignore[override]
        kwargs.setdefault("auth_token", self._auth_token)
        return super().run(*args, **kwargs)

    def arun(self, *args, **kwargs):  # type: ignore[override]
        kwargs.setdefault("auth_token", self._auth_token)
        return super().arun(*args, **kwargs)

def contract_analyzer_remote() -> RemoteAgent | None:
    """Proxy to the Contract Analyzer served over the A2A protocol.

    Returns None if that server is unreachable, so the team still runs with its
    local members. Configure via env:
      CONTRACT_REMOTE_AGENT_URL  — A2A base url for the agent
      CONTRACT_REMOTE_AGENT_ID   — remote agent id
      CONTRACT_REMOTE_AGENT_TOKEN — bearer token (e.g. aak_...)
    """
    base_url = os.getenv(
        "CONTRACT_REMOTE_AGENT_URL",
        "http://localhost:3002/a2a/agents/contract-clause-analyzer",
    )
    agent_id = os.getenv("CONTRACT_REMOTE_AGENT_ID", "contract-clause-analyzer")
    auth_token = os.getenv("CONTRACT_REMOTE_AGENT_TOKEN")

    if auth_token:
        agent: RemoteAgent = _AuthenticatedRemoteAgent(
            base_url=base_url,
            agent_id=agent_id,
            protocol="a2a",
            auth_token=auth_token,
        )
    else:
        agent = RemoteAgent(base_url=base_url, agent_id=agent_id, protocol="a2a")

    # print(agent.run("Hello!"))

    try:
        # Touching .name fetches the remote agent card and confirms reachability.
        # For A2A a down server raises a connection error (not the agno-specific
        # RemoteServerUnavailableError), so guard broadly and degrade gracefully.
        _ = agent.name
    except Exception:
        print(
            f"[contract-team] Remote agent unreachable at {base_url} — "
            "running without it. Start it with: uv run contract-team-remote"
        )
        return None
    return agent




