import duckdb

duckdb.sql(
    """
    COPY (SELECT * FROM read_csv_auto('data/flights.csv'))
    TO 'data/flights.parquet' (FORMAT PARQUET, COMPRESSION ZSTD)
"""
)

print("done")