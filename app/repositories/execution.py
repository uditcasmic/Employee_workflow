from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.execution import Execution, ExecutionLog, ExecutionStatus


class ExecutionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, execution: Execution) -> Execution:
        self.db.add(execution)
        self.db.commit()
        self.db.refresh(execution)
        return execution

    def save(self, execution: Execution) -> Execution:
        self.db.add(execution)
        self.db.commit()
        self.db.refresh(execution)
        return execution

    def get(self, execution_id: int) -> Execution | None:
        return self.db.get(Execution, execution_id)

    def list_for_workflow(self, workflow_id: int) -> list[Execution]:
        return list(self.db.scalars(select(Execution).where(Execution.workflow_id == workflow_id).order_by(Execution.id.desc())))

    def add_log(self, log: ExecutionLog) -> ExecutionLog:
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def list_logs(self, execution_id: int) -> list[ExecutionLog]:
        return list(self.db.scalars(select(ExecutionLog).where(ExecutionLog.execution_id == execution_id).order_by(ExecutionLog.id.asc())))

    def dashboard_stats(self) -> dict:
        total_workflows = self.db.scalar(select(func.count(func.distinct(Execution.workflow_id)))) or 0
        running = self.db.scalar(select(func.count()).select_from(Execution).where(Execution.status == ExecutionStatus.RUNNING)) or 0
        failed = self.db.scalar(select(func.count()).select_from(Execution).where(Execution.status == ExecutionStatus.FAILED)) or 0
        total_executions = self.db.scalar(select(func.count()).select_from(Execution)) or 0
        success = self.db.scalar(select(func.count()).select_from(Execution).where(Execution.status == ExecutionStatus.SUCCESS)) or 0
        avg_ms = 0.0
        completed = self.db.scalars(select(Execution).where(Execution.completed_at.is_not(None), Execution.started_at.is_not(None))).all()
        if completed:
            durations = [(item.completed_at - item.started_at).total_seconds() * 1000 for item in completed]
            avg_ms = sum(durations) / len(durations)
        success_rate = (success / total_executions * 100) if total_executions else 0.0
        return {
            "total_workflows": total_workflows,
            "running_workflows": running,
            "failed_workflows": failed,
            "success_rate": round(success_rate, 2),
            "average_execution_time_ms": round(avg_ms, 2),
        }
