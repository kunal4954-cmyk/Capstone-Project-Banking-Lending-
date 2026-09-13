# Cred Banking & FinTech Domain Support Agent

**Track:** Banking & FinTech (Cred)  
**Mode:** MOCK_LLM — Deterministic, Offline, Zero API Key  
**Frameworks:** LangGraph, ChromaDB, FastAPI, MCP

## Dataset

- Random seed: `42`
- Total records: `1000`
- Personal Loan: `205`
- Home Loan: `199`
- Auto Loan: `197`
- Business Loan: `186`
- Education Loan: `213`
- Fraud review rate: `19.60%`
- Loan amount range: `INR 200,000 – INR 4,999,000`

## Knowledge Base

12 policy documents covering:

- Loan eligibility
- EMI calculation
- Credit card fees
- KYC requirements
- Fraud dispute resolution
- Account closure
- Interest rates
- Prepayment penalties
- Minimum balance
- Credit score factors
- Joint accounts
- NRI eligibility

## RAG Chunking Evaluation

| Strategy | Precision@3 | Recall@3 |
|---|---:|---:|
| Fixed-size + overlap | 0.3333 | 1.0000 |
| Sentence-based | 0.3333 | 1.0000 |

Both required strategies achieved identical results.  
**Selected collection:** `fixed_chunks`

Semantic chunking is included as an additional experiment.

## Similarity Threshold

- Minimum in-scope similarity: `0.6735`
- Maximum out-of-scope similarity: `0.2403`
- Empirically selected threshold: `0.4569`

## Agent Capabilities

- Policy RAG queries
- Loan application status lookup
- Grounded response generation
- Source attribution
- Escalation scoring
- PII masking
- Prompt-injection detection
- Out-of-scope abstention
- Conversation checkpointing

## API

FastAPI supports:

- Health check
- Policy queries
- Application lookup
- Dynamic document ingestion

## MCP

Tool:

```text
lookup_loan_status
```

Endpoint:

```text
http://127.0.0.1:8001/mcp
```

MCP round-trip verified for two loan application IDs.

## Evaluation

12 policy queries:

| Metric | Score |
|---|---:|
| Context Relevance | 1.0000 |
| Groundedness | 1.0000 |
| Answer Relevance | 1.0000 |

Functional and safety checks: **3/3 PASS**

## Resilience

- SQLite checkpoint/resume: PASS
- Exponential backoff: PASS
- Per-node timeout: PASS
- Global timeout: PASS

## Run

```bash
pip install -r requirement.txt
python dataset.py
python rag_core.py
python test_eval.py
python test_resilience.py
```

FastAPI:

```bash
uvicorn app:app --reload
```
