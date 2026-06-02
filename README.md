# AI DevOps Platform 🤖

> 5 AI-powered tools that plug into a real DevOps pipeline using Claude API.
> Built by [Amith Busireddy](https://linkedin.com/in/busireddy-amith-761311181) —
> Cloud DevOps Engineer at Wells Fargo, Fidelity, AT&T, Comcast.

---

## What This Does

Most DevOps engineers spend hours on repetitive tasks —
reviewing PRs, writing runbooks, debugging pipeline failures.
This project automates all of that using AI.

| Tool | What it does |
|------|-------------|
| AI PR Reviewer | Reviews Terraform PRs and flags security issues automatically |
| AI Terraform Generator | Type plain English and get production-ready Terraform code |
| AI Failure Detective | Pipeline fails, AI reads logs and tells you exactly what went wrong |
| AI Runbook Generator | Paste incident notes and get a formatted runbook saved to GitHub |
| Infra Chatbot | Ask your infrastructure questions in plain English |

---

## Demo

**AI PR Reviewer — catches security issues automatically:**

```
$ python scripts/pr_reviewer.py terraform-samples/bad_example.tf

## AI Terraform Code Review

### Critical Issues
- NSG rule allows ALL inbound traffic from 0.0.0.0/0
- Storage account has public blob access enabled
- Key Vault missing purge_protection_enabled = true
- Key Vault has no network restrictions

### Recommendations
- Add tags: environment, owner, project, managed-by
- Restrict NSG rules to specific IPs
```

**AI Terraform Generator — plain English to code:**

```
$ python scripts/tf_generator.py "Create an AKS cluster with a VNet"

# Generates complete main.tf, variables.tf, outputs.tf
# With tags, security best practices, autoscaler configured
```

**AI Failure Detective — explains pipeline failures:**

```
$ python scripts/failure_detective.py

### Root Cause
Terraform state lock conflict — previous pipeline run
cancelled mid-apply, leaving a lock in state backend.

### How to Fix
1. Run: terraform force-unlock <LOCK_ID>
2. Verify no other pipeline is running
3. Re-run the pipeline
```

**AI Runbook Generator — incident notes to runbook:**

```
$ python scripts/runbook_generator.py

# Generates formatted runbook saved to runbooks/ folder
# Includes: Summary, Impact, Timeline, Root Cause,
# Resolution Steps, Prevention, Lessons Learned
```

**Infra Chatbot — ask your infrastructure anything:**

```
$ python scripts/infra_chatbot.py "what resources are running"

Currently only NetworkWatcher is running in your Azure
subscription. Run terraform apply to deploy resources.
```

---

## How It Works

```
Developer opens PR / Pipeline fails / Incident occurs
                    |
         GitHub Actions triggers
                    |
         Python script runs
                    |
    Script sends context to Claude API
                    |
       Claude analyzes and responds
                    |
  Result posted as PR comment / saved to repo
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| AI Engine | Claude API (Anthropic) |
| Pipeline | GitHub Actions |
| Language | Python 3.x |
| IaC | Terraform (Azure) |
| Cloud | Microsoft Azure |
| Auth | Azure CLI + Managed Identity |

---

## Project Structure

```
ai-devops-platform/
├── .github/workflows/       # CI/CD pipeline
├── scripts/
│   ├── pr_reviewer.py       # Feature 1 — AI PR Reviewer
│   ├── tf_generator.py      # Feature 2 — AI Terraform Generator
│   ├── failure_detective.py # Feature 3 — AI Failure Detective
│   ├── runbook_generator.py # Feature 4 — AI Runbook Generator
│   └── infra_chatbot.py     # Feature 5 — Infra Chatbot
├── runbooks/                # Auto-generated runbooks saved here
├── terraform-samples/       # Sample Terraform files for testing
├── requirements.txt         # Python dependencies
└── README.md
```

---

## Quick Start

**1. Clone the repo:**

```bash
git clone https://github.com/amithvr46/ai-devops-platform.git
cd ai-devops-platform
```

**2. Install dependencies:**

```bash
pip install -r requirements.txt
```

**3. Set your API key:**

```bash
# Windows PowerShell
$env:ANTHROPIC_API_KEY="your-key-here"

# Mac/Linux
export ANTHROPIC_API_KEY="your-key-here"
```

**4. Run any feature:**

```bash
# AI PR Reviewer
python scripts/pr_reviewer.py terraform-samples/bad_example.tf

# AI Terraform Generator
python scripts/tf_generator.py "Create a storage account with private access"

# AI Failure Detective
python scripts/failure_detective.py

# AI Runbook Generator
python scripts/runbook_generator.py

# Infra Chatbot
python scripts/infra_chatbot.py "what resources are running"
```

---

## Real World Context

This project was built to demonstrate AI integration in DevOps
pipelines — a skill increasingly required at enterprise companies.

The patterns here mirror real automation opportunities identified
working at Wells Fargo and Fidelity Investments:

- PR reviews were manual and inconsistent — AI makes them instant
- Runbook writing took hours after incidents — AI does it in seconds
- Pipeline debugging required senior engineers — AI handles first-line triage

---

## Related Project

See also: [azure-infrastructure-terraform](https://github.com/amithvr46/azure-infrastructure-terraform)
— the Azure Landing Zone this platform is designed to work with.

---

## Author

**Amith Busireddy** — Cloud DevOps Engineer
- Email: Amithvr46@gmail.com
- LinkedIn: https://linkedin.com/in/busireddy-amith-761311181
- GitHub: https://github.com/amithvr46

