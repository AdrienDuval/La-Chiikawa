from chiikawa.topics import baseline_topics, build_edition, prepare_docs, topic_metrics, vectorize


def test_prepare_docs_drops_duplicates_and_empty_titles():
    items = [
        {"title": "A", "link": "https://x.fr/a?utm_source=rss", "excerpt": ""},
        {"title": "A again", "link": "https://x.fr/a", "excerpt": ""},  # same clean URL
        {"title": "", "link": "https://x.fr/b", "excerpt": ""},  # no title
        {"title": "B", "link": "https://x.fr/b", "excerpt": "<b>hi</b>"},
    ]
    docs, kept = prepare_docs(items)
    assert [k["link"] for k in kept] == ["https://x.fr/a", "https://x.fr/b"]
    assert docs[1] == "B. hi"  # HTML stripped from excerpt


def test_build_edition_groups_and_sorts_by_coverage():
    labels = [0, 0, 1, -1]
    names = {0: "foot", 1: "météo"}
    items = [
        {"title": "match", "source": "Le Monde", "link": "l1"},
        {"title": "score", "source": "Le Figaro", "link": "l2"},
        {"title": "pluie", "source": "Le Monde", "link": "l3"},
        {"title": "bruit", "source": "Le Monde", "link": "l4"},  # outlier, dropped
    ]
    edition = build_edition(labels, names, items)
    assert [t["topic"] for t in edition] == ["foot", "météo"]  # foot has 2 sources, comes first
    assert edition[0]["sources"] == ["Le Figaro", "Le Monde"]
    assert sum(len(t["articles"]) for t in edition) == 3


def test_baseline_clusters_separable_titles():
    docs = [
        "élection président vote",
        "vote scrutin président",
        "football match victoire",
        "match football score",
    ] * 2
    matrix, vocab = vectorize(docs)
    labels, names = baseline_topics(matrix, vocab, k=2)
    # the two politics docs land together, apart from the two football docs
    assert labels[0] == labels[1]
    assert labels[2] == labels[3]
    assert labels[0] != labels[2]
    assert len(names) == 2


def test_metrics_shape():
    docs = ["vote président", "vote scrutin", "match football", "score match"]
    matrix, _ = vectorize(docs)
    labels = [0, 0, 1, 1]
    edition = build_edition(
        labels, {0: "a", 1: "b"}, [{"source": s, "title": "t", "link": "l"} for s in "wxyz"]
    )
    m = topic_metrics(matrix, labels, edition)
    assert m["n_docs"] == 4
    assert m["n_topics"] == 2
    assert m["outlier_share"] == 0.0
