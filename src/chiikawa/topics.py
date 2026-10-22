"""Group the day's articles into topics, and track every run in MLflow.

Two models, same input and output:
- baseline: TF-IDF + KMeans (light, always available)
- bertopic: BERTopic on multilingual embeddings (install with `uv sync --extra topics`)
"""

import argparse
import hashlib
import html
import json
import os
import re
from collections import Counter
from pathlib import Path

import mlflow
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import silhouette_score

from chiikawa.urls import canonical_url

SEED = 42
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"

# Common French words that say nothing about a topic
FRENCH_STOP_WORDS = sorted(
    set(
        """
        a à au aux avec ce ces cet cette d dans de des du elle en et eux il ils je l la le les
        leur leurs lui m ma mais me même mes moi mon n ne nos notre nous on ou où par pas pour
        qu que qui s sa se ses son sur t ta te tes toi ton tu un une vos votre vous y été être
        est sont ont a fait faire plus moins après avant contre entre chez sans sous selon
        comme deux trois très tout tous toute toutes aussi encore dont quand alors ans an
        c j cela ça ici là si non oui ni car donc or ainsi peu bien
        """.split()
    )
)


def prepare_docs(items: list[dict]) -> tuple[list[str], list[dict]]:
    """Remove duplicate articles (same clean URL) and empty titles; return texts and items."""
    seen, docs, kept = set(), [], []
    for item in items:
        title = item.get("title", "").strip()
        key = canonical_url(item.get("link", ""))
        if not title or key in seen:
            continue
        seen.add(key)
        excerpt = html.unescape(re.sub(r"<[^>]+>", " ", item.get("excerpt", "")))
        docs.append(re.sub(r"\s+", " ", f"{title}. {excerpt}").strip())
        kept.append({**item, "link": key})
    return docs, kept


def vectorize(docs: list[str]):
    """TF-IDF matrix and vocabulary, shared by both models so metrics compare fairly."""
    vectorizer = TfidfVectorizer(
        stop_words=FRENCH_STOP_WORDS, min_df=2, max_df=0.5, token_pattern=r"(?u)\b\w\w\w+\b"
    )
    return vectorizer.fit_transform(docs), vectorizer.get_feature_names_out()


def baseline_topics(matrix, vocab, k: int) -> tuple[list[int], dict[int, str]]:
    """KMeans on TF-IDF; each topic is named by its 3 strongest words."""
    model = KMeans(n_clusters=k, random_state=SEED, n_init=10).fit(matrix)
    names = {
        topic: " · ".join(vocab[i] for i in center.argsort()[::-1][:3])
        for topic, center in enumerate(model.cluster_centers_)
    }
    return model.labels_.tolist(), names


def bertopic_topics(docs: list[str], min_topic_size: int) -> tuple[list[int], dict[int, str]]:
    """BERTopic with multilingual embeddings; topic -1 holds the outliers."""
    from bertopic import BERTopic  # heavy (torch), only needed for this model
    from sklearn.feature_extraction.text import CountVectorizer
    from umap import UMAP

    model = BERTopic(
        embedding_model=EMBEDDING_MODEL,
        umap_model=UMAP(n_neighbors=15, n_components=5, metric="cosine", random_state=SEED),
        vectorizer_model=CountVectorizer(stop_words=FRENCH_STOP_WORDS),
        min_topic_size=min_topic_size,
    )
    labels, _ = model.fit_transform(docs)
    names = {
        topic: " · ".join(word for word, _ in model.get_topic(topic)[:3])
        for topic in set(labels)
        if topic != -1
    }
    return list(labels), names


