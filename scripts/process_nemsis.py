
#!/usr/bin/env python3
# Process NEMSIS ASCII or CSV state files into clean CSVs for the dashboard.

import os
import re
import sys
import json
import glob
import pandas as pd
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
DATA_DIR = BASE / "data"
RAW_DIR = DATA_DIR / "nemsis_raw"
OUT_STATES_DIR = DATA_DIR / "nemsis_states"
GEO_PATH = DATA_DIR / "geo" / "geo_counties.csv"
CONFIG_PATH = Path(__file__).resolve().with_name("config_nemsis.json")

with open(CONFIG_PATH, "r") as f:
    CFG = json.load(f)

MIN_DATE = pd.to_datetime(CFG["min_date"]).tz_localize(None)

def _print(msg: str):
    print(f"[process_nemsis] {msg}")

def _find_column(df, candidates):
    lower_cols = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand.lower() in lower_cols:
            return lower_cols[cand.lower()]
    return None

def _open_raw_file(path: Path):
    try:
        df = pd.read_csv(path, low_memory=False)
        return df
    except Exception as e:
        _print(f"CSV read failed for {path.name}: {e}")
        return None

def _coerce_datetime(s):
    if pd.isna(s):
        return pd.NaT
    try:
        return pd.to_datetime(s, errors="coerce", utc=True).tz_convert(None)
    except Exception:
        return pd.NaT

def _first_nonnull_col(df, candidates):
    lower_cols = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand in df.columns:
            return cand
        if cand.lower() in lower_cols:
            return lower_cols[cand.lower()]
        matches = [lower_cols[c] for c in lower_cols if c.endswith(cand.lower()) or c.split('.')[-1] == cand.lower()]
        if matches:
            return matches[0]
    return None

def _map_columns(raw_df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame()
    for clean_name, candidates in CFG["element_ids"].items():
        col = _first_nonnull_col(raw_df, candidates)
        if col is not None:
            out[clean_name] = raw_df[col]
        else:
            out[clean_name] = pd.NA
    return out

def _postprocess(df: pd.DataFrame, state_code: str) -> pd.DataFrame:
    df["state"] = df.get("state").fillna(state_code).replace({"": state_code, None: state_code})
    for c in ["dispatch_ts","enroute_ts","onscene_ts"]:
        df[c] = df[c].apply(_coerce_datetime)
    df["incident_date"] = df["dispatch_ts"].dt.date
    df["response_time_sec"] = (df["onscene_ts"] - df["dispatch_ts"]).dt.total_seconds()
    df["patient_age"] = pd.to_numeric(df.get("patient_age"), errors="coerce")
    df["transported"] = df.get("transported").astype(str).str.strip().str.lower().isin(["yes","true","y","1"])
    if "priority" in df.columns:
        df["priority"] = df["priority"].astype(str).str.upper().str.extract(r"([A-Z0-9]+)", expand=False)
    if "urbanicity" in df.columns:
        df["urbanicity"] = df["urbanicity"].astype(str).str.title()
    df["day_of_week"] = df["dispatch_ts"].dt.day_name()
    df["hour_of_day"] = df["dispatch_ts"].dt.hour
    df = df.dropna(subset=["dispatch_ts","onscene_ts","response_time_sec"])
    df = df[(df["response_time_sec"] >= 0) & (df["response_time_sec"] <= 3600)]
    df = df[df["dispatch_ts"] >= MIN_DATE]
    if "county_fips" in df.columns:
        df["county_fips"] = df["county_fips"].astype(str).str.extract(r"(\d{5})", expand=False)
    if GEO_PATH.exists():
        try:
            geo = pd.read_csv(GEO_PATH, dtype={"county_fips": str})
            df = df.merge(geo, on="county_fips", how="left")
        except Exception as e:
            _print(f"Geo join skipped: {e}")
    return df

def process_file(path: Path) -> pd.DataFrame:
    state_guess = path.name.split("_")[0].upper()[:2]
    _print(f"Processing {path.name} (state guess: {state_guess})")
    raw = _open_raw_file(path)
    if raw is None:
        raise RuntimeError(f"Could not read {path.name} as CSV. If this is fixed-width ASCII, convert to CSV first or provide a separate loader.")
    mapped = _map_columns(raw)
    cleaned = _postprocess(mapped, state_guess)
    keep = [c for c in CFG["keep_columns"] if c in cleaned.columns]
    cleaned = cleaned[keep]
    return cleaned

def main():
    os.makedirs(OUT_STATES_DIR, exist_ok=True)
    files = sorted(glob.glob(str(RAW_DIR / "*.*")))
    if not files:
        _print(f"No files found in {RAW_DIR}. Place your state files there and re-run.")
        sys.exit(1)

    all_rows = []
    for fp in files:
        try:
            df = process_file(Path(fp))
            if df.empty:
                _print(f"WARNING: No valid rows after filtering in {fp}")
                continue
            state_code = df["state"].dropna().astype(str).str.upper().iloc[0] if not df.empty else Path(fp).name[:2].upper()
            out_path = OUT_STATES_DIR / f"nemsis_{state_code}.csv"
            df.to_csv(out_path, index=False)
            _print(f"Saved {len(df):,} rows to {out_path.name}")
            all_rows.append(df)
        except Exception as e:
            _print(f"ERROR processing {fp}: {e}")

    if not all_rows:
        _print("No state outputs generated. Exiting.")
        sys.exit(1)

    merged = pd.concat(all_rows, ignore_index=True)
    merged_out = DATA_DIR / "nemsis_cleaned.csv"
    merged.to_csv(merged_out, index=False)
    _print(f"Merged {len(merged):,} rows across {len(all_rows)} files → {merged_out.name}")

if __name__ == "__main__":
    main()
