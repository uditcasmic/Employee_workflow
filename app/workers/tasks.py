from app.core.database import SessionLocal
from app.models.workflow import Workflow
from app.services.execution import ExecutionService
from app.workers.celery_app import celery_app


@celery_app.task(name="app.workers.tasks.process_execution")
def process_execution(execution_id: int) -> None:
    db = SessionLocal()
    try:
        service = ExecutionService(db)
        execution = service.get_or_404(execution_id)
        workflow = db.get(Workflow, execution.workflow_id)
        if workflow is not None:
            service.run_execution(execution, workflow)
    finally:
        db.close()
