from typing import Any, Optional

from data.providers import VALID_PROVIDERS, VALID_INTERVALS

from pydantic import BaseModel, Field, validator
from datetime import date, datetime

KEY_SIZE = 32


class RunRequest(BaseModel):
    provider: VALID_PROVIDERS = Field(..., description="The name of the data provider")
    agent_id: str = Field(
        ..., min_length=2 * KEY_SIZE, max_length=2 * KEY_SIZE, description="Agent ID"
    )
    interval: VALID_INTERVALS = Field(
        ..., description="Enter the interval for the candles"
    )

    start_date: date = Field(..., description="Date in %Y-%m-%d format")
    end_date: date = Field(..., description="Date in %Y-%m-%d format")
    initial_amount: float = Field(
        ..., description=f"Enter initial amount of cash", ge=0
    )
    commission: float = Field(
        0, ge=0, lt=1, description=f"Enter commission per transaction"
    )

    @validator("end_date")
    def ensure_end_later_than_start(cls, end_date, values):
        assert end_date > values["start_date"], ValueError(
            "End date must be greater than start_time date"
        )
        assert end_date <= datetime.today().date(), ValueError(
            "End date cannot be greater than today"
        )
        return end_date


class AgentUpdateRequest(BaseModel):
    agent_id: str = Field(
        ..., min_length=2 * KEY_SIZE, max_length=2 * KEY_SIZE, description="Agent ID"
    )
    updates: dict = Field(dict())
