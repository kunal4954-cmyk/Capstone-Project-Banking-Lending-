import os
import re
from typing import List, Dict

import numpy as np
import chromadb
from sentence_transformers import SentenceTransformer

from kb_dataset import KB_DOCUMENTS

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

CHROMA_DIR = os.path.join(
    BASE_DIR,
    "chroma_db"
)

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

FIXED_COLLECTION_NAME = "banking_fixed_chunks"
SENTENCE_COLLECTION_NAME = "banking_sentence_chunks"
SEMANTIC_COLLECTION_NAME = "banking_semantic_chunks"

TOP_K = 3

SIMILARITY_THRESHOLD = None

print("=" * 70)
print("LOADING EMBEDDING MODEL")
print("=" * 70)

embedding_model = SentenceTransformer(
    EMBEDDING_MODEL_NAME
)

print(
    f"Model loaded: {EMBEDDING_MODEL_NAME}"
)

chroma_client = chromadb.PersistentClient(
    path=CHROMA_DIR
)

def split_sentences(
    text: str
) -> List[str]:


    if not text:
        return []

    sentences = re.split(
        r'(?<=[.!?])\s+',
        text.strip()
    )

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]

def fixed_size_chunk(
    text: str,
    chunk_size: int = 300,
    overlap: int = 60
) -> List[str]:

    if not text:
        return []

    if chunk_size <= 0:
        raise ValueError(
            "chunk_size must be greater than 0."
        )

    if overlap < 0:
        raise ValueError(
            "overlap cannot be negative."
        )

    if overlap >= chunk_size:
        raise ValueError(
            "overlap must be smaller than chunk_size."
        )

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunk = text[
            start:end
        ].strip()

        if chunk:
            chunks.append(
                chunk
            )

        if end >= len(text):
            break

        start = end - overlap

    return chunks

def sentence_based_chunk(
    text: str,
    sentences_per_chunk: int = 2
) -> List[str]:


    if sentences_per_chunk <= 0:

        raise ValueError(
            "sentences_per_chunk must be greater than 0."
        )

    sentences = split_sentences(
        text
    )

    chunks = []

    for index in range(
        0,
        len(sentences),
        sentences_per_chunk
    ):

        chunk = " ".join(
            sentences[
                index:
                index + sentences_per_chunk
            ]
        ).strip()

        if chunk:
            chunks.append(
                chunk
            )

    return chunks

def cosine_similarity(
    vector_a,
    vector_b
) -> float:

    """
    Calculate cosine similarity between two vectors.
    """

    vector_a = np.asarray(
        vector_a,
        dtype=np.float32
    )

    vector_b = np.asarray(
        vector_b,
        dtype=np.float32
    )

    denominator = (
        np.linalg.norm(vector_a)
        *
        np.linalg.norm(vector_b)
    )

    if denominator == 0:

        return 0.0

    return float(
        np.dot(
            vector_a,
            vector_b
        )
        /
        denominator
    )

def semantic_based_chunk(
    text: str,
    similarity_threshold: float = 0.65
) -> List[str]:


    sentences = split_sentences(
        text
    )

    if not sentences:

        return []

    if len(sentences) == 1:

        return sentences

    sentence_embeddings = (
        embedding_model.encode(
            sentences,
            normalize_embeddings=True,
            show_progress_bar=False
        )
    )


    chunks = []

    current_chunk = [
        sentences[0]
    ]

    for index in range(
        1,
        len(sentences)
    ):

        previous_embedding = (
            sentence_embeddings[
                index - 1
            ]
        )

        current_embedding = (
            sentence_embeddings[
                index
            ]
        )


        similarity = cosine_similarity(
            previous_embedding,
            current_embedding
        )

        if similarity >= similarity_threshold:

            current_chunk.append(
                sentences[index]
            )

        else:

            chunks.append(
                " ".join(
                    current_chunk
                )
            )

            current_chunk = [
                sentences[index]
            ]

    if current_chunk:

        chunks.append(
            " ".join(
                current_chunk
            )
        )


    return chunks

