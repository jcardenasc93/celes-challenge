from typing import Dict, Optional

from pydantic.fields import Field

from app.schemas.base_response import BaseResponse


class SalesSchema(BaseResponse):
    data: Optional[Dict[str, float]] = Field(
        default=None,
        description="Sales amount",
        examples=[{"amount": 147800.00}],
    )
