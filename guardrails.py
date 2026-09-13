import re

FALLBACK = "I don't know based on the available knowledge base."

PAN = r"\b[A-Z]{5}\d{4}[A-Z]\b"
ACCOUNT = r"(?i)(account(?: number| no\.?)?\s*(?:is|:)?\s*)\d{9,18}\b"
AADHAAR = r"\b\d{4}(?:[\s-]\d{4}){2}\b"

INJECTION_PATTERNS = [
    r"ignore (all |previous )?instructions",
    r"reveal .*system prompt",
    r"show .*system prompt",
    r"bypass .*instructions",
    r"forget .*instructions",
    r"developer message",
    r"internal instructions"
]

def mask_pii(text):
    text = re.sub(ACCOUNT, r"\1[MASKED_ACCOUNT]", text)
    text = re.sub(PAN, "[MASKED_PAN]", text)
    text = re.sub(AADHAAR, "[MASKED_AADHAAR]", text)
    return text

def detect_prompt_injection(text):
    return any(re.search(p, text, re.I) for p in INJECTION_PATTERNS)

def input_guardrail(text):
    masked = mask_pii(text)
    if detect_prompt_injection(masked):
        return {
            "allowed": False,
            "text": masked,
            "reason": "prompt_injection",
            "response": "I cannot follow requests to bypass instructions or reveal protected information."
        }
    return {"allowed": True, "text": masked, "reason": None, "response": None}

def validate_grounding(answer, retrieved_chunks):
    if answer == FALLBACK:
        return True
    if not retrieved_chunks:
        return False
    context = " ".join(x["text"] for x in retrieved_chunks).lower()
    words = [w for w in re.findall(r"\w+", answer.lower()) if len(w) > 3]
    return bool(words) and sum(w in context for w in words) / len(words) >= 0.5

def output_guardrail(answer, retrieved_chunks=None):
    if retrieved_chunks is not None and not validate_grounding(answer, retrieved_chunks):
        return FALLBACK
    return mask_pii(answer)

def apply_rag_output_guardrail(rag_result):
    answer = rag_result.get("answer", FALLBACK)
    chunks = rag_result.get("retrieved_chunks", [])

    if not validate_grounding(answer, chunks):
        return FALLBACK

    return mask_pii(answer)
