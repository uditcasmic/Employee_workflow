from datetime import datetime

from pydantic import BaseModel, Field

from app.models.execution import ExecutionStatus, StepStatus


class ExecutionCreate(BaseModel):
    input_payload: dict = Field(default_factory=dict)


class ExecutionResponse(BaseModel):
    id: int
    workflow_id: int
    initiated_by_id: int
    status: ExecutionStatus
    current_step: str | None
    input_payload: dict | None
    result_payload: dict | None
    error_message: str | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ExecutionLogResponse(BaseModel):
    id: int
    execution_id: int
    step_name: str
    status: StepStatus
    message: str | None
    duration_ms: int | None
    retry_count: int
    timestamp: datetime

    model_config = {"from_attributes": True}


class DashboardStats(BaseModel):
    total_workflows: int
    running_workflows: int
    failed_workflows: int
    success_rate: float
    average_execution_time_ms: float
