import pandas as pd
from functools import lru_cache

@lru_cache(maxsize=8)
def load_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=[c for c in ['date','timestamp'] if c in pd.read_csv(path, nrows=1).columns])
    return df
