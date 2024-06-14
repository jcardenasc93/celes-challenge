from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from typing_extensions import Self

from app.api.auth import validate_token
from app.config import get_logger
from app.constants import FILTER_OPERATORS, KEYS_CONSTANTS
from app.dataloader import Filter
from app.schemas.sales_response import SalesPeriodSchema, SalesTotalAvgSchema
from app.services.sales import SalesService

router = APIRouter(
    prefix="/sales", tags=["sales"], dependencies=[Depends(validate_token)]
)


def keys_validator(key_employee, key_product, key_store):
    if any([key_employee, key_store, key_product]) is False:
        get_logger().warning("Request received without key values")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_msg": "At least one key must be included in the query params"
            },
        )


class FilterBuilder:
    def __init__(self) -> None:
        self.filters: List[Filter] = []

    def with_employee_key(self, key_employee: str) -> Self:
        employee_filter = Filter(
            key=KEYS_CONSTANTS["Employee"],
            operator=FILTER_OPERATORS["eq"],
            value=key_employee,
        )
        self.filters.append(employee_filter)
        return self

    def with_product_key(self, key_product: str) -> Self:
        product_filter = Filter(
            key=KEYS_CONSTANTS["Product"],
            operator=FILTER_OPERATORS["eq"],
            value=key_product,
        )
        self.filters.append(product_filter)
        return self

    def with_store_key(self, key_store: str) -> Self:
        store_filter = Filter(
            key=KEYS_CONSTANTS["Store"],
            operator=FILTER_OPERATORS["eq"],
            value=key_store,
        )
        self.filters.append(store_filter)
        return self

    def add_filter(self, filter: Filter) -> Self:
        self.filters.append(filter)
        return self


@router.get(
    "/",
    summary="Retrieves total & average sales by [Employee, Product, Store]",
    status_code=status.HTTP_200_OK,
)
async def get_total_avg_sales(
    key_employee: Optional[str] = None,
    key_product: Optional[str] = None,
    key_store: Optional[str] = None,
) -> SalesTotalAvgSchema:
    """Fetchs and returns total and average sales.
    At least one of the following query keys should be used as query param:
    - KeyEmployee: Filter by employee key
    - KeyProduct: Filter by product key
    - KeyStore: Filter by store"""
    keys_validator(key_employee, key_product, key_store)
    # Builds proper filters
    filter_builder = FilterBuilder()
    if key_employee:
        filter_builder.with_employee_key(key_employee)

    if key_product:
        filter_builder.with_product_key(key_product)

    if key_store:
        filter_builder.with_store_key(key_store)

    service = SalesService(filters=filter_builder.filters)
    try:
        total_avg = service.total_avg_sales()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
    return SalesTotalAvgSchema(data=total_avg)


@router.get(
    "/period",
    summary="Retrieves sales in a given period",
    status_code=status.HTTP_200_OK,
)
async def get_sales_by_period(
    start_period: date,
    end_period: date,
    key_employee: Optional[str] = None,
    key_product: Optional[str] = None,
    key_store: Optional[str] = None,
) -> SalesPeriodSchema:
    """Fetchs and returns sales in a given period.
    - start_period & end_period should be given in format YYYY-MM-DD to be valid\n
    At least one of the following query keys should be used as query param:
    - KeyEmployee: Filter by employee key
    - KeyProduct: Filter by product key
    - KeyStore: Filter by store"""
    keys_validator(key_employee, key_product, key_store)
    # Builds proper filters
    filter_builder = FilterBuilder()
    start_period_filter = Filter(
        key=KEYS_CONSTANTS["Date"], operator=FILTER_OPERATORS["gte"], value=start_period
    )
    end_period_filter = Filter(
        key=KEYS_CONSTANTS["Date"], operator=FILTER_OPERATORS["lte"], value=end_period
    )
    filter_builder.add_filter(start_period_filter).add_filter(end_period_filter)

    if key_employee:
        filter_builder.with_employee_key(key_employee)

    if key_product:
        filter_builder.with_product_key(key_product)

    if key_store:
        filter_builder.with_store_key(key_store)

    service = SalesService(filters=filter_builder.filters)
    try:
        total_sales = service.sales_by_period()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
    return SalesPeriodSchema(data={"amount": total_sales})
