# agno-team

A minimal, runnable example of an **[Agno](https://docs.agno.com) multi-agent team** built with **Python + [uv](https://docs.astral.sh/uv/)**.

A *team leader* (Gemini) reads your question, delegates to specialist member
agents, and synthesizes their work into one answer. One member — the **Risk
Assessor** — is a `RemoteAgent` running in a separate AgentOS process.

```
                ┌─────────────────────────┐
   question ──► │   Market Research Team   │  (leader: Gemini, coordinates)
                └───────────┬─────────────┘
                            │ delegates
        ┌───────────────────┼────────────────────┐
        ▼                   ▼                     ▼
 ┌──────────────┐  ┌──────────────────┐  ┌─────────────────────┐
 │ Web Researcher│  │ Finance Analyst  │  │ Risk Assessor       │
 │ DuckDuckGo   │  │ yfinance         │  │ RemoteAgent ──HTTP──┼─► AgentOS
 └──────────────┘  └──────────────────┘  └─────────────────────┘   :7777
       local              local                  remote
```

The Risk Assessor joins the team only when its AgentOS server is reachable;
otherwise the team runs with the two local members and prints a hint.

## Project layout

```
src/agno_team/
├── models.py         # central model config (Gemini, env-overridable) — shared
├── agents.py         # market team members: web research, finance, + remote risk proxy
├── team.py           # assembles the market-research team leader
├── remote_server.py  # AgentOS serving the Risk Assessor (RemoteAgent target, :7777)
├── __init__.py       # market team main() CLI entrypoint
└── contract/         # second team — contract review (reuses models.py)
    ├── agents.py        # members: clause extractor, legal researcher, + remote analyzer proxy
    ├── team.py          # assembles the contract-review team leader
    ├── remote_server.py # AgentOS serving the Contract Analyzer (RemoteAgent target, :7778)
    ├── pdf_ocr.py       # Gemini OCR fallback for scanned/image-only PDFs
    └── __init__.py      # contract team main() CLI entrypoint (PDF/txt/question input)
```

## Setup

1. Install dependencies (creates `.venv` automatically):

   ```bash
   uv sync
   ```

2. Add your Gemini API key (free key: https://aistudio.google.com/apikey):

   ```bash
   cp .env.example .env
   # then edit .env and set GOOGLE_API_KEY
   ```

## Run

**Terminal 1** — start the remote Risk Assessor (AgentOS on :7777):

```bash
uv run agno-team-remote
```

**Terminal 2** — run the team (it auto-discovers the remote agent):

```bash
uv run agno-team                                                  # default NVDA demo
uv run agno-team "Compare Apple and Microsoft: latest price and recent news"
```

> Skipping Terminal 1 is fine — the team runs with its two local members and
> prints a note that the remote agent was unavailable.

### Contract Review Team

A second team with the same shape: a leader coordinates a **Clause Extractor**
and **Legal Researcher** locally, plus a **Contract Analyzer** running as a
`RemoteAgent` on its own AgentOS (`:7778`, so it can run alongside the Risk
Service on `:7777`).

**Terminal 1** — start the remote Contract Analyzer:

```bash
uv run contract-team-remote
```

**Terminal 2** — run the team. Pass a contract file (**PDF or `.txt`**), a
question, or nothing (uses a built-in sample clause):

```bash
uv run contract-team                       # default sample contract
uv run contract-team ./my-contract.pdf     # review a PDF contract
uv run contract-team ./my-contract.txt     # review a text contract
uv run contract-team "Is a 90-day auto-renewal notice window unusual?"
```

> PDF text is extracted with `pypdf`. Scanned/image-only PDFs (no text layer)
> automatically fall back to **Gemini OCR** — the raw PDF is sent to Gemini,
> which transcribes it. Reuses your `GOOGLE_API_KEY`; no extra binaries needed.
> Override the OCR model with `GEMINI_OCR_MODEL`.

> Same graceful-degrade behavior: skip Terminal 1 and the team runs with its
> two local members.

## How it works

- **`models.py`** — one `build_model()` so every agent and the leader share the
  same provider; swap models in a single place via the `GEMINI_MODEL` env var.
- **`agents.py`** — each member has a narrow `role` + its own tools
  (`DuckDuckGoTools` for the web, `YFinanceTools` for market data).
- **`team.py`** — the `Team` is the leader: its `instructions` tell it how to
  route requests to members and combine results.
- **`remote_server.py`** — a `RemoteAgent` is a proxy to an agent hosted on
  another AgentOS instance. This module serves the Risk Assessor under id
  `risk-assessor`; `agents.py` connects to it via
  `RemoteAgent(base_url, agent_id="risk-assessor")`. Same interface as a local
  member, but it executes in a separate process (and could run on another host).

Built on Agno `2.6.x`.