def build_chunks(
    strategy: str
) -> List[Dict]:

    """
    Convert all KB documents into chunks.

    Each chunk maintains its relationship with
    its parent KB document.
    """

    all_chunks = []


    for document in KB_DOCUMENTS:

        text = document[
            "content"
        ].strip()

        if strategy == "fixed":

            chunks = fixed_size_chunk(
                text=text,
                chunk_size=300,
                overlap=60
            )

        elif strategy == "sentence":

            chunks = sentence_based_chunk(
                text=text,
                sentences_per_chunk=2
            )

        elif strategy == "semantic":

            chunks = semantic_based_chunk(
                text=text,
                similarity_threshold=0.65
            )


        else:

            raise ValueError(
                "strategy must be "
                "'fixed', 'sentence', or 'semantic'."
            )

        for chunk_number, chunk_text in enumerate(
            chunks
        ):

            chunk_id = (
                f'{document["doc_id"]}'
                f'_{strategy}'
                f'_{chunk_number:03d}'
            )


            all_chunks.append(

                {
                    "chunk_id": chunk_id,

                    "doc_id":
                        document["doc_id"],

                    "topic":
                        document["topic"],

                    "title":
                        document["title"],

                    "strategy":
                        strategy,

                    "text":
                        chunk_text
                }

            )


    return all_chunks

def create_embeddings(
    texts: List[str]
) -> List[List[float]]:

    """
    Create normalized SentenceTransformer embeddings.
    """

    if not texts:

        return []


    embeddings = embedding_model.encode(

        texts,

        normalize_embeddings=True,

        show_progress_bar=False
    )


    return embeddings.tolist()

def create_collection(
    collection_name: str,
    chunks: List[Dict],
    reset: bool = False
):

    """
    Create and populate one ChromaDB collection.
    """

    if reset:

        try:

            chroma_client.delete_collection(
                collection_name
            )

        except Exception:

            pass

    collection = (
        chroma_client.get_or_create_collection(

            name=collection_name,

            metadata={
                "hnsw:space":
                    "cosine"
            }

        )
    )

    existing_count = (
        collection.count()
    )


    if existing_count > 0:

        print(
            f"{collection_name:<30}: "
            f"{existing_count} existing chunks"
        )

        return collection

    texts = [

        chunk["text"]

        for chunk in chunks
    ]


    embeddings = create_embeddings(
        texts
    )


    ids = [

        chunk["chunk_id"]

        for chunk in chunks
    ]


    metadatas = [

        {
            "doc_id":
                chunk["doc_id"],

            "topic":
                chunk["topic"],

            "title":
                chunk["title"],

            "strategy":
                chunk["strategy"]
        }

        for chunk in chunks
    ]

    collection.add(

        ids=ids,

        documents=texts,

        metadatas=metadatas,

        embeddings=embeddings
    )


    print(
        f"{collection_name:<30}: "
        f"{collection.count()} chunks indexed"
    )


    return collection

def build_vector_stores(
    reset: bool = False
):

    print("\n" + "=" * 70)

    print(
        "BUILDING CHROMADB VECTOR STORES"
    )

    print("=" * 70)

    fixed_chunks = build_chunks(
        strategy="fixed"
    )


    sentence_chunks = build_chunks(
        strategy="sentence"
    )


    semantic_chunks = build_chunks(
        strategy="semantic"
    )

    print(
        f"\nFixed-size chunks : "
        f"{len(fixed_chunks)}"
    )

    print(
        f"Sentence chunks   : "
        f"{len(sentence_chunks)}"
    )

    print(
        f"Semantic chunks   : "
        f"{len(semantic_chunks)}"
    )


    print(
        "\nIndexing collections..."
    )

    fixed_collection = create_collection(

        collection_name=
            FIXED_COLLECTION_NAME,

        chunks=fixed_chunks,

        reset=reset
    )

    sentence_collection = create_collection(

        collection_name=
            SENTENCE_COLLECTION_NAME,

        chunks=sentence_chunks,

        reset=reset
    )

    semantic_collection = create_collection(

        collection_name=
            SEMANTIC_COLLECTION_NAME,

        chunks=semantic_chunks,

        reset=reset
    )


    print(
        "\nVector stores ready."
    )


    return (
        fixed_collection,
        sentence_collection,
        semantic_collection
    )

