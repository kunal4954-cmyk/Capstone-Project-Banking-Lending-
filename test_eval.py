from statistics import mean
from rag_core import build_vector_stores, retrieve, answer_query

STRATEGIES = ["fixed", "sentence", "semantic"]

IN_SCOPE = [
    "What documents are required for KYC?", "How is EMI calculated?",
    "What affects a credit score?", "Can a borrower prepay a loan?",
    "Who is eligible for an NRI account?"
]

OUT_SCOPE = [
    "How do I cook pasta?", "What is the weather today?",
    "Who won the football world cup?"
]

EVAL_QUERIES = [
    ("What documents are required for KYC?", ["KB004"]),
    ("How is EMI calculated for a loan?", ["KB002"]),
    ("What affects a customer's credit score?", ["KB010"]),
    ("Can I prepay or foreclose my loan?", ["KB008"]),
    ("What happens when EMI payments are missed?", ["KB013"]),
    ("What is the loan recovery process?", ["KB015"]),
    ("How is a loan classified as NPA?", ["KB014"]),
    ("What are the rules for P2P lending?", ["KB020"])
]

TRIAD_QUERIES = [
    ("What determines loan eligibility?", "KB001"),
    ("How is EMI calculated?", "KB002"),
    ("What fees apply to credit cards?", "KB003"),
    ("What documents are needed for KYC?", "KB004"),
    ("How are fraud disputes resolved?", "KB005"),
    ("How can a bank account be closed?", "KB006"),
    ("How are loan interest rates decided?", "KB007"),
    ("What are loan prepayment rules?", "KB008"),
    ("What are minimum balance requirements?", "KB009"),
    ("What factors affect credit score?", "KB010"),
    ("What are the rules for joint accounts?", "KB011"),
    ("Who is eligible for an NRI account?", "KB012"),
    ("What happens after missed EMI payments?", "KB013"),
    ("How do I cook pasta?", None),
    ("Who won today's cricket match?", None)
]

def top_score(q, strategy):
    r = retrieve(q, strategy=strategy, top_k=1)
    return r[0]["similarity"] if r else 0

def calibrate(strategy):
    print(f"\n{'='*65}\nTHRESHOLD CALIBRATION: {strategy.upper()}\n{'='*65}")
    ins = [top_score(q, strategy) for q in IN_SCOPE]
    outs = [top_score(q, strategy) for q in OUT_SCOPE]

    for q, s in zip(IN_SCOPE, ins): print(f"IN  | {s:.4f} | {q}")
    for q, s in zip(OUT_SCOPE, outs): print(f"OUT | {s:.4f} | {q}")

    min_in, max_out = min(ins), max(outs)
    threshold = (min_in + max_out) / 2
    print(f"\nMin in-scope : {min_in:.4f}")
    print(f"Max OOS      : {max_out:.4f}")
    print(f"Threshold    : {threshold:.4f}")
    print("Status       :", "CLEAR SEPARATION" if max_out < min_in else "OVERLAP")
    return round(threshold, 4)

def evaluate(strategy):
    print(f"\n{'='*65}\nRETRIEVAL EVALUATION: {strategy.upper()}\n{'='*65}")
    ps, rs = [], []

    for i, (q, gold) in enumerate(EVAL_QUERIES, 1):
        retrieved = retrieve(q, strategy=strategy, top_k=10)
        docs = list(dict.fromkeys(x["doc_id"] for x in retrieved))[:3]
        relevant = len(set(docs) & set(gold))
        p, r = relevant / 3, relevant / len(gold)
        ps.append(p); rs.append(r)

        print(f"\nQ{i}: {q}")
        print("Gold       :", gold)
        print("Top-3 docs :", docs)
        print(f"P@3 = {relevant}/3 = {p:.4f} | R@3 = {relevant}/{len(gold)} = {r:.4f}")

    p, r = sum(ps)/len(ps), sum(rs)/len(rs)
    print(f"\nAVERAGE\nPrecision@3 : {p:.4f}\nRecall@3    : {r:.4f}")
    return round(p, 4), round(r, 4)

def run_triad(strategy, threshold):
    print(f"\n{'='*65}\n15-QUERY RAG TRIAD EVALUATION\n{'='*65}")
    scores = []

    for i, (q, expected) in enumerate(TRIAD_QUERIES, 1):
        result = answer_query(q, strategy, 3, threshold)
        docs = {x["doc_id"] for x in result["retrieved_chunks"]}

        if expected is None:
            c = g = a = int(result["fallback"])
        else:
            c = int(expected in docs)
            g = int(not result["fallback"] and result["answer"] !=
                    "I don't know based on the available knowledge base.")
            a = int(c and g)

        scores.append((c, g, a))
        print(f"\nQ{i}: {q}")
        print(f"Context relevance : {c}\nGroundedness      : {g}\nAnswer relevance  : {a}")

    avgs = tuple(sum(x[i] for x in scores)/len(scores) for i in range(3))
    print(f"\nRAG TRIAD AVERAGES\nContext relevance : {avgs[0]:.4f}")
    print(f"Groundedness      : {avgs[1]:.4f}\nAnswer relevance  : {avgs[2]:.4f}")
    return avgs

if __name__ == "__main__":
    build_vector_stores(reset=False)
    results = {}

    for s in STRATEGIES:
        threshold = calibrate(s)
        precision, recall = evaluate(s)
        results[s] = {"threshold": threshold, "precision": precision, "recall": recall}

    priority = {"sentence": 3, "semantic": 2, "fixed": 1}
    selected = max(results, key=lambda s:
                   (results[s]["recall"], results[s]["precision"], priority[s]))
    threshold = results[selected]["threshold"]

    print(f"\n{'='*65}\nFINAL RETRIEVAL SELECTION\n{'='*65}")
    for s in STRATEGIES:
        x = results[s]
        print(f"{s:<10} | P@3={x['precision']:.4f} | R@3={x['recall']:.4f} | Threshold={x['threshold']:.4f}")
    print(f"\nSelected strategy : {selected}\nSelected threshold: {threshold:.4f}")

    print(f"\n{'='*65}\nGROUNDED GENERATION / FALLBACK DEMO\n{'='*65}")
    demos = [
        "What are the KYC requirements?", "How is EMI calculated?",
        "What affects credit score?", "What are loan prepayment rules?",
        "Who can open an NRI account?", "How do I make chocolate cake?"
    ]

    for i, q in enumerate(demos, 1):
        r = answer_query(q, selected, 3, threshold)
        print(f"\nQ{i}: {q}\nTop similarity : {r['top_similarity']}")
        print(f"Fallback       : {r['fallback']}\nAnswer         : {r['answer']}")

    c, g, a = run_triad(selected, threshold)
    x = results[selected]

    print(f"\n{'='*65}\nVALUES TO COPY INTO README\n{'='*65}")
    print(f"Strategy          : {selected}")
    print(f"Threshold         : {threshold:.4f}")
    print(f"Precision@3       : {x['precision']:.4f}")
    print(f"Recall@3          : {x['recall']:.4f}")
    print(f"Context relevance : {c:.4f}")
    print(f"Groundedness      : {g:.4f}")
    print(f"Answer relevance  : {a:.4f}")
