"""Central model configuration for the Agno team.

Keeping model construction in one place makes it trivial to swap the provider
or model id for every agent + the team leader at once.
"""

from __future__ import annotations

import os

from agno.models.google import Gemini

# Default to a fast, low-cost Gemini model. Override with GEMINI_MODEL in .env.
DEFAULT_MODEL_ID = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def build_model(model_id: str | None = None) -> Gemini:
    """Return a configured Gemini model.

    The Gemini client reads GOOGLE_API_KEY from the environment automatically,
    so callers only need to ensure the key is loaded (see load_dotenv in main).
    """
    return Gemini(id=model_id or DEFAULT_MODEL_ID)
