import json, os, re, sqlite3
from typing import TypedDict, Dict, Any, Optional

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

from dataset import LOAN_APPLICATIONS
from rag_core import answer_query
from guardrails import input_guardrail, apply_rag_output_guardrail, FALLBACK
from schemas import AgentResponse

RAG_STRATEGY = "sentence"
RAG_THRESHOLD = 0.2480
ESCALATION_THRESHOLD = 0.65
DB_PATH = "checkpoints.sqlite"


NODE_COUNTS = {
    "classify": 0,
    "rag": 0,
    "lookup": 0,
    "final": 0
}


class AgentState(TypedDict, total=False):
    query: str
    thread_id: str
    intent: str
    record_id: Optional[str]
    lookup_result: dict
    rag_result: dict
    response: dict


def extract_record_id(text: str):
    match = re.search(r"\bREC\d{4}\b", text.upper())
    return match.group(0) if match else None


def check_loan_application_status(record_id: str) -> dict:
    record = next(
        (x for x in LOAN_APPLICATIONS if x["record_id"] == record_id),
        None
    )

    if not record:
        return {
            "found": False,
            "record_id": record_id
        }

    recency = 1 - min(record["days_since_created"], 30) / 30
    fraud = 1.0 if record["flagged_for_fraud_review"] else 0.0

    score = round(
        0.60 * fraud + 0.40 * recency,
        3
    )

    return {
        "found": True,
        "record_id": record["record_id"],
        "status": record["status"],
        "loan_amount_inr": record["loan_amount_inr"],
        "escalation_score": score,
        "needs_escalation": score >= ESCALATION_THRESHOLD
    }


def classify_node(state: AgentState):
    NODE_COUNTS["classify"] += 1

    query = state["query"].lower()

    terms = [
        "loan status",
        "application status",
        "check application",
        "track application",
        "record id",
        "record_id"
    ]

    state["intent"] = (
        "lookup"
        if any(term in query for term in terms)
        else "rag"
    )

    if state["intent"] == "lookup":
        state["record_id"] = extract_record_id(
            state["query"]
        )

    return state


def lookup_node(state: AgentState):
    NODE_COUNTS["lookup"] += 1

    record_id = state.get("record_id")

    if not record_id:
        state["lookup_result"] = {
            "found": False,
            "record_id": None
        }
    else:
        state["lookup_result"] = (
            check_loan_application_status(record_id)
        )

    return state


def rag_node(state: AgentState):
    NODE_COUNTS["rag"] += 1

    state["rag_result"] = answer_query(
        query=state["query"],
        strategy=RAG_STRATEGY,
        top_k=3,
        similarity_threshold=RAG_THRESHOLD
    )

    return state


def final_node(state: AgentState):
    NODE_COUNTS["final"] += 1

    if state["intent"] == "lookup":

        result = state["lookup_result"]

        if not result["found"]:
            answer = "Loan application record not found."

        else:
            answer = (
                f'Application {result["record_id"]} '
                f'is {result["status"]}. '
                f'Loan amount: INR '
                f'{result["loan_amount_inr"]:,}. '
                f'Escalation score: '
                f'{result["escalation_score"]:.3f}.'
            )

        source = "loan_status_tool"

    else:

        guarded = apply_rag_output_guardrail(
            state["rag_result"]
        )

        answer = (
            guarded.get("answer", FALLBACK)
            if isinstance(guarded, dict)
            else guarded
        )

        source = "knowledge_base"

    return {
        "response": {
            "answer": answer,
            "intent": state["intent"],
            "source": source,
            "thread_id": state["thread_id"]
        }
    }


def route_node(state: AgentState):
    return state["intent"]


def create_builder():
    builder = StateGraph(AgentState)

    builder.add_node(
        "classify",
        classify_node
    )

    builder.add_node(
        "lookup",
        lookup_node
    )

    builder.add_node(
        "rag",
        rag_node
    )

    builder.add_node(
        "final",
        final_node
    )

    builder.set_entry_point(
        "classify"
    )

    builder.add_conditional_edges(
        "classify",
        route_node,
        {
            "lookup": "lookup",
            "rag": "rag"
        }
    )

    builder.add_edge(
        "lookup",
        "final"
    )

    builder.add_edge(
        "rag",
        "final"
    )

    builder.add_edge(
        "final",
        END
    )

    return builder


db_connection = sqlite3.connect(
    DB_PATH,
    check_same_thread=False
)

checkpointer = SqliteSaver(
    db_connection
)

agent_graph = create_builder().compile(
    checkpointer=checkpointer
)


def run_agent(
    query: str,
    thread_id: str = "default"
):
    safe_query = input_guardrail(query)

    if isinstance(safe_query, dict):
        safe_query = safe_query.get(
            "query",
            safe_query.get("masked_text", query)
        )

    state = {
        "query": safe_query,
        "thread_id": thread_id
    }

    result = agent_graph.invoke(
        state,
        config={
            "configurable": {
                "thread_id": thread_id
            }
        }
    )

    return result["response"]


def build_interrupt_graph():
    return create_builder().compile(
        checkpointer=checkpointer,
        interrupt_after=[
            "rag",
            "lookup"
        ]
    )
