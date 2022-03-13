from .agent import KEY_SIZE
from data.providers import VALID_PROVIDERS, VALID_INTERVALS

from pydantic import BaseModel, Field, validator
from datetime import date, datetime


class RunRequest(BaseModel):
    provider: VALID_PROVIDERS = Field(..., description="The name of the data provider")
    agent_id: str = Field(
        ..., min_length=2 * KEY_SIZE, max_length=2 * KEY_SIZE, description="Agent ID"
    )
    interval: VALID_INTERVALS = Field(
        ..., description="Enter the interval for the candles"
    )

    start: date = Field(..., description="Date in %Y-%m-%d format")
    end: date = Field(..., description="Date in %Y-%m-%d format")
    initial_amount: float = Field(..., ge=0)
    commission: float = Field(..., ge=0, lt=1)

    @validator("end")
    def ensure_end_later_than_start(cls, end, values):
        assert end > values["start"], ValueError(
            "End date must be greater than start date"
        )
        assert end <= datetime.today().date(), ValueError(
            "End date cannot be greater than today"
        )
        return end
