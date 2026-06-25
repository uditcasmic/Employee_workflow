from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.workflow import Workflow
from app.repositories.workflow import WorkflowRepository
from app.schemas.workflow import WorkflowCreate, WorkflowUpdate


class WorkflowService:
    def __init__(self, db: Session) -> None:
        self.repo = WorkflowRepository(db)
        self.db = db

    def create(self, owner_id: int, payload: WorkflowCreate) -> Workflow:
        workflow = Workflow(
            name=payload.name,
            description=payload.description,
            definition={"steps": [step.model_dump() for step in payload.steps]},
            owner_id=owner_id,
        )
        return self.repo.create(workflow)

    def list_for_owner(self, owner_id: int) -> list[Workflow]:
        return self.repo.list_for_owner(owner_id)

    def get_owned(self, workflow_id: int, owner_id: int) -> Workflow:
        workflow = self.repo.get_for_owner(workflow_id, owner_id)
        if not workflow:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
        return workflow

    def update(self, workflow: Workflow, payload: WorkflowUpdate) -> Workflow:
        updates = payload.model_dump(exclude_unset=True)
        if "name" in updates:
            workflow.name = updates["name"]
        if "description" in updates:
            workflow.description = updates["description"]
        if "steps" in updates:
            workflow.definition = {"steps": [step for step in updates["steps"]]}
        self.db.add(workflow)
        self.db.commit()
        self.db.refresh(workflow)
        return workflow

    def delete(self, workflow: Workflow) -> None:
        self.repo.delete(workflow)