def build_edition(labels: list[int], names: dict[int, str], items: list[dict]) -> list[dict]:
    """The day's topics: name, newspapers covering it, links. Most-covered topics first."""
    groups: dict[int, list[dict]] = {}
    for label, item in zip(labels, items, strict=True):
        if label != -1:
            groups.setdefault(label, []).append(item)
    edition = [
        {
            "topic": names[label],
            "sources": sorted({a["source"] for a in articles}),
            "articles": [
                {"title": a["title"], "source": a["source"], "link": a["link"]} for a in articles
            ],
        }
        for label, articles in groups.items()
    ]
    return sorted(edition, key=lambda t: (len(t["sources"]), len(t["articles"])), reverse=True)


def topic_metrics(matrix, labels: list[int], edition: list[dict]) -> dict[str, float]:
    """Quality numbers logged for every run, the same for both models."""
    clustered = [i for i, label in enumerate(labels) if label != -1]
    kept = [labels[i] for i in clustered]
    silhouette = (
        float(silhouette_score(matrix[clustered], kept, metric="cosine", random_state=SEED))
        if 1 < len(set(kept)) < len(kept)
        else 0.0
    )
    return {
        "n_docs": len(labels),
        "n_topics": len(edition),
        "outlier_share": 1 - len(clustered) / len(labels),
        "silhouette": silhouette,
        "multi_source_topic_share": sum(len(t["sources"]) > 1 for t in edition)
        / max(len(edition), 1),
    }


def run(items: list[dict], model: str, k: int, min_topic_size: int, out: Path) -> list[dict]:
    """One tracked run: data, parameters, metrics and artifacts all go to MLflow."""
    out.mkdir(parents=True, exist_ok=True)
    items_path = out / "items.json"
    items_path.write_text(json.dumps(items, ensure_ascii=False), encoding="utf-8")

    docs, kept = prepare_docs(items)
    matrix, vocab = vectorize(docs)
    if model == "bertopic":
        labels, names = bertopic_topics(docs, min_topic_size)
    else:
        labels, names = baseline_topics(matrix, vocab, k)
    edition = build_edition(labels, names, kept)
    metrics = topic_metrics(matrix, labels, edition)

    edition_path = out / "topics.json"
    edition_path.write_text(json.dumps(edition, ensure_ascii=False, indent=2), encoding="utf-8")

    # MLflow 3 dropped the file store; default to a local sqlite db (Postgres in production).
    mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI", f"sqlite:///{out / 'mlflow.db'}"))
    mlflow.set_experiment("topics")
    with mlflow.start_run():
        mlflow.log_params(
            {
                "model": model,
                "k": k if model == "baseline" else None,
                "min_topic_size": min_topic_size if model == "bertopic" else None,
                "embedding_model": EMBEDDING_MODEL if model == "bertopic" else None,
                "seed": SEED,
                "data_sha256": hashlib.sha256(items_path.read_bytes()).hexdigest(),
                "sources": len(Counter(i["source"] for i in kept)),
            }
        )
        mlflow.log_metrics(metrics)
        mlflow.log_artifact(str(items_path), "data")
        mlflow.log_artifact(str(edition_path))
    return edition


def main() -> None:
    parser = argparse.ArgumentParser(description="Group articles into the day's topics.")
    parser.add_argument("--input", type=Path, help="items JSON; if missing, collect now")
    parser.add_argument("--model", choices=["baseline", "bertopic"], default="baseline")
    parser.add_argument("--k", type=int, default=30, help="number of topics (baseline)")
    parser.add_argument("--min-topic-size", type=int, default=5, help="(bertopic)")
    parser.add_argument("--out", type=Path, default=Path("output"))
    args = parser.parse_args()

    if args.input:
        items = json.loads(args.input.read_text(encoding="utf-8"))
    else:
        from chiikawa.collect import collect_all
        from chiikawa.sources import load_sources

        items, _ = collect_all(load_sources())

    edition = run(items, args.model, args.k, args.min_topic_size, args.out)
    for t in edition[:10]:
        print(f"{len(t['sources']):2} sources  {len(t['articles']):3} articles  {t['topic']}")


if __name__ == "__main__":
    main()
