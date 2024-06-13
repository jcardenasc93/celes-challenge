from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError

from app.config import get_logger
from app.constants import FILTER_OPERATORS, KEYS_CONSTANTS
from app.dataloader import Filter
from app.schemas.sales_response import SalesSchema
from app.services.sales import SalesService

router = APIRouter(
    prefix="/sales",
    tags=["sales"],
)


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
) -> SalesSchema:
    """Fetchs and returns sales in a given period.
    - start_period & end_period should be given in format YYYY-MM-DD to be valid\n
    At least one of the following query keys should be used as query param:
    - KeyEmployee: Filter by employee key
    - KeyProduct: Filter by product key
    - KeyStore: Filter by store"""

    # Builds proper filters
    filters: List[Filter] = []
    start_period_filter = Filter(
        key=KEYS_CONSTANTS["Date"], operator=FILTER_OPERATORS["gte"], value=start_period
    )
    end_period_filter = Filter(
        key=KEYS_CONSTANTS["Date"], operator=FILTER_OPERATORS["lte"], value=end_period
    )
    filters.append(start_period_filter)
    filters.append(end_period_filter)

    if any([key_employee, key_store, key_product]) is False:
        get_logger().warning("Request received without key values")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_msg": "At least one key must be included in the query params"
            },
        )

    if key_employee:
        employee_filter = Filter(
            key=KEYS_CONSTANTS["Employee"],
            operator=FILTER_OPERATORS["eq"],
            value=key_employee,
        )
        filters.append(employee_filter)

    if key_product:
        product_filter = Filter(
            key=KEYS_CONSTANTS["Product"],
            operator=FILTER_OPERATORS["eq"],
            value=key_product,
        )
        filters.append(product_filter)

    if key_store:
        store_filter = Filter(
            key=KEYS_CONSTANTS["Store"],
            operator=FILTER_OPERATORS["eq"],
            value=key_store,
        )
        filters.append(store_filter)

    service = SalesService(filters=filters)
    total_sales = service.sales_by_period()

    return SalesSchema(data={"amount": total_sales})
