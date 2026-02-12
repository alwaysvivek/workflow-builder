from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from core.prompts import ActionType

class WorkflowStep(BaseModel):
    action: ActionType
    params: Optional[dict] = Field(default_factory=dict)

class WorkflowBase(BaseModel):
    name: str
    description: Optional[str] = None
    steps: List[WorkflowStep]

class WorkflowCreate(WorkflowBase):
    @field_validator('steps')
    @classmethod
    def check_consecutive_duplicates(cls, steps: List[WorkflowStep]) -> List[WorkflowStep]:
        if not steps:
            return steps
            
        for i in range(len(steps) - 1):
            if steps[i].action == steps[i+1].action:
                raise ValueError(f"Consecutive duplicate actions are not allowed: Step {i+1} and Step {i+2} are both '{steps[i].action.value}'")
        return steps

class WorkflowRead(WorkflowBase):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class WorkflowRunCreate(BaseModel):
    input_text: str

class WorkflowStepRunRead(BaseModel):
    id: UUID
    workflow_run_id: UUID
    step_order: int
    step_type: str
    output_text: str
    model_config = ConfigDict(from_attributes=True)

class WorkflowRunRead(BaseModel):
    id: UUID
    workflow_id: UUID
    input_text: str
    status: str
    created_at: datetime
    step_runs: List[WorkflowStepRunRead] = []
    model_config = ConfigDict(from_attributes=True)

class KeyValidationRequest(BaseModel):
    api_key: str
