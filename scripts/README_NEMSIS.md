
# NEMSIS Processing

1) Place your state ASCII/CSV files in:
`data/nemsis_raw/`

2) Optional: Provide county centroids at:
`data/geo/geo_counties.csv` with columns:
`county_fips,latitude,longitude,population`

3) Run:
```bash
pip install pandas
python scripts/process_nemsis.py
```

Outputs:
- Per-state CSVs in `data/nemsis_states/`
- Merged `data/nemsis_cleaned.csv`
