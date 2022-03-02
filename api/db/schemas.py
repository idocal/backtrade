from pydantic import BaseModel, Field


class Agent(BaseModel):
    id: str
    train_progress: float = Field(..., gt=0, lt=1)
    train_done: int = 0
    test_progress: float = Field(..., gt=0, lt=1)
    test_done: int = 0

    class Config:
        orm_mode = True
