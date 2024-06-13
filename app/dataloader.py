import pandas as pd
from functools import lru_cache

@lru_cache()
def load_data() -> pd.DataFrame:
    """Loads data from parquet files and caches it"""
    data = pd.read_parquet("data/", engine="pyarrow")
    return data
