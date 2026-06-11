"""Member agents for the contract-review team.

Each agent masters one narrow domain. The team leader (see team.py) decides
which member(s) to delegate to based on the user's request. The deep
Contract Analyzer is a RemoteAgent running in a separate AgentOS process.
"""

from __future__ import annotations
import os
from agno.agent.remote import RemoteAgent


class _AuthenticatedRemoteAgent(RemoteAgent):
    """A RemoteAgent that attaches a bearer token and drops the session id.

    Two adaptations are needed for the Team to talk to the remote A2A server:

    1. Auth: the base RemoteAgent only accepts ``auth_token`` as a per-call
       argument on ``run``/``arun`` — it is NOT a constructor parameter. The
       Team invokes members via ``arun()`` without forwarding any token, so an
       authenticated A2A server would reject every delegated call. We store the
       token and inject it into each call.

    2. Stateless calls: the Team passes ``session_id`` to each member, which
       RemoteAgent maps to the A2A ``contextId``. The remote analyzer returns an
       EMPTY task whenever a ``contextId`` is present (server-side quirk —
       reproduced even with a brand-new id), which makes the leader receive an
       empty result and reply "I'll get back to you" instead of the analysis.
       We drop ``session_id`` so every delegation is a clean, stateless A2A call
       and the agent's response actually comes back.
    """

    def __init__(self, *args, auth_token: str, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._auth_token = auth_token

    def _prepare(self, kwargs: dict) -> None:
        kwargs.setdefault("auth_token", self._auth_token)
        kwargs.pop("session_id", None)  # maps to A2A contextId → empties response

    def run(self, *args, **kwargs):  # type: ignore[override]
        self._prepare(kwargs)
        return super().run(*args, **kwargs)

    def arun(self, *args, **kwargs):  # type: ignore[override]
        self._prepare(kwargs)
        return super().arun(*args, **kwargs)

def contract_analyzer_remote() -> RemoteAgent | None:
    """Proxy to the Contract Analyzer served over the A2A protocol.

    Returns None if that server is unreachable, so the team still runs with its
    local members. Configure via env:
      CONTRACT_REMOTE_AGENT_URL  — A2A base url for the agent
      CONTRACT_REMOTE_AGENT_ID   — remote agent id
      CONTRACT_REMOTE_AGENT_TOKEN — bearer token (e.g. aak_...)
    """
    base_url = os.getenv("CONTRACT_REMOTE_AGENT_URL")
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

    try:
        # Touching .name fetches the remote agent card and confirms reachability.
        # For A2A a down server raises a connection error (not the agno-specific
        # RemoteServerUnavailableError), so guard broadly and degrade gracefully.
        _ = agent.name
    except Exception:
        print(
            f"[contract-team] Remote agent unreachable at {base_url} — "
            "running without it."
        )
        return None
    return agent




