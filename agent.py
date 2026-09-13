import json
import os
import re
import sqlite3
from typing import Any, Dict, List, Optional, TypedDict

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, StateGraph

from guardrails import (
    detect_prompt_injection,
    mask_pii,
    verify_groundedness,
)
from rag_core import retrieve_with_scores
from schemas import AgentStructuredResponse


DATASET_PATH = "data/loan_applications.json"

RAG_COLLECTION = "fixed_chunks"
SIMILARITY_THRESHOLD = 0.4569

ESCALATION_THRESHOLD = 0.55

def check_loan_application_status(
    record_id: str
) -> Dict[str, Any]:

    if not os.path.exists(DATASET_PATH):
        return {"error": "Dataset not found."}

    with open(DATASET_PATH, "r", encoding="utf-8") as file:
        dataset = json.load(file)

    record = next(
        (
            row
            for row in dataset
            if row["record_id"].upper() == record_id.upper()
        ),
        None,
    )

    if record is None:
        return {
            "error": f"Application ID '{record_id}' not found."
        }

    fraud_score = (
        0.60
        if record["flagged_for_fraud_review"]
        else 0.0
    )

    recency_score = (
        0.40
        * min(
            record["days_since_created"] / 30.0,
            1.0,
        )
    )

    escalation_score = round(
        fraud_score + recency_score,
        3,
    )

    return {
        "record_id": record["record_id"],
        "category": record["category"],
        "status": record["status"],
        "loan_amount_inr": record["loan_amount_inr"],
        "days_since_created": record["days_since_created"],
        "flagged_for_fraud_review":
            record["flagged_for_fraud_review"],
        "escalation_score": escalation_score,
        "escalation_recommended":
            escalation_score >= ESCALATION_THRESHOLD,
    }

class AgentState(TypedDict, total=False):
    query: str
    masked_query: str
    intent: str
    context: List[Dict]
    tool_result: Dict
    response: Dict
    conversation_history: List[str]
    guardrail_triggered: bool
    error_message: Optional[str]

def input_guardrail_node(
    state: AgentState
) -> AgentState:

    raw_query = state["query"]

    if detect_prompt_injection(raw_query):

        state["guardrail_triggered"] = True

        state["response"] = AgentStructuredResponse(
            query=mask_pii(raw_query),
            intent="SECURITY_VIOLATION",
            answer=(
                "Request blocked because a prompt "
                "injection pattern was detected."
            ),
            sources=[],
            escalation_recommended=False,
            escalation_score=0.0,
            grounded=False,
        ).model_dump()

        return state

    masked_query = mask_pii(raw_query)

    state["masked_query"] = masked_query
    state["guardrail_triggered"] = False

    if (
        re.search(
            r"CRD-LN-\d+",
            masked_query,
            re.IGNORECASE,
        )
        or "application status" in masked_query.lower()
    ):
        state["intent"] = "APPLICATION_LOOKUP"

    else:
        state["intent"] = "POLICY_QUERY"

    return state

def rag_retrieval_node(
    state: AgentState
) -> AgentState:

    retrieved = retrieve_with_scores(
        RAG_COLLECTION,
        state["masked_query"],
        top_k=3,
    )

    state["context"] = [
        item
        for item in retrieved
        if item["similarity"] >= SIMILARITY_THRESHOLD
    ]

    return state

def application_lookup_node(
    state: AgentState
) -> AgentState:

    match = re.search(
        r"CRD-LN-\d+",
        state["masked_query"],
        re.IGNORECASE,
    )

    if match:
        record_id = match.group(0).upper()

        state["tool_result"] = (
            check_loan_application_status(record_id)
        )

    else:
        state["tool_result"] = {
            "error": (
                "No valid application ID provided. "
                "Expected format: CRD-LN-XXXX."
            )
        }

    return state

def answer_synthesis_node(
    state: AgentState
) -> AgentState:

    query = state["masked_query"]
    intent = state["intent"]

    if intent == "APPLICATION_LOOKUP":

        result = state.get("tool_result", {})

        if "error" in result:

            response = AgentStructuredResponse(
                query=query,
                intent=intent,
                answer=(
                    "Unable to retrieve application status: "
                    + result["error"]
                ),
                sources=[],
                escalation_recommended=False,
                escalation_score=0.0,
                grounded=False,
            )

        else:

            answer = (
                f"Application {result['record_id']} "
                f"({result['category']}) is currently "
                f"'{result['status']}'. "
                f"Loan Amount: INR "
                f"{result['loan_amount_inr']:,}. "
                f"Days since creation: "
                f"{result['days_since_created']}. "
                f"Fraud Review Flag: "
                f"{result['flagged_for_fraud_review']}."
            )

            response = AgentStructuredResponse(
                query=query,
                intent=intent,
                answer=answer,
                sources=[result["record_id"]],
                escalation_recommended=(
                    result["escalation_recommended"]
                ),
                escalation_score=(
                    result["escalation_score"]
                ),
                grounded=True,
            )

    else:

        chunks = state.get("context", [])

        if not chunks:

            response = AgentStructuredResponse(
                query=query,
                intent=intent,
                answer=(
                    "I am sorry, but I do not have enough "
                    "policy information in my knowledge base "
                    "to answer that specific question."
                ),
                sources=[],
                escalation_recommended=False,
                escalation_score=0.0,
                grounded=False,
            )

        else:

            context = " ".join(
                chunk["content"]
                for chunk in chunks
            )

            sources = list(
                dict.fromkeys(
                    chunk["doc_id"]
                    for chunk in chunks
                )
            )

            answer = (
                f"Based on Cred Policy documents "
                f"({', '.join(sources)}): {context}"
            )

            response = AgentStructuredResponse(
                query=query,
                intent=intent,
                answer=answer,
                sources=sources,
                escalation_recommended=False,
                escalation_score=0.0,
                grounded=verify_groundedness(
                    context,
                    answer,
                ),
            )

    state["response"] = response.model_dump()

    history = state.get(
        "conversation_history",
        [],
    )

    history.extend([
        f"User: {query}",
        f"Agent: {response.answer}",
    ])

    state["conversation_history"] = history

    return state

def route_intent(
    state: AgentState
) -> str:

    if state.get("guardrail_triggered"):
        return "end"

    if state["intent"] == "APPLICATION_LOOKUP":
        return "application"

    return "rag"

builder = StateGraph(AgentState)

builder.add_node(
    "input_guardrail",
    input_guardrail_node,
)

builder.add_node(
    "rag",
    rag_retrieval_node,
)

builder.add_node(
    "application",
    application_lookup_node,
)

builder.add_node(
    "answer",
    answer_synthesis_node,
)

builder.set_entry_point(
    "input_guardrail"
)

builder.add_conditional_edges(
    "input_guardrail",
    route_intent,
    {
        "rag": "rag",
        "application": "application",
        "end": END,
    },
)

builder.add_edge(
    "rag",
    "answer",
)

builder.add_edge(
    "application",
    "answer",
)

builder.add_edge(
    "answer",
    END,
)

os.makedirs(
    "data",
    exist_ok=True,
)

connection = sqlite3.connect(
    "data/checkpoints.sqlite",
    check_same_thread=False,
)

checkpointer = SqliteSaver(
    connection
)

agent_graph = builder.compile(
    checkpointer=checkpointer
)
