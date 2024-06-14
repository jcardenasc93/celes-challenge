from typing import Dict, Optional

from pydantic import BaseModel
from pydantic.fields import Field

from app.schemas.base_response import BaseResponse


class SalesPeriodSchema(BaseResponse):
    data: Optional[Dict[str, float]] = Field(
        default=None,
        description="Sales amount",
        examples=[{"amount": 147800.00}],
    )


class TotalAvgSales(BaseModel):
    total: float = Field(description="Total sales", examples=[125698.34])
    average: float = Field(description="Average sales", examples=[65632.20])


class SalesTotalAvgSchema(BaseResponse):
    data: Optional[TotalAvgSales] = Field(
        description="Includes total and average sales",
        examples=[
            {
                "total": 125698.34,
                "average": 65632.20,
            }
        ],
        default=None,
    )
