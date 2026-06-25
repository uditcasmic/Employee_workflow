from datetime import UTC, datetime
from time import perf_counter

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.execution import Execution, ExecutionLog, ExecutionStatus, StepStatus
from app.models.workflow import Workflow
from app.repositories.execution import ExecutionRepository


class ExecutionService:
    def __init__(self, db: Session) -> None:
        self.repo = ExecutionRepository(db)
        self.db = db

    def start_execution(self, workflow: Workflow, user_id: int, input_payload: dict) -> Execution:
        execution = Execution(
            workflow_id=workflow.id,
            initiated_by_id=user_id,
            input_payload=input_payload,
            status=ExecutionStatus.PENDING,
        )
        return self.repo.create(execution)

    def get_or_404(self, execution_id: int) -> Execution:
        execution = self.repo.get(execution_id)
        if not execution:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Execution not found")
        return execution

    def cancel(self, execution: Execution) -> Execution:
        if execution.status in {ExecutionStatus.SUCCESS, ExecutionStatus.FAILED, ExecutionStatus.CANCELLED}:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Execution already finished")
        execution.status = ExecutionStatus.CANCELLED
        execution.completed_at = datetime.now(UTC)
        return self.repo.save(execution)

    def retry(self, execution: Execution) -> Execution:
        execution.status = ExecutionStatus.PENDING
        execution.error_message = None
        execution.result_payload = None
        execution.current_step = None
        execution.started_at = None
        execution.completed_at = None
        return self.repo.save(execution)

    def run_execution(self, execution: Execution, workflow: Workflow) -> Execution:
        execution.status = ExecutionStatus.RUNNING
        execution.started_at = datetime.now(UTC)
        self.repo.save(execution)

        payload = execution.input_payload or {}
        output = dict(payload)

        try:
            for step in workflow.definition.get("steps", []):
                step_name = step["name"]
                execution.current_step = step_name
                self.repo.save(execution)
                started = perf_counter()
                self.repo.add_log(ExecutionLog(execution_id=execution.id, step_name=step_name, status=StepStatus.RUNNING, message=f"Step {step_name} started"))
                output = self._execute_step(step, output)
                duration_ms = int((perf_counter() - started) * 1000)
                self.repo.add_log(ExecutionLog(execution_id=execution.id, step_name=step_name, status=StepStatus.SUCCESS, message=f"Step {step_name} completed", duration_ms=duration_ms))

            execution.status = ExecutionStatus.SUCCESS
            execution.result_payload = output
            execution.completed_at = datetime.now(UTC)
            execution.current_step = None
            return self.repo.save(execution)
        except Exception as exc:
            self.repo.add_log(ExecutionLog(execution_id=execution.id, step_name=execution.current_step or "unknown", status=StepStatus.FAILED, message=str(exc)))
            execution.status = ExecutionStatus.FAILED
            execution.error_message = str(exc)
            execution.completed_at = datetime.now(UTC)
            return self.repo.save(execution)

    def _execute_step(self, step: dict, payload: dict) -> dict:
        action = step["action"]
        step_name = step["name"]
        updated = dict(payload)
        updated.setdefault("executed_steps", []).append(step_name)

        if action == "validate":
            updated["validated"] = True
        elif action == "create_user":
            updated["user_created"] = True
        elif action == "send_email":
            updated["email_sent"] = True
        elif action == "generate_pdf":
            updated["document_generated"] = True
        elif action == "parse_file":
            updated["parsed"] = True
        elif action == "save_records":
            updated["saved"] = True
        elif action == "generate_report":
            updated["report_generated"] = True
        else:
            updated[f"action_{action}"] = "completed"
        return updated
