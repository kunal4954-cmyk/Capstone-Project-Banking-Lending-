import re

PAN_PATTERN = r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"

AADHAAR_PATTERN = (
    r"\b[2-9][0-9]{3}\s?[0-9]{4}\s?[0-9]{4}\b"
)

BANK_ACC_PATTERN = r"\b[0-9]{9,18}\b"

INJECTION_PATTERNS = [
    r"ignore previous instructions",
    r"ignore all previous instructions",
    r"system prompt",
    r"developer mode",
    r"bypass security",
    r"reveal your rules",
    r"reveal your instructions",
]

def mask_pii(text: str) -> str:
    """Mask PAN, Aadhaar, and bank account numbers."""

    masked = re.sub(
        PAN_PATTERN,
        "[PAN_REDACTED]",
        text,
        flags=re.IGNORECASE
    )

    masked = re.sub(
        AADHAAR_PATTERN,
        "[AADHAAR_REDACTED]",
        masked
    )

    masked = re.sub(
        r"(?:account|acc|acct)?\s*#?\s*" + BANK_ACC_PATTERN,
        "[BANK_ACCOUNT_REDACTED]",
        masked,
        flags=re.IGNORECASE
    )

    return masked

def detect_prompt_injection(text: str) -> bool:
    """Return True when a known injection pattern is detected."""

    text_lower = text.lower()

    return any(
        re.search(pattern, text_lower)
        for pattern in INJECTION_PATTERNS
    )

def verify_groundedness(
    retrieved_context: str,
    answer: str
) -> bool:
    """
    Basic deterministic groundedness check for MOCK_LLM.
    """

    if not retrieved_context.strip():
        return False

    refusal_text = (
        "i am sorry, but i do not have enough policy information"
    )

    if refusal_text in answer.lower():
        return False

    return True
