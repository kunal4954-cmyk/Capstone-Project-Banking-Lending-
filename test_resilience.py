# test_resilience.py
import time
import random
import asyncio
from concurrent.futures import ThreadPoolExecutor, TimeoutError

from agent import build_interrupt_graph, agent_graph

MAX_ATTEMPTS = 3
INITIAL_INTERVAL = 0.5
MAX_INTERVAL = 2.0
JITTER = 0.2
NODE_TIMEOUT = 2
GLOBAL_TIMEOUT = 5


# ---------------- RETRY TEST ----------------

def transient_operation():
    transient_operation.attempt += 1
    print(f"Attempt {transient_operation.attempt}")

    if transient_operation.attempt < 3:
        raise ConnectionError("Simulated transient failure")

    return "Recovered successfully"


transient_operation.attempt = 0


def retry_with_backoff():
    delay = INITIAL_INTERVAL

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            return transient_operation()

        except ConnectionError as e:
            if attempt == MAX_ATTEMPTS:
                raise

            wait = min(delay, MAX_INTERVAL) + random.uniform(0, JITTER)
            print(f"{e} -> retry in {wait:.2f}s")
            time.sleep(wait)
            delay *= 2


# ---------------- PER-NODE TIMEOUT ----------------

def slow_node():
    time.sleep(4)
    return "Node completed"


def test_node_timeout():
    executor = ThreadPoolExecutor(max_workers=1)
    future = executor.submit(slow_node)

    try:
        print(future.result(timeout=NODE_TIMEOUT))

    except TimeoutError:
        print(f"Node timeout handled after {NODE_TIMEOUT}s")

    finally:
        executor.shutdown(wait=False)


# ---------------- GLOBAL GRAPH TIMEOUT ----------------

async def run_graph_async():
    return await asyncio.to_thread(
        agent_graph.invoke,
        {
            "query": "What documents are required for KYC?",
            "thread_id": "global-timeout-demo"
        },
        {"configurable": {"thread_id": "global-timeout-demo"}}
    )


async def test_global_timeout():
    try:
        result = await asyncio.wait_for(
            run_graph_async(),
            timeout=GLOBAL_TIMEOUT
        )
        print("Graph completed:", result["response"]["answer"])

    except asyncio.TimeoutError:
        print(f"Global graph cancelled after {GLOBAL_TIMEOUT}s")


# ---------------- SQLITE INTERRUPTION / RESUME ----------------

def test_interrupt_resume():
    graph = build_interrupt_graph()

    thread_id = "resume-demo-001"
    config = {"configurable": {"thread_id": thread_id}}

    print("\nStarting graph...")
    graph.invoke(
        {
            "query": "What documents are required for KYC?",
            "thread_id": thread_id
        },
        config=config
    )

    state = graph.get_state(config)

    print("Graph interrupted.")
    print("Thread ID:", thread_id)
    print("Next node(s):", state.next)

    print("\nResuming same thread...")

    result = graph.invoke(
        None,
        config=config
    )

    final_state = graph.get_state(config)

    print("Resume complete.")
    print("Remaining nodes:", final_state.next)

    if result and result.get("response"):
        print("Answer:", result["response"]["answer"])


# ---------------- MAIN ----------------

def main():
    print("=" * 60)
    print("RETRY WITH EXPONENTIAL BACKOFF")
    print("=" * 60)

    transient_operation.attempt = 0
    try:
        print(retry_with_backoff())
    except Exception as e:
        print("Retry failed:", e)

    print("\n" + "=" * 60)
    print("PER-NODE TIMEOUT")
    print("=" * 60)
    test_node_timeout()

    print("\n" + "=" * 60)
    print("SQLITE INTERRUPTION / RESUME")
    print("=" * 60)
    test_interrupt_resume()

    print("\n" + "=" * 60)
    print("GLOBAL GRAPH TIMEOUT")
    print("=" * 60)
    asyncio.run(test_global_timeout())


if __name__ == "__main__":
    main()
