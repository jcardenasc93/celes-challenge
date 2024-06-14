import pandas as pd
import pytest

from app.constants import KEYS_CONSTANTS
from app.schemas.sales_response import TotalAvgSales


@pytest.fixture
def sales_dates():
    dates = ["2024-01-01", "2024-01-01", "2024-01-02", "2024-01-03", "2024-01-03"]
    return dates


@pytest.fixture
def sales_qtys():
    return [10, 5, 2, 1, 3]


@pytest.fixture
def sales_costs():
    return [2500.00, 9730.00, 15750.99, 1237.0, 3420.10]


@pytest.fixture
def employees():
    return ["E1", "E1", "E2", "E3", "E3"]


@pytest.fixture
def products():
    return ["P1", "P2", "P3", "P4", "P5"]


@pytest.fixture
def stores():
    return ["S1", "S1", "S1", "S2", "S2"]


@pytest.fixture
def total_sales_period_employee(sales_costs, sales_qtys) -> float:
    total = (sales_costs[3] * sales_qtys[3]) + (sales_costs[4] * sales_qtys[4])
    return round(total, 2)


@pytest.fixture
def total_avg_sales_store(sales_costs, sales_qtys) -> TotalAvgSales:
    total = (sales_costs[3] * sales_qtys[3]) + (sales_costs[4] * sales_qtys[4])
    avg = total / 2  # Two sales were done in S2
    return TotalAvgSales(total=total, average=avg)


@pytest.fixture
def testing_data(
    sales_dates, sales_qtys, sales_costs, employees, products, stores
) -> pd.DataFrame:
    data = {
        "Index": [i for i in range(1, 6)],
        "Qty": sales_qtys,
        "CostAmount": sales_costs,
        KEYS_CONSTANTS["Date"]: sales_dates,
        KEYS_CONSTANTS["Employee"]: employees,
        KEYS_CONSTANTS["Product"]: products,
        KEYS_CONSTANTS["Store"]: stores,
    }
    df = pd.DataFrame(data, index=data["Index"])
    df[KEYS_CONSTANTS["Date"]] = pd.to_datetime(df[KEYS_CONSTANTS["Date"]])
    return df
