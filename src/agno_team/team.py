"""Assemble the contract-review team.

The Team object is itself the "team leader": it reads the incoming contract or
question, delegates to the right member agent(s), then synthesizes their
outputs into a single decision-ready review.
"""

from __future__ import annotations

from agno.team import Team

from .models import build_model
from .agents import (
    contract_analyzer_remote,
)


def build_team() -> Team:
    """Build the coordinating contract-review team.

    The Contract Analyzer is a RemoteAgent: it joins the team only when its
    AgentOS server is reachable, otherwise the team runs with its two local
    members.
    """
    members = []
    remote_analyzer = contract_analyzer_remote()
    if remote_analyzer is not None:
        members.append(remote_analyzer)

    return Team(
        name="Contract Review Team",
        model=build_model(),
        members=members,
        instructions=[
            "You coordinate a team that reviews contracts for risk.",
            "First delegate to the Clause Extractor to structure the contract text.",
            "Delegate questions about legal norms or regulations to the Legal Researcher.",
            "If a Contract Analyzer is available, delegate to it for the deep "
            "risk verdict (red flags, missing protections, suggested fixes).",
            "For a full review, use multiple members and combine their findings.",
            "Finish with a short, decision-ready summary and an overall risk rating. "
            "Keep clause quotes and sources intact.",
        ],
        markdown=True,
        show_members_responses=True,
    )
