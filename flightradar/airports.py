import duckdb

RAW = "data/flights.parquet"
CLEAN = "data/flights_clean.parquet"
REF = "data/reference"


def build_clean_dataset(raw: str = RAW, clean: str = CLEAN) -> None:
    """Replace October's DOT airport codes with IATA codes and write a clean file."""
    duckdb.sql(f"""
        COPY (
            WITH known_iata AS (
                SELECT ORIGIN_AIRPORT AS code FROM '{raw}' WHERE MONTH <> 10
                UNION
                SELECT DESTINATION_AIRPORT FROM '{raw}' WHERE MONTH <> 10
            ),
            mapping AS (
                SELECT CAST(d.Code AS VARCHAR) AS dot_code, i.Code AS iata_code
                FROM read_csv('{REF}/L_AIRPORT_ID.csv', encoding='latin-1') d
                JOIN read_csv('{REF}/L_AIRPORT.csv', encoding='latin-1') i
                  ON d.Description = i.Description
                WHERE i.Code IN (SELECT code FROM known_iata)

                UNION ALL

                -- Airport renamed after 2015: the current lookup maps it to a
                -- new IATA code, while the 2015 data uses PBI.
                SELECT '14027', 'PBI'
            )
            SELECT f.* REPLACE (
                COALESCE(o.iata_code, f.ORIGIN_AIRPORT)      AS ORIGIN_AIRPORT,
                COALESCE(d.iata_code, f.DESTINATION_AIRPORT) AS DESTINATION_AIRPORT
            )
            FROM '{raw}' f
            LEFT JOIN mapping o ON f.ORIGIN_AIRPORT = o.dot_code
            LEFT JOIN mapping d ON f.DESTINATION_AIRPORT = d.dot_code
        ) TO '{clean}' (FORMAT PARQUET, COMPRESSION ZSTD)
    """)


if __name__ == "__main__":
    build_clean_dataset()
    print("done")