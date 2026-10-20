import csv
from dataclasses import dataclass


@dataclass(frozen=True)
class Source:
    name: str
    kind: str  # PQN or PQR
    rss_url: str | None
    sitemap_url: str | None


def load_sources(path: str = "sources.csv") -> list[Source]:
    """Read sources.csv and return the enabled sources."""
    with open(path, encoding="utf-8", newline="") as file:
        return [
            Source(
                name=row["nom"],
                kind=row["type"],
                rss_url=row["rss_url"] or None,
                sitemap_url=row["sitemap_url"] or None,
            )
            for row in csv.DictReader(file)
            if row["enabled"] == "yes"
        ]
