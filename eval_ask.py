import time
import requests

URL = "http://127.0.0.1:8000/api/posts/ask_ai/"

QUESTIONS = [
    ("What is the demo password for the staging box?", "The demo password for the staging box is river-stone-19."),
    ("What does HNSW do for latency?", "It keeps latency low while holding recall high enough for most RAG work."),
    ("What format can Django's built-in logging write?", "Django's built-in logging can write JSON lines."),
    ("Why is embedding a whole blog post as one vector a bad idea?", "If you embed the full post as one vector, search can only say that the post is roughly related."),
    ("How does a Django request hand off slow work to a background worker?", "The web process pushes a small message onto a Redis list."),
    ("Why should I actually test restoring my database backups?", "A backup that has never been restored is only a hope."),
    ("Why is cross-encoder reranking affordable even though it is slow?", "The extra cost is acceptable because the cross-encoder runs on only the short list, not on the whole corpus."),
    ("Should I call an external API inside transaction.atomic?", "If an external call must happen, do it after the transaction commits."),
    ("Which Postgres index speeds up icontains searches on short fields like titles?", "For shorter fields such as titles or tags, a trigram index (pg_trgm) helps `icontains` and similarity searches."),
    ("What is the capital of France?", "not found"),
    ("How do I stop the same Stripe webhook event from being applied twice?", "Store the Stripe event id in a processed-events table."),
    ("Does Django need code changes to connect through PgBouncer?", "Django talks to PgBouncer exactly as it would talk to Postgres; only the host and port change."),
    ("What status code should the analytics ingestion endpoint return?", "Return 204 immediately; do not wait for downstream processing."),
    ("best biryani in bangalore", "not found"),
    ("What is the SSH port of the staging box?", "not found"),
]

for i, (question, expected) in enumerate(QUESTIONS, start=1):
    print(f"\n{'='*60}")
    print(f"#{i} {question}")
    print(f"Expected: {expected}")
    try:
        res = requests.post(URL, json={"question": question}, timeout=60)
        data = res.json()
        print(f"Answer: {data.get('answer', '')}")
        sources = data.get("sources", [])
        print(f"Sources: {len(sources)}")
        for s in sources[:2]:
            print(f"  - {s.get('sentence', '')[:80]}")
    except Exception as e:
        print(f"ERROR: {e}")
    if i < len(QUESTIONS):
        time.sleep(25)

print("\nDone.")