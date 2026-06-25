from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.execution import DashboardStats, ExecutionCreate, ExecutionLogResponse, ExecutionResponse
from app.services.execution import ExecutionService
from app.services.workflow import WorkflowService
from app.workers.tasks import process_execution

router = APIRouter(prefix="/executions", tags=["executions"])


@router.post("/workflow/{workflow_id}", response_model=ExecutionResponse)
def execute_workflow(workflow_id: int, payload: ExecutionCreate, sync: bool = Query(default=False), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> ExecutionResponse:
    workflow = WorkflowService(db).get_owned(workflow_id, current_user.id)
    service = ExecutionService(db)
    execution = service.start_execution(workflow, current_user.id, payload.input_payload)
    if sync:
        execution = service.run_execution(execution, workflow)
    else:
        process_execution.delay(execution.id)
    return ExecutionResponse.model_validate(execution)


@router.get("/{execution_id}", response_model=ExecutionResponse)
def get_execution(execution_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> ExecutionResponse:
    execution = ExecutionService(db).get_or_404(execution_id)
    if execution.initiated_by_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return ExecutionResponse.model_validate(execution)


@router.get("/{execution_id}/logs", response_model=list[ExecutionLogResponse])
def get_execution_logs(execution_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> list[ExecutionLogResponse]:
    service = ExecutionService(db)
    execution = service.get_or_404(execution_id)
    if execution.initiated_by_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    logs = service.repo.list_logs(execution_id)
    return [ExecutionLogResponse.model_validate(item) for item in logs]


@router.post("/{execution_id}/retry", response_model=ExecutionResponse)
def retry_execution(execution_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> ExecutionResponse:
    service = ExecutionService(db)
    execution = service.get_or_404(execution_id)
    if execution.initiated_by_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    updated = service.retry(execution)
    process_execution.delay(updated.id)
    return ExecutionResponse.model_validate(updated)


@router.post("/{execution_id}/cancel", response_model=ExecutionResponse)
def cancel_execution(execution_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> ExecutionResponse:
    service = ExecutionService(db)
    execution = service.get_or_404(execution_id)
    if execution.initiated_by_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    updated = service.cancel(execution)
    return ExecutionResponse.model_validate(updated)


@router.get("/workflow/{workflow_id}/history", response_model=list[ExecutionResponse])
def execution_history(workflow_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> list[ExecutionResponse]:
    workflow = WorkflowService(db).get_owned(workflow_id, current_user.id)
    items = ExecutionService(db).repo.list_for_workflow(workflow.id)
    return [ExecutionResponse.model_validate(item) for item in items]


@router.get("/dashboard/stats", response_model=DashboardStats)
def dashboard_stats(db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> DashboardStats:
    stats = ExecutionService(db).repo.dashboard_stats()
    return DashboardStats(**stats)
