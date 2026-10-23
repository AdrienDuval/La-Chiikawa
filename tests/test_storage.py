from chiikawa.storage import bronze_path, slug


def test_slug_removes_accents_and_spaces():
    assert slug("La Dépêche du Midi") == "la-depeche-du-midi"
    assert slug("L'Humanité") == "l-humanite"


def test_bronze_path_uses_day_folder_and_run_id():
    assert (
        bronze_path("Le Monde", "2026-10-23T14")
        == "s3://bronze/items/ingest_date=2026-10-23/le-monde__2026-10-23T14.parquet"
    )
