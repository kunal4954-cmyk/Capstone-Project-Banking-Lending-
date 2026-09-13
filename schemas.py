# schemas.py
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    query: str = Field(..., min_length=1)
    thread_id: str = "default"


class RetrievedChunk(BaseModel):
    chunk_id: str
    doc_id: str
    topic: str
    title: str
    similarity: float


class AgentResponse(BaseModel):
    answer: str
    intent: Literal["rag", "lookup"]
    source: str
    thread_id: str


class LoanLookupResponse(BaseModel):
    found: bool
    record_id: Optional[str] = None
    status: Optional[str] = None
    loan_amount_inr: Optional[float] = None
    escalation_score: Optional[float] = None
    needs_escalation: Optional[bool] = None
    message: Optional[str] = None


class RAGResponse(BaseModel):
    query: str
    answer: str
    strategy: str
    top_similarity: Optional[float] = None
    fallback: bool
    retrieved_chunks: List[RetrievedChunk] = []


class AddDocumentRequest(BaseModel):
    doc_id: str
    topic: str
    title: str
    content: str
    source: str = "User-added document"


class AddDocumentResponse(BaseModel):
    success: bool
    doc_id: str
    message: str


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
