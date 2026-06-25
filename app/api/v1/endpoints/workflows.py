from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.workflow import WorkflowCreate, WorkflowResponse, WorkflowUpdate
from app.services.workflow import WorkflowService

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.post("", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
def create_workflow(payload: WorkflowCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> WorkflowResponse:
    workflow = WorkflowService(db).create(current_user.id, payload)
    return WorkflowResponse.model_validate(workflow)


@router.get("", response_model=list[WorkflowResponse])
def list_workflows(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> list[WorkflowResponse]:
    workflows = WorkflowService(db).list_for_owner(current_user.id)
    return [WorkflowResponse.model_validate(item) for item in workflows]


@router.get("/{workflow_id}", response_model=WorkflowResponse)
def get_workflow(workflow_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> WorkflowResponse:
    workflow = WorkflowService(db).get_owned(workflow_id, current_user.id)
    return WorkflowResponse.model_validate(workflow)


@router.put("/{workflow_id}", response_model=WorkflowResponse)
def update_workflow(workflow_id: int, payload: WorkflowUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> WorkflowResponse:
    service = WorkflowService(db)
    workflow = service.get_owned(workflow_id, current_user.id)
    updated = service.update(workflow, payload)
    return WorkflowResponse.model_validate(updated)


@router.delete("/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workflow(workflow_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> None:
    service = WorkflowService(db)
    workflow = service.get_owned(workflow_id, current_user.id)
    service.delete(workflow)
