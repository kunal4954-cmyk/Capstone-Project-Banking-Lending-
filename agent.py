# agent.py
import json, os, re, sqlite3
from typing import TypedDict, Dict, Any
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver

from dataset import LOAN_APPLICATIONS
from rag_core import answer_query
from guardrails import input_guardrail, apply_rag_output_guardrail
from schemas import AgentResponse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "checkpoints.sqlite")
HISTORY_FILE = os.path.join(BASE_DIR, "conversation_history.json")

RAG_STRATEGY = "sentence"       # replace after evaluation
RAG_THRESHOLD = None           # replace with calibrated value
ESCALATION_THRESHOLD = 0.65

APPLICATION_INDEX = {str(x["record_id"]): x for x in LOAN_APPLICATIONS}


class AgentState(TypedDict, total=False):
    query: str
    thread_id: str
    intent: str
    record_id: str
    tool_result: Dict[str, Any]
    rag_result: Dict[str, Any]
    response: Dict[str, Any]


def check_loan_application_status(record_id: str) -> dict:
    """Return application status, loan amount and escalation score."""
    record = APPLICATION_INDEX.get(str(record_id))
    if not record:
        return {"found": False, "record_id": record_id, "message": "Loan application not found."}

    days = max(0, min(int(record["days_since_created"]), 30))
    fraud = 1.0 if record["flagged_for_fraud_review"] else 0.0
    recency = 1.0 - (days / 30)
    score = round((0.60 * fraud) + (0.40 * recency), 3)

    return {
        "found": True,
        "record_id": str(record["record_id"]),
        "status": record["status"],
        "loan_amount_inr": record["loan_amount_inr"],
        "escalation_score": score,
        "needs_escalation": score >= ESCALATION_THRESHOLD
    }


def extract_record_id(query: str) -> str:
    match = re.search(r"\bREC\d+\b", query.upper())
    return match.group(0) if match else ""


def classify_node(state: AgentState):
    query = state["query"].lower()
    terms = ["loan status", "application status", "check application",
             "track application", "record id", "record_id"]
    state["intent"] = "lookup" if any(x in query for x in terms) else "rag"
    if state["intent"] == "lookup":
        state["record_id"] = extract_record_id(state["query"])
    return state


def route_intent(state: AgentState):
    return state["intent"]


def lookup_node(state: AgentState):
    record_id = state.get("record_id", "")
    state["tool_result"] = (
        check_loan_application_status(record_id)
        if record_id
        else {"found": False, "message": "Please provide a valid record ID such as REC0001."}
    )
    return state


def rag_node(state: AgentState):
    state["rag_result"] = answer_query(
        query=state["query"],
        strategy=RAG_STRATEGY,
        top_k=3,
        similarity_threshold=RAG_THRESHOLD
    )
    return state


def final_node(state: AgentState):
    if state["intent"] == "lookup":
        result = state["tool_result"]
        if result.get("found"):
            answer = (
                f"Application {result['record_id']} is {result['status']}. "
                f"Loan amount: INR {result['loan_amount_inr']:,}. "
                f"Escalation score: {result['escalation_score']:.3f}."
            )
        else:
            answer = result.get("message", "Loan application not found.")
        source = "loan_status_tool"
    else:
        answer = apply_rag_output_guardrail(state["rag_result"])
        source = "knowledge_base"

    state["response"] = {
        "answer": answer,
        "intent": state["intent"],
        "source": source,
        "thread_id": state.get("thread_id", "default")
    }
    return state


def create_builder():
    builder = StateGraph(AgentState)
    builder.add_node("classify", classify_node)
    builder.add_node("lookup", lookup_node)
    builder.add_node("rag", rag_node)
    builder.add_node("finalize", final_node)

    builder.add_edge(START, "classify")
    builder.add_conditional_edges("classify", route_intent, {
        "lookup": "lookup",
        "rag": "rag"
    })
    builder.add_edge("lookup", "finalize")
    builder.add_edge("rag", "finalize")
    builder.add_edge("finalize", END)
    return builder


db_connection = sqlite3.connect(DB_PATH, check_same_thread=False)
checkpointer = SqliteSaver(db_connection)
agent_graph = create_builder().compile(checkpointer=checkpointer)


def load_history():
    if not os.path.exists(HISTORY_FILE):
        return {}
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}


def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def add_history(thread_id, role, content):
    history = load_history()
    history.setdefault(thread_id, []).append({"role": role, "content": content})
    save_history(history)


def reset_history(thread_id):
    history = load_history()
    history.pop(thread_id, None)
    save_history(history)


def run_agent(query: str, thread_id: str = "default"):
    guard = input_guardrail(query)

    if not guard["allowed"]:
        response = {
            "answer": guard["response"],
            "intent": "rag",
            "source": "guardrail",
            "thread_id": thread_id
        }
        return AgentResponse.model_validate(response).model_dump()

    safe_query = guard["text"]
    add_history(thread_id, "user", safe_query)

    config = {"configurable": {"thread_id": thread_id}}
    state = agent_graph.invoke(
        {"query": safe_query, "thread_id": thread_id},
        config=config
    )

    response = AgentResponse.model_validate(state["response"]).model_dump()
    add_history(thread_id, "assistant", response["answer"])
    return response


def build_interrupt_graph():
    """Graph used only for interruption/resume testing."""
    return create_builder().compile(
        checkpointer=checkpointer,
        interrupt_after=["rag", "lookup"]
    )


if __name__ == "__main__":
    print(run_agent("What documents are required for KYC?", "demo-1"))
    print(run_agent("Check application status for REC0001", "demo-2"))
