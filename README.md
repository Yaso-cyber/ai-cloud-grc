# ai-cloud-grc

> AI-driven Cloud GRC Toolkit — automated compliance scanning, risk scoring, AI-generated remediation, and a live dashboard.

[![CI](https://github.com/Yaso-cyber/ai-cloud-grc/actions/workflows/ci.yml/badge.svg)](https://github.com/Yaso-cyber/ai-cloud-grc/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## What This Is

A full-stack portfolio project that demonstrates:

- **Cloud scanning** — collects AWS inventory and config (S3, IAM, EC2, VPC)
- **Policy-as-code** — OPA/Rego rules mapped to NIST 800-53 / ISO 27001 / SOC 2 controls
- **AI assistant** — LLM-powered plain-English explanations, remediation playbooks, risk summaries
- **Automation** — GitHub Action runs the scanner, opens issues/PRs with evidence and fixes
- **Dashboard** — React + Tailwind UI with findings, risk score history, and PDF export

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        GitHub Actions CI                        │
│   (scheduled scan → scanner → policy engine → AI → issue/PR)   │
└─────────────────────┬───────────────────────────────────────────┘
                      │
          ┌───────────▼───────────┐
          │    Python Backend      │
          │  ┌─────────────────┐  │
          │  │  AWS Scanner    │  │  boto3 / mock data
          │  │  (S3,IAM,EC2)   │  │
          │  └────────┬────────┘  │
          │  ┌────────▼────────┐  │
          │  │ Policy Engine   │  │  OPA/Rego + local evaluator
          │  │ (control map)   │  │
          │  └────────┬────────┘  │
          │  ┌────────▼────────┐  │
          │  │  Risk Scorer    │  │  rule weights + ML anomaly
          │  └────────┬────────┘  │
          │  ┌────────▼────────┐  │
          │  │  AI Assistant   │  │  OpenAI / local LLM
          │  │ /explain        │  │
          │  │ /remediate      │  │
          │  └────────┬────────┘  │
          │  ┌────────▼────────┐  │
          │  │  FastAPI REST   │  │
          │  └────────┬────────┘  │
          └───────────┼───────────┘
                      │
          ┌───────────▼───────────┐
          │   React Dashboard     │
          │  (findings, scores,   │
          │   PDF export, history)│
          └───────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Cloud scanner | Python 3.11 + boto3 |
| Policy engine | OPA/Rego (dockerized) + local Python evaluator |
| AI assistant | OpenAI API (gpt-4o) or local LLM |
| API | FastAPI + Uvicorn |
| Frontend | React 18 + Tailwind CSS + Recharts |
| PDF export | jsPDF / WeasyPrint |
| Data store | SQLite (demo) / Postgres (prod) |
| CI/CD | GitHub Actions |
| Deploy | Render (backend) + Vercel (frontend) |
| Tests | pytest + Jest |
| IaC (optional) | Terraform |

---

## Project Structure

```
ai-cloud-grc/
├── backend/
│   ├── scanner/          # AWS resource collectors
│   ├── policy_engine/    # OPA evaluator + control mappings
│   ├── risk_scorer/      # Scoring logic + anomaly detection
│   ├── ai_assistant/     # LLM integration (/explain, /remediate)
│   ├── api/              # FastAPI app
│   └── tests/
├── frontend/             # React dashboard
│   └── src/
│       └── components/
├── policies/             # OPA .rego policy files
├── .github/workflows/    # CI + scheduled scanner
├── demo-data/            # Sample findings JSON
└── docs/                 # Architecture notes
```

---

## MVP Implementation Plan

| Phase | Days | Deliverable |
|---|---|---|
| Repo skeleton + README | Day 0 | This file, folder structure |
| AWS scanner (S3 + IAM) | Day 1–2 | `findings.json` output |
| Policy checks + risk scoring | Day 3–4 | Control mapping + score |
| AI assistant endpoints | Day 5–6 | `/explain` and `/remediate` |
| GitHub Action automation | Day 7–9 | Auto-issues + remediation PRs |
| React dashboard + PDF | Day 10–13 | Live UI + exportable report |
| Polish + demo + blog post | Day 14+ | Deployed demo, walkthrough |

---

## Quickstart

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # add your OPENAI_API_KEY and AWS credentials
uvicorn api.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Run scanner locally

```bash
cd backend
python -m scanner.aws_scanner --profile default --output ../demo-data/findings.json
```

---

## Environment Variables

| Variable | Description |
|---|---|
| `OPENAI_API_KEY` | OpenAI API key for AI assistant |
| `AWS_ACCESS_KEY_ID` | AWS credentials (or use mock mode) |
| `AWS_SECRET_ACCESS_KEY` | AWS credentials |
| `AWS_DEFAULT_REGION` | e.g. `us-east-1` |
| `MOCK_MODE` | Set `true` to use demo data instead of live AWS |

---

## Compliance Frameworks

Findings are mapped to controls in:

- **NIST SP 800-53 Rev 5**
- **ISO/IEC 27001:2022**
- **SOC 2 Type II** (CC series)

---

## License

MIT
