from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.workflow import Workflow


class WorkflowRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, workflow: Workflow) -> Workflow:
        self.db.add(workflow)
        self.db.commit()
        self.db.refresh(workflow)
        return workflow

    def list_for_owner(self, owner_id: int) -> list[Workflow]:
        return list(self.db.scalars(select(Workflow).where(Workflow.owner_id == owner_id).order_by(Workflow.id.desc())))

    def get_for_owner(self, workflow_id: int, owner_id: int) -> Workflow | None:
        return self.db.scalar(select(Workflow).where(Workflow.id == workflow_id, Workflow.owner_id == owner_id))

    def delete(self, workflow: Workflow) -> None:
        self.db.delete(workflow)
        self.db.commit()
