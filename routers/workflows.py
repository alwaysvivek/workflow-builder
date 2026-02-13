from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from db.database import get_db, Workflow, WorkflowRun, WorkflowStepRun
from core.schemas import WorkflowCreate, WorkflowRead, WorkflowRunCreate, WorkflowRunRead, LLMStepOutput
from core.logging_config import get_logger
from services.llm import llm_service
from core.prompts import PROMPTS
import json

router = APIRouter(prefix="/workflows", tags=["workflows"])
logger = get_logger(__name__)

@router.post("", response_model=WorkflowRead)
def create_workflow(workflow: WorkflowCreate, db: Session = Depends(get_db)):
    db_workflow = Workflow(
        name=workflow.name,
        description=workflow.description,
        steps=[step.model_dump() for step in workflow.steps]
    )
    db.add(db_workflow)
    db.commit()
    db.refresh(db_workflow)
    logger.info(
        "Workflow created",
        extra={"workflow_id": str(db_workflow.id)},
    )
    return db_workflow

@router.post("/{workflow_id}/run", response_model=WorkflowRunRead)
def run_workflow_sync(workflow_id: str, run_request: WorkflowRunCreate, db: Session = Depends(get_db)):
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    db_run = WorkflowRun(
        workflow_id=workflow.id,
        input_text=run_request.input_text,
        status="running"
    )
    db.add(db_run)
    db.commit()
    db.refresh(db_run)
    logger.info(
        "Sync workflow run created",
        extra={"workflow_id": workflow_id, "run_id": str(db_run.id)},
    )
    return db_run

@router.post("/{workflow_id}/run_stream")
def run_workflow_stream(workflow_id: str, run_request: WorkflowRunCreate, request: Request, db: Session = Depends(get_db)):
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    # Create Run Record
    db_run = WorkflowRun(
        workflow_id=workflow.id,
        input_text=run_request.input_text,
        status="running"
    )
    db.add(db_run)
    db.commit()
    db.refresh(db_run)

    run_id = str(db_run.id)
    logger.info(
        "Streaming workflow run started",
        extra={"workflow_id": workflow_id, "run_id": run_id},
    )

    # Get API Key
    header_key = request.headers.get("x-groq-api-key")
    client = llm_service.get_client(header_key)

    # Sync generator — StreamingResponse will run this in a threadpool,
    # so blocking Groq SDK calls do NOT block the async event loop.
    def coherent_generator():
        if not client:
            logger.warning("API key missing for streaming run", extra={"run_id": run_id})
            yield json.dumps({"error": "API Key missing"}) + "\n"
            return

        current_input = run_request.input_text
        
        try:
            for index, step in enumerate(workflow.steps):
                action = step.get('action')
                yield json.dumps({"step": index + 1, "action": action, "status": "started"}) + "\n"
                
                prompt = PROMPTS.get(action).format(input_text=current_input)
                
                MAX_RETRIES = 1
                step_output = ""
                attempt = 0
                
                while attempt <= MAX_RETRIES:
                    # Sync stream call — safe inside sync generator
                    stream = client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model="llama-3.3-70b-versatile",
                        stream=True
                    )
                    
                    step_output = ""
                    for chunk in stream:
                        content = chunk.choices[0].delta.content
                        if content:
                            step_output += content
                            yield json.dumps({"step": index + 1, "chunk": content}) + "\n"
                    
                    # If output is non-empty, break out — success
                    if step_output.strip():
                        break
                    
                    # Empty output — retry with repair prompt
                    attempt += 1
                    if attempt <= MAX_RETRIES:
                        logger.warning(
                            "Empty LLM output, retrying with repair prompt",
                            extra={"run_id": run_id, "step": index + 1, "action": action, "attempt": attempt},
                        )
                        yield json.dumps({"step": index + 1, "status": "retrying", "reason": "empty output"}) + "\n"
                        prompt = (
                            f"The previous attempt returned an empty response. "
                            f"Please try again carefully.\n\n{prompt}"
                        )
                
                # Save Step (even if output is empty after retries)
                step_run = WorkflowStepRun(
                    workflow_run_id=db_run.id,
                    step_order=index + 1,
                    step_type=action,
                    output_text=step_output
                )
                db.add(step_run)
                db.commit()
                
                # Validate step output with Pydantic before passing to next step
                validated = LLMStepOutput(
                    content=step_output,
                    step_order=index + 1,
                    action=action,
                )

                logger.info(
                    "Step completed",
                    extra={"run_id": run_id, "step": index + 1, "action": action, "attempts": attempt + 1},
                )
                
                current_input = validated.content
                yield json.dumps({"step": index + 1, "status": "completed", "final_output": validated.content}) + "\n"
            
            # Complete Run
            db_run.status = "completed"
            db.commit()
            logger.info("Workflow run completed", extra={"run_id": run_id})
            
            yield json.dumps({"status": "workflow_completed", "run_id": run_id}) + "\n"
            
        except Exception as e:
            logger.error(
                "Workflow run failed",
                extra={"run_id": run_id},
                exc_info=True,
            )
            db_run.status = "failed"
            db.commit()
            yield json.dumps({"error": str(e)}) + "\n"

    return StreamingResponse(coherent_generator(), media_type="application/x-ndjson")

