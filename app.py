# app.py
import json, os, time, uuid
from typing import Union
from fastapi import FastAPI, HTTPException
from schemas import AskRequest, AgentResponse, AddDocumentRequest, AddDocumentResponse, ErrorResponse
from agent import run_agent
from guardrails import input_guardrail, output_guardrail
from rag_core import (
    chroma_client, create_embeddings, fixed_size_chunk,
    sentence_based_chunk, semantic_based_chunk,
    FIXED_COLLECTION_NAME, SENTENCE_COLLECTION_NAME, SEMANTIC_COLLECTION_NAME
)

app = FastAPI(title="Cred Banking & FinTech Support Agent", version="1.0")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "requests.jsonl")


def write_log(trace_id, endpoint, query, status, duration_ms):
    record = {
        "trace_id": trace_id,
        "endpoint": endpoint,
        "query": query,
        "status": status,
        "duration_ms": round(duration_ms, 2)
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


@app.get("/")
def root():
    return {"service": "Cred Banking & FinTech Support Agent", "status": "running"}


@app.post("/ask", response_model=Union[AgentResponse, ErrorResponse])
def ask(request: AskRequest):
    start = time.perf_counter()
    trace_id = str(uuid.uuid4())

    guard = input_guardrail(request.query)
    safe_query = guard["text"]

    if not guard["allowed"]:
        duration = (time.perf_counter() - start) * 1000
        write_log(trace_id, "/ask", safe_query, "blocked", duration)
        return ErrorResponse(error=guard["response"])

    try:
        result = run_agent(safe_query, request.thread_id)
        result["answer"] = output_guardrail(result["answer"], grounded=True)
        validated = AgentResponse.model_validate(result)

        duration = (time.perf_counter() - start) * 1000
        write_log(trace_id, "/ask", safe_query, "success", duration)
        return validated

    except Exception as e:
        duration = (time.perf_counter() - start) * 1000
        write_log(trace_id, "/ask", safe_query, "error", duration)
        return ErrorResponse(error=str(e))


def add_chunks(collection_name, doc, chunks, strategy):
    collection = chroma_client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )

    ids, documents, metadatas = [], [], []

    for i, text in enumerate(chunks):
        ids.append(f"{doc.doc_id}_{strategy}_{i:03d}")
        documents.append(text)
        metadatas.append({
            "doc_id": doc.doc_id,
            "topic": doc.topic,
            "title": doc.title,
            "strategy": strategy
        })

    if documents:
        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=create_embeddings(documents)
        )


@app.post("/add-document", response_model=Union[AddDocumentResponse, ErrorResponse])
def add_document(request: AddDocumentRequest):
    start = time.perf_counter()
    trace_id = str(uuid.uuid4())

    guard = input_guardrail(request.content)
    safe_content = guard["text"]

    if not guard["allowed"]:
        duration = (time.perf_counter() - start) * 1000
        write_log(trace_id, "/add-document", safe_content, "blocked", duration)
        return ErrorResponse(error=guard["response"])

    try:
        existing = []
        for name in [FIXED_COLLECTION_NAME, SENTENCE_COLLECTION_NAME, SEMANTIC_COLLECTION_NAME]:
            try:
                collection = chroma_client.get_collection(name)
                result = collection.get(where={"doc_id": request.doc_id})
                existing.extend(result.get("ids", []))
            except Exception:
                pass

        if existing:
            raise HTTPException(status_code=409, detail="Document ID already exists.")

        safe_doc = request.model_copy(update={"content": safe_content})

        add_chunks(
            FIXED_COLLECTION_NAME,
            safe_doc,
            fixed_size_chunk(safe_content, chunk_size=300, overlap=60),
            "fixed"
        )

        add_chunks(
            SENTENCE_COLLECTION_NAME,
            safe_doc,
            sentence_based_chunk(safe_content, sentences_per_chunk=2),
            "sentence"
        )

        add_chunks(
            SEMANTIC_COLLECTION_NAME,
            safe_doc,
            semantic_based_chunk(safe_content, similarity_threshold=0.65),
            "semantic"
        )

        duration = (time.perf_counter() - start) * 1000
        write_log(trace_id, "/add-document", f"document:{request.doc_id}", "success", duration)

        return AddDocumentResponse(
            success=True,
            doc_id=request.doc_id,
            message="Document added to all vector collections."
        )

    except HTTPException:
        raise

    except Exception as e:
        duration = (time.perf_counter() - start) * 1000
        write_log(trace_id, "/add-document", f"document:{request.doc_id}", "error", duration)
        return ErrorResponse(error=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
