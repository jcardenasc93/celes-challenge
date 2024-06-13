from datetime import date
from typing import List

import pytest

from app.constants import FILTER_OPERATORS, KEYS_CONSTANTS
from app.dataloader import Filter
from app.services.sales import SalesService


@pytest.fixture
def period_filters(sales_dates) -> List[Filter]:
    start_period_filter = Filter(
        key=KEYS_CONSTANTS["Date"],
        operator=FILTER_OPERATORS["gte"],
        value=sales_dates[2],
    )
    end_period_filter = Filter(
        key=KEYS_CONSTANTS["Date"],
        operator=FILTER_OPERATORS["lte"],
        value=sales_dates[-1],
    )
    return [start_period_filter, end_period_filter]


@pytest.fixture
def employee_filter(employees) -> Filter:
    return Filter(
        key=KEYS_CONSTANTS["Employee"],
        operator=FILTER_OPERATORS["eq"],
        value=employees[-1],
    )


@pytest.fixture
def product_filter(products) -> Filter:
    return Filter(
        key=KEYS_CONSTANTS["Product"],
        operator=FILTER_OPERATORS["eq"],
        value=products[-1],
    )


@pytest.fixture
def store_filter(stores) -> Filter:
    return Filter(
        key=KEYS_CONSTANTS["Store"],
        operator=FILTER_OPERATORS["eq"],
        value=stores[-1],
    )


@pytest.fixture
def sales_service_period(period_filters) -> SalesService:
    return SalesService(filters=period_filters)


@pytest.fixture
def sales_service_employee_key(period_filters, employee_filter) -> SalesService:
    filters = []
    filters.extend(period_filters)
    filters.append(employee_filter)
    return SalesService(filters=filters)


@pytest.fixture
def sales_service_product_key(period_filters, product_filter) -> SalesService:
    filters = []
    filters.extend(period_filters)
    filters.append(product_filter)
    return SalesService(filters=filters)


@pytest.fixture
def sales_service_store_key(period_filters, store_filter) -> SalesService:
    filters = []
    filters.extend(period_filters)
    filters.append(store_filter)
    return SalesService(filters=filters)
