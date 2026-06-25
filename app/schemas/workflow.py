from datetime import datetime

from pydantic import BaseModel, Field


class WorkflowStep(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    action: str = Field(min_length=1, max_length=255)
    config: dict = Field(default_factory=dict)


class WorkflowCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    steps: list[WorkflowStep]


class WorkflowUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    steps: list[WorkflowStep] | None = None


class WorkflowResponse(BaseModel):
    id: int
    name: str
    description: str | None
    definition: dict
    owner_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
