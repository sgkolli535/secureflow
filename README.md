# SecureFlow                                                                                                                                                                                                         
                                                                                                                                                                                                                    
Automated security remediation pipeline that connects GitHub CodeQL to [Devin](https://devin.ai), turning security findings into merged PRs without pulling engineers off sprint work.

Built for the **MedSecure** scenario: *"CodeQL flags dozens of new issues every week and they just pile up. Our security team files them, our engineers ignore them because they're not sprint work."*

## Demo Recording
Access the full demo and walkthrough [here](https://www.loom.com/share/6749153a25cb4359b3ba68c71e9d1f3c)

## How It Works

```
CodeQL Scan → Smart Triage → Devin Fixes → Team Reviews → Audit Trail
```

1. **Fetch** — Pulls open CodeQL alerts from GitHub (manual trigger or webhook)
2. **Triage** — Classifies each finding by CWE type and severity into three tiers:
  - **Auto-fix** — Standard vulnerabilities (SQLi, XSS, path traversal) → Devin handles end-to-end
  - **Assist** — Devin writes the fix, human reviews before merge
  - **Escalate** — Complex issues (auth, race conditions) → routed to security team
3. **Dispatch** — Creates Devin sessions with CWE-specific remediation guidance, batching related findings per file
4. **Monitor** — Background poller tracks Devin sessions, detects completed PRs, computes confidence scores
5. **Notify** — Slack notifications to security team (escalations, digest) and engineering (PR ready for review)
6. **Feedback loop** — Engineers can reject a fix from the dashboard; Devin retries with their feedback

## Architecture

```
secureflow/          Python package — triage, orchestration, Devin/GitHub clients
api/                 FastAPI backend — REST endpoints, webhook handler, background poller
dashboard/           React + TypeScript frontend — real-time monitoring dashboard
scripts/             Pipeline runner and demo seed data
tests/               Unit tests for triage logic and webhook verification
slides/              Presentation slides (HTML)
```

## Sample App
[Sample App](https://github.com/sgkolli535/secureflow-demo-app) created to show the performance of Secureflow and Devin on a codebase similar to that of the customer.
 
## Dashboard

- **Overview** - Stats bar, severity donut chart, findings table with confidence scores, pipeline Kanban view
- **Compliance** — MTTR, auto-fix rate, finding age distribution, CWE fix rate chart, remediation timeline, audit trail
- **Notifications** — Real-time feed with Slack-style formatting
- **Feedback loop** — Reject PRs directly from the dashboard, Devin retries with context

## Key Features

- **Intelligent triage** — Not everything gets auto-fixed; complex CWEs are escalated
- **Batching** — Multiple findings in the same file → one Devin session, one PR
- **Confidence scoring** — Heuristic score based on session outcome, PR creation, and insights
- **GitHub webhook** — `POST /api/webhooks/github` triggers pipeline on CodeQL scan completion
- **Slack integration** — Real webhook delivery or mock mode for development
- **Compliance reporting** — MTTR, auto-fix rates, age distribution, full audit trail
- **Reject & re-dispatch** — Engineers provide feedback, Devin iterates

## Devin API Integration

Uses the Devin API for:
- **Sessions** — Create, poll, and send messages
- **Playbooks** — Reusable remediation templates
- **Knowledge** — Push CWE guidance as organizational context
- **Session insights** — Post-completion analysis for confidence scoring
- **Secrets** — Secure credential management

## Setup

```bash
# Backend
cp .env.example .env  # Fill in GitHub token, Devin API key
pip install -e .
uvicorn api.main:app --reload

# Frontend
cd dashboard
npm install
npm run dev
```

## Configuration

| Variable | Description |
|---|---|
| `GITHUB_TOKEN` | GitHub PAT with repo + security_events scopes |
| `GITHUB_OWNER` | GitHub username or org |
| `GITHUB_REPO` | Target repository name |
| `DEVIN_API_KEY` | Devin API key |
| `SLACK_WEBHOOK_URL` | Slack incoming webhook URL |
| `SLACK_ENABLED` | `true` to send real Slack messages |
| `MAX_CONCURRENT_SESSIONS` | Max parallel Devin sessions (default: 3) |

## Tech Stack

**Backend:** Python, FastAPI, SQLAlchemy, SQLite, httpx

**Frontend:** React, TypeScript, Tailwind CSS, Recharts, Vite
