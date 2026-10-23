import os
import re
import unicodedata

import duckdb
import pyarrow as pa
from dotenv import load_dotenv


def connect() -> duckdb.DuckDBPyConnection:
    """Open duckdb and give it the garage keys from .env"""
    load_dotenv()
    con = duckdb.connect()
    con.execute("INSTALL httpfs; Load httpfs;")
    con.execute(
        f"""
        CREATE SECRET garage (
        TYPE s3,
        KEY_ID '{os.environ["S3_ACCESS_KEY_ID"]}',
        SECRET '{os.environ["S3_SECRET_ACCESS_KEY"]}',
        ENDPOINT '{os.environ["S3_ENDPOINT"].removeprefix("http://")}',
        URL_STYLE 'path',
        USE_SSL false,
        REGION 'garage',
        )
        """
    )

    return con


def write_parquet(con: duckdb.DuckDBPyConnection, items: list[dict], path: str) -> None:
    """Write a list of items as one parquest file (zstd compressed)."""
    con.register("items", pa.Table.from_pylist(items))
    con.execute(f"COPY items TO '{path}' (FORMAT parquet, COMPRESSION zstd)")
    con.unregister("items")


def slug(name: str) -> str:
    """'La Dépêche du Midi' -> 'la-depeche-du-midi'."""
    ascii_name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", ascii_name.lower()).strip("-")


def bronze_path(source_name: str, run_id: str) -> str:
    """one file per source and per runm in the folder of the day."""
    return f"s3://bronze/items/ingest_date={run_id[:10]}/{slug(source_name)}__{run_id}.parquet"
