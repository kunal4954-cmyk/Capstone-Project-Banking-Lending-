# Cred Banking & FinTech Support Agent

A Banking & FinTech support agent built with **LangGraph + RAG** for banking queries and loan application status lookup.

**Track:** Banking & FinTech (Cred)  
**Mode:** `MOCK_LLM` — Offline, deterministic, no API key  
**Random Seed:** `42`

## Key Features

- RAG-based banking question answering
- Loan application status lookup
- LangGraph conditional routing
- PII masking and prompt-injection protection
- Grounded response validation
- FastAPI endpoints
- FastMCP integration
- SQLite checkpointing
- JSONL request logging
- Retry and timeout handling

## Dataset

The project uses `Banking.csv` to create **1,000 loan application records**.

| Property | Value |
|---|---:|
| Records | 1,000 |
| Unique IDs | 1,000 |
| Loan Range | ₹200,561 – ₹4,999,992 |
| Fraud Review | 144 (14.4%) |

**Loan Categories:** Business, Home, Education, Personal, Auto

**Application Status:** Submitted, Under Review, Approved, Rejected, Disbursed

## Knowledge Base & RAG

The knowledge base contains **20 documents** covering important Banking and FinTech topics including:

KYC, EMI, loan eligibility, credit score, fraud, prepayment, NPA/default, collateral, guarantor, bank lending, NBFC lending, and P2P lending.

Three chunking methods were evaluated:

| Chunking | Threshold | P@3 | R@3 |
|---|---:|---:|---:|
| Fixed | 0.2390 | 0.3333 | 1.0000 |
| **Sentence** | **0.2480** | **0.3333** | **1.0000** |
| Semantic | 0.2651 | 0.3333 | 1.0000 |

**Final Strategy:** Sentence-based chunking  
**Embedding:** `all-MiniLM-L6-v2`  
**Vector DB:** ChromaDB

Queries below the threshold return:

```text
I don't know based on the available knowledge base.
```

## Agent Workflow

```text
                  ┌── RAG ─────┐
Query → Classify ─┤             ├→ Final Response
                  └── Lookup ──┘
```

The lookup tool returns loan status, amount, escalation score, and escalation requirement.

**Escalation Threshold:** `0.65`  
**Escalated Applications:** 128/1000 (12.8%)

## Guardrails

- PAN masking
- Aadhaar masking
- Bank account masking
- Prompt-injection detection
- RAG groundedness check
- PII-safe logging

## API & MCP

FastAPI endpoints:

```text
POST /ask
POST /add-document
```

FastMCP exposes the loan-status lookup tool through `/mcp`.

## Evaluation

RAG evaluation was performed on **15 queries**.

| Metric | Score |
|---|---:|
| Context Relevance | 1.0000 |
| Groundedness | 1.0000 |
| Answer Relevance | 1.0000 |

## Run

```bash
pip install -r requirements.txt
python dataset.py
python kb_dataset.py
python test_eval.py
```

Start API:

```bash
uvicorn app:app --host 127.0.0.1 --port 8000
```

Start MCP:

```bash
python mcp_server.py
python mcp_client.py
```

## Tech Stack

`Python` • `LangGraph` • `SentenceTransformers` • `ChromaDB` • `FastAPI` • `FastMCP` • `Pydantic` • `SQLite`
