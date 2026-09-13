# app.py
import json, os, time, uuid
from typing import Union
from fastapi import FastAPI, HTTPException
from schemas import AskRequest, AgentResponse, AddDocumentRequest, AddDocumentResponse, ErrorResponse
from agent import run_agent
from guardrails import input_guardrail, output_guardrail
from rag_core import (chroma_client, create_embeddings, fixed_size_chunk,
    sentence_based_chunk, semantic_based_chunk, FIXED_COLLECTION_NAME,
    SENTENCE_COLLECTION_NAME, SEMANTIC_COLLECTION_NAME)

app = FastAPI(title="Cred Banking & FinTech Support Agent", version="1.0")
LOG_FILE = os.path.join(os.path.dirname(__file__), "requests.jsonl")

def write_log(trace_id, endpoint, query, status, start):
    row = {"trace_id": trace_id, "endpoint": endpoint, "query": query,
           "status": status, "duration_ms": round((time.perf_counter()-start)*1000, 2)}
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

@app.get("/")
def root():
    return {"service": "Cred Banking & FinTech Support Agent", "status": "running"}

@app.post("/ask", response_model=Union[AgentResponse, ErrorResponse])
def ask(request: AskRequest):
    start, trace_id = time.perf_counter(), str(uuid.uuid4())
    guard = input_guardrail(request.query)
    safe_query = guard["text"]

    if not guard["allowed"]:
        write_log(trace_id, "/ask", safe_query, "blocked", start)
        return ErrorResponse(error=guard["response"])

    try:
        result = run_agent(safe_query, request.thread_id)
        response = AgentResponse(
            answer=output_guardrail(result["answer"]),
            intent=result["intent"],
            source=result["source"],
            thread_id=result["thread_id"]
        )
        write_log(trace_id, "/ask", safe_query, "success", start)
        return response
    except Exception as e:
        write_log(trace_id, "/ask", safe_query, "error", start)
        return ErrorResponse(error=str(e))

def add_chunks(name, doc, chunks, strategy):
    c = chroma_client.get_or_create_collection(name=name, metadata={"hnsw:space": "cosine"})
    if not chunks: return
    ids = [f"{doc.doc_id}_{strategy}_{i:03d}" for i in range(len(chunks))]
    meta = [{"doc_id": doc.doc_id, "topic": doc.topic, "title": doc.title,
             "strategy": strategy} for _ in chunks]
    c.add(ids=ids, documents=chunks, metadatas=meta, embeddings=create_embeddings(chunks))

@app.post("/add-document", response_model=Union[AddDocumentResponse, ErrorResponse])
def add_document(request: AddDocumentRequest):
    start, trace_id = time.perf_counter(), str(uuid.uuid4())
    guard = input_guardrail(request.content)
    content = guard["text"]

    if not guard["allowed"]:
        write_log(trace_id, "/add-document", content, "blocked", start)
        return ErrorResponse(error=guard["response"])

    try:
        for name in [FIXED_COLLECTION_NAME, SENTENCE_COLLECTION_NAME, SEMANTIC_COLLECTION_NAME]:
            try:
                if chroma_client.get_collection(name).get(where={"doc_id": request.doc_id})["ids"]:
                    raise HTTPException(409, "Document ID already exists.")
            except HTTPException:
                raise
            except Exception:
                pass

        doc = request.model_copy(update={"content": content})
        add_chunks(FIXED_COLLECTION_NAME, doc, fixed_size_chunk(content, 300, 60), "fixed")
        add_chunks(SENTENCE_COLLECTION_NAME, doc, sentence_based_chunk(content, 2), "sentence")
        add_chunks(SEMANTIC_COLLECTION_NAME, doc, semantic_based_chunk(content, 0.65), "semantic")

        write_log(trace_id, "/add-document", f"document:{request.doc_id}", "success", start)
        return AddDocumentResponse(
            success=True, doc_id=request.doc_id,
            message="Document added to all vector collections."
        )
    except HTTPException:
        raise
    except Exception as e:
        write_log(trace_id, "/add-document", f"document:{request.doc_id}", "error", start)
        return ErrorResponse(error=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000)