def get_collection(
    strategy: str
):

    """
    Return the Chroma collection corresponding
    to a chunking strategy.
    """

    if strategy == "fixed":

        collection_name = (
            FIXED_COLLECTION_NAME
        )


    elif strategy == "sentence":

        collection_name = (
            SENTENCE_COLLECTION_NAME
        )


    elif strategy == "semantic":

        collection_name = (
            SEMANTIC_COLLECTION_NAME
        )


    else:

        raise ValueError(
            "strategy must be "
            "'fixed', 'sentence', or 'semantic'."
        )


    try:

        return chroma_client.get_collection(
            collection_name
        )


    except Exception as error:

        raise RuntimeError(

            f"Collection '{collection_name}' "
            f"does not exist. Run "
            f"build_vector_stores() first."

        ) from error

def embed_query(
    query: str
) -> List[float]:

    """
    Generate embedding for one user query.
    """

    query_embedding = (
        embedding_model.encode(

            [query],

            normalize_embeddings=True,

            show_progress_bar=False

        )[0]
    )


    return query_embedding.tolist()

def retrieve(
    query: str,
    strategy: str = "sentence",
    top_k: int = TOP_K
) -> List[Dict]:

    """
    Retrieve top-k relevant chunks.

    Chroma cosine distance is converted to
    cosine similarity using:

        similarity = 1 - distance
    """

    if not query.strip():

        return []


    collection = get_collection(
        strategy
    )


    query_embedding = embed_query(
        query
    )


    available_chunks = (
        collection.count()
    )


    if available_chunks == 0:

        return []


    n_results = min(
        top_k,
        available_chunks
    )


    results = collection.query(

        query_embeddings=[
            query_embedding
        ],

        n_results=n_results,

        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )


    retrieved_chunks = []


    ids = (
        results.get(
            "ids",
            [[]]
        )[0]
    )


    documents = (
        results.get(
            "documents",
            [[]]
        )[0]
    )


    metadatas = (
        results.get(
            "metadatas",
            [[]]
        )[0]
    )


    distances = (
        results.get(
            "distances",
            [[]]
        )[0]
    )

    for (
        chunk_id,
        document,
        metadata,
        distance
    ) in zip(
        ids,
        documents,
        metadatas,
        distances
    ):

        cosine_distance = float(
            distance
        )


        cosine_similarity_score = (
            1.0
            -
            cosine_distance
        )


        retrieved_chunks.append(

            {
                "chunk_id":
                    chunk_id,

                "doc_id":
                    metadata["doc_id"],

                "topic":
                    metadata["topic"],

                "title":
                    metadata["title"],

                "strategy":
                    metadata["strategy"],

                "text":
                    document,

                "distance":
                    cosine_distance,

                "similarity":
                    cosine_similarity_score
            }

        )


    return retrieved_chunks

def mock_generate_answer(query: str, retrieved_chunks: List[Dict]) -> str:
    if not retrieved_chunks:
        return "I don't know based on the available knowledge base."

    query_emb = embedding_model.encode(
        query,
        normalize_embeddings=True,
        show_progress_bar=False
    )

    best_text, best_score = None, -1

    for chunk in retrieved_chunks:
        text = chunk["text"].strip()

        searchable_text = (
            f'{chunk["title"]}. '
            f'{chunk["topic"].replace("_", " ")}. '
            f'{text}'
        )

        context_emb = embedding_model.encode(
            searchable_text,
            normalize_embeddings=True,
            show_progress_bar=False
        )

        score = cosine_similarity(query_emb, context_emb)

        if score > best_score:
            best_score = score
            best_text = text

    return best_text or (
        "I don't know based on the available knowledge base."
    )

