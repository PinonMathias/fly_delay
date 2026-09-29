import duckdb

RAW = "data/flights.parquet"
CLEAN = "data/flights_clean.parquet"


def test_no_numeric_airport_codes():
    n = duckdb.sql(f"""
        SELECT COUNT(*) FROM '{CLEAN}'
        WHERE regexp_full_match(ORIGIN_AIRPORT, '[0-9]+')
           OR regexp_full_match(DESTINATION_AIRPORT, '[0-9]+')
    """).fetchone()[0]
    assert n == 0


def test_row_count_unchanged():
    raw = duckdb.sql(f"SELECT COUNT(*) FROM '{RAW}'").fetchone()[0]
    clean = duckdb.sql(f"SELECT COUNT(*) FROM '{CLEAN}'").fetchone()[0]
    assert raw == clean