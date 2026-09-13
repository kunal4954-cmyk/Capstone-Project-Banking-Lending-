import json
import os
import time
import uuid

import chromadb
from fastapi import FastAPI, HTTPException

from agent import agent_graph
from guardrails import mask_pii
from rag_core import model
from schemas import (
    AddDocumentRequest,
    AddDocumentResponse,
    AgentStructuredResponse,
    AskRequest,
    AskResponse,
)


app = FastAPI(
    title="Cred Domain Support Agent API",
    version="1.0"
)

LOG_FILE = "logs/requests.jsonl"
VECTOR_PATH = "vector_store"
RAG_COLLECTION = "fixed_chunks"

os.makedirs("logs", exist_ok=True)

def log_request_jsonl(
    trace_id: str,
    thread_id: str,
    raw_query: str,
    response_data: dict,
    duration_ms: float
):
    entry = {
        "timestamp": time.strftime(
            "%Y-%m-%dT%H:%M:%SZ",
            time.gmtime()
        ),
        "trace_id": trace_id,
        "thread_id": thread_id,
        "query_masked": mask_pii(raw_query),
        "response": response_data,
        "duration_ms": round(duration_ms, 2),
    }

    with open(
        LOG_FILE,
        "a",
        encoding="utf-8"
    ) as file:
        file.write(
            json.dumps(
                entry,
                ensure_ascii=False
            )
            + "\n"
        )

@app.post(
    "/ask",
    response_model=AskResponse
)
def ask_agent(req: AskRequest):

    start_time = time.time()
    trace_id = f"trace-{uuid.uuid4().hex[:8]}"

    config = {
        "configurable": {
            "thread_id": req.thread_id
        }
    }

    try:
        final_state = agent_graph.invoke(
            {
                "query": req.query,
                "conversation_history": []
            },
            config=config
        )

        response = AgentStructuredResponse(
            **final_state["response"]
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Agent execution failed: {exc}"
        )

    duration_ms = (
        time.time() - start_time
    ) * 1000

    log_request_jsonl(
        trace_id,
        req.thread_id,
        req.query,
        response.model_dump(),
        duration_ms
    )

    return AskResponse(
        trace_id=trace_id,
        status="success",
        data=response
    )

@app.post(
    "/add-document",
    response_model=AddDocumentResponse
)
def add_document(req: AddDocumentRequest):

    client = chromadb.PersistentClient(
        path=VECTOR_PATH
    )

    try:
        collection = client.get_collection(
            RAG_COLLECTION
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Vector collection unavailable: {exc}"
        )

    chunk_id = f"dynamic_{req.doc_id}"

    # Prevent duplicate IDs during repeated testing
    existing = collection.get(
        ids=[chunk_id]
    )

    if existing["ids"]:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Document {req.doc_id} "
                "already exists."
            )
        )

    embedding = model.encode(
        req.content
    ).tolist()

    collection.add(
        ids=[chunk_id],
        embeddings=[embedding],
        documents=[req.content],
        metadatas=[
            {
                "doc_id": req.doc_id,
                "topic": req.topic,
                "dynamic": True,
            }
        ]
    )

    return AddDocumentResponse(
        status="success",
        message=(
            f"Document {req.doc_id} successfully "
            "embedded and indexed."
        ),
        doc_id=req.doc_id
    )

@app.get("/health")
def health():
    return {
        "status": "ok",
        "rag_collection": RAG_COLLECTION
    }
