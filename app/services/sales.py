from typing import List

import pandas as pd

from app.constants import KEYS_CONSTANTS
from app.dataloader import Filter, load_data
from app.schemas.sales_response import TotalAvgSales


class SalesService:
    def __init__(self, filters: List[Filter]) -> None:
        self._filters = filters

    def sales_by_period(self) -> float:
        """Calcs sales in a period"""
        filtered_data = self._filter_data(load_data())
        if filtered_data.empty:
            return 0.0
        return self._calc_total(filtered_data)

    def total_avg_sales(self) -> TotalAvgSales:
        """Calcs total and average sales"""
        filtered_data = self._filter_data(load_data())
        if filtered_data.empty:
            return TotalAvgSales(total=0.0, average=0.0)
        total = self._calc_total(filtered_data)
        avg = total / len(filtered_data.index)
        return TotalAvgSales(total=total, average=avg)

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

    @staticmethod
    def _calc_total(data: pd.DataFrame) -> float:
        total_df = (
            pd.DataFrame()
        )  # Creates new dataframe to avoiding dataframe copy warning
        total_df["Total"] = data["Qty"] * data["CostAmount"]
        total = total_df["Total"].sum()
        return round(total, 2)
