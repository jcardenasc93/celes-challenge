from functools import reduce
from typing import List

import pandas as pd

from app.constants import KEYS_CONSTANTS
from app.dataloader import Filter, load_data


class SalesService:
    def __init__(self, filters: List[Filter]) -> None:
        self._filters = filters

    def sales_by_period(self) -> float:
        filtered_data = self._filter_data(load_data())
        # Calcs the total per sale
        filtered_data["Total"] = filtered_data["Qty"] * filtered_data["CostAmount"]
        total: float = reduce(lambda x, y: x + y, filtered_data["Total"])
        return round(total, 2)

    def _filter_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """This method allows to apply the list of filters to a given data frame"""

        # In order to build a correct query the dates related values
        # must be parsed to a valid pandas query values
        for filter in self._filters:
            if filter.key == KEYS_CONSTANTS["Date"]:
                filter.value = f"@pd.to_datetime('{filter.value}').date()"
                continue
            filter.value = f"'{filter.value}'"

        query = " & ".join(
            [
                f"{filter.key} {filter.operator} {filter.value}"
                for filter in self._filters
            ]
        )
        filtered_data = data.query(query)
        return filtered_data
