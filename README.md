# Flight delay prediction

> Author: Mathias Pinon

---
### Introduction
 
    The goal of this project, it's to build a prediction and visulization app. This idea came form my wish to improve my skills in data science skills.
    Throughout the developement, I'll document every step I take.
---     

## Setup

```bash
python -m venv .venv
source .venv/Scripts/activate    # Windows (Git Bash)
source .venv/bin/activate        # macOS / Linux 
pip install -r requirements.txt
```

## First Step : Data 

Download the [2015 Flight Delays dataset](https://www.kaggle.com/datasets/usdot/flight-delays)
from Kaggle and unzip it into a 'data/' folder at the root of the project.
You'll find 'flights.csv', 'airlines.csv' and 'airports.csv' inside.

### Airport lookup table

Airport codes are IATA (ATL) for every month expect October, where they switch to 5-digit DOT codes (10397). The tables needed to reconcile them are not part of the Kaggle dataset.Download both from [TranStats](https://www.transtats.bts.gov/DL_SelectFields.aspx?gnoyr_VQ=FGJ&QO_fu146_anzr=b0-gvzr):

- `L_AIRPORT_ID.csv`(ORIGIN->OriginAirportID -> getLookupTable)
- `L_AIRPORT`(Origin->Origin->getLookupTable) 

Save both file into `data/reference`. They share an identiacal `description` column, which bridges the two codes systems. Both file are enconded in `latin-1`, not UTF-8.

--- 

## Secound Step :  Convert to parquet


`flights.csv` is 580 MB, which makes every read slow.

```bash
python scripts/to_parquet.py
```
This produces `data/flights.parquet' (~100 MB). Parquet is columnar, so as a query touching three column out of thirty-one only those three. Every step after this one reads the Parquet file, never the csv.

## Third Step: Data checks

Two checks run before any feature work, in `notebooks/01_eda.ipynb`.

**Base rate.** 18% of non-cancelled, non-diverted flights arrive more than
15 minutes late. A model always predicting "on time" would therefore score 82%
accuracy while being useless — which is why AUC is used instead of accuracy.

**Airport code format.** Looking at `MIN(ORIGIN_AIRPORT)` month by month shows
letter codes from January to September, a numeric code in October, then letter
codes again in November and December. October is entirely numeric: 486,165
flights, 306 distinct codes, no mixing.

This matters because the train/test split is temporal. Left uncorrected, the
codes in the test set would match nothing learned during training, and every
airport-based feature would break silently, without raising any error.

---

## Fourth Step: Map airport codes to IATA

```bash
python scripts/map_airports.py
```

This produces `data/flights_clean.parquet`, where every airport code is IATA.
Every step after this one reads this file.

The two lookup tables are joined on their `Description` column. Two issues
came up along the way:

- **Duplicate matches.** 4 of the 306 October codes match two IATA candidates
  (e.g. `10423` → `AUS` or `BSM`). The candidate that appears in the other
  months of the dataset is kept.
- **Renamed airport.** The lookup tables describe airports as they are today,
  not in 2015. One airport (`14027`, West Palm Beach) was renamed since, and
  now maps to a code absent from the 2015 data. It is mapped to `PBI` by hand.

Two tests guard the result: no numeric code remains, and the row count is
unchanged (a join producing duplicate rows would otherwise go unnoticed).

```bash
pytest
```
