from dataclasses import dataclass
from functools import lru_cache
from typing import Any, List

import pandas as pd


@lru_cache()
def load_data() -> pd.DataFrame:
    """Loads data from parquet files and caches it"""
    data = pd.read_parquet("data/", engine="pyarrow")
    return data


@dataclass
class Filter:
    key: str
    operator: str
    value: Any
