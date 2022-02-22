from pydantic import BaseModel, Field


class Agent(BaseModel):
    id: str
    training_progress: float = Field(..., gt=0, lt=1)
    training_completed: bool = False
    testing_progress: float = Field(..., gt=0, lt=1)
    testing_completed: bool = False

    class Config:
        orm_mode = True