from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class BaseResponse(BaseModel):
    data: Optional[Dict[str, Any]] = Field(
        default=None,
    )

    error_details: Optional[Any] = Field(
        default=None, description="Error details if the request is not success"
    )