def answer_query(
    query: str,
    strategy: str = "sentence",
    top_k: int = TOP_K,
    similarity_threshold=None
) -> Dict:

    """
    Complete RAG pipeline.

    1. Embed query
    2. Retrieve top-k chunks
    3. Check similarity threshold
    4. Return grounded MOCK_LLM answer
    """

    retrieved_chunks = retrieve(

        query=query,

        strategy=strategy,

        top_k=top_k
    )

    if not retrieved_chunks:

        return {

            "query":
                query,

            "answer":
                (
                    "I don't know based on the "
                    "available knowledge base."
                ),

            "strategy":
                strategy,

            "top_similarity":
                None,

            "fallback":
                True,

            "retrieved_chunks":
                []
        }

    top_similarity = (
        retrieved_chunks[0][
            "similarity"
        ]
    )


    # --------------------------------------------------------
    # Threshold-based fallback
    # --------------------------------------------------------

    if (
        similarity_threshold
        is not None
        and
        top_similarity
        <
        similarity_threshold
    ):

        answer = (
            "I don't know based on the "
            "available knowledge base."
        )

        fallback = True


    else:

        answer = mock_generate_answer(

            query=query,

            retrieved_chunks=
                retrieved_chunks
        )

        fallback = False


    return {

        "query":
            query,

        "answer":
            answer,

        "strategy":
            strategy,

        "top_similarity":
            round(
                top_similarity,
                4
            ),

        "fallback":
            fallback,

        "retrieved_chunks":
            retrieved_chunks
    }

def print_retrieval_results(
    query: str,
    strategy: str,
    top_k: int = 3
):

    """
    Print retrieval results for inspection.
    """

    results = retrieve(

        query=query,

        strategy=strategy,

        top_k=top_k
    )


    print("\n" + "=" * 70)

    print(
        f"QUERY    : {query}"
    )

    print(
        f"STRATEGY : {strategy.upper()}"
    )

    print("=" * 70)


    if not results:

        print(
            "No results retrieved."
        )

        return


    for rank, result in enumerate(
        results,
        start=1
    ):

        print(
            f"\nRank       : {rank}"
        )

        print(
            f'Document   : '
            f'{result["doc_id"]}'
        )

        print(
            f'Title      : '
            f'{result["title"]}'
        )

        print(
            f'Topic      : '
            f'{result["topic"]}'
        )

        print(
            f'Similarity : '
            f'{result["similarity"]:.4f}'
        )

        print(
            f'Chunk ID   : '
            f'{result["chunk_id"]}'
        )

        print(
            f'Chunk      : '
            f'{result["text"]}'
        )

        print(
            "-" * 70
        )

def compare_strategies(
    query: str,
    top_k: int = 3
):

    """
    Retrieve the same query using all
    three chunking strategies.
    """

    print("\n" + "#" * 70)

    print(
        "CHUNKING STRATEGY COMPARISON"
    )

    print("#" * 70)


    for strategy in [

        "fixed",
        "sentence",
        "semantic"

    ]:

        print_retrieval_results(

            query=query,

            strategy=strategy,

            top_k=top_k
        )

def print_chunk_statistics():

    """
    Display number of chunks created by
    each strategy.
    """

    print("\n" + "=" * 70)

    print(
        "CHUNKING STATISTICS"
    )

    print("=" * 70)


    for strategy in [

        "fixed",
        "sentence",
        "semantic"

    ]:

        chunks = build_chunks(
            strategy
        )


        chunk_lengths = [

            len(
                chunk["text"]
            )

            for chunk in chunks
        ]


        if chunk_lengths:

            average_length = (

                sum(
                    chunk_lengths
                )
                /
                len(
                    chunk_lengths
                )

            )

        else:

            average_length = 0


        print(
            f"\nStrategy      : "
            f"{strategy}"
        )

        print(
            f"Total chunks  : "
            f"{len(chunks)}"
        )

        print(
            f"Average length: "
            f"{average_length:.2f} characters"
        )

def run_demo():

    sample_query = (
        "What factors affect a customer's credit score?"
    )


    compare_strategies(

        query=sample_query,

        top_k=3
    )

    print("\n" + "=" * 70)

    print(
        "SAMPLE GROUNDED RESPONSE"
    )

    print("=" * 70)


    result = answer_query(

        query=sample_query,

        strategy="sentence",

        top_k=3,

        # No threshold until calibration
        similarity_threshold=None
    )


    print(
        f'\nQuery:\n'
        f'{result["query"]}'
    )


    print(
        f'\nTop similarity:\n'
        f'{result["top_similarity"]}'
    )


    print(
        f'\nAnswer:\n'
        f'{result["answer"]}'
    )

if __name__ == "__main__":
    build_vector_stores(
        reset=True
    )
    print_chunk_statistics()
    run_demo()
