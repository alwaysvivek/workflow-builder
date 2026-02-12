from sqlalchemy import create_engine, Column, String, Text, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
import datetime
from core.config import settings

# Use settings for DB URL
DATABASE_URL = settings.DATABASE_URL

# Check if using SQLite (which needs specific connect args)
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, index=True)
    description = Column(Text)
    steps = Column(JSON)  # Stores JSONB in Postgres
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)

    runs = relationship("WorkflowRun", back_populates="workflow")


class WorkflowRun(Base):
    __tablename__ = "workflow_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflows.id"))
    input_text = Column(Text)
    status = Column(String, default="running") # running, completed, failed
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)

    workflow = relationship("Workflow", back_populates="runs")
    step_runs = relationship("WorkflowStepRun", back_populates="workflow_run")


class WorkflowStepRun(Base):
    __tablename__ = "workflow_step_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_run_id = Column(UUID(as_uuid=True), ForeignKey("workflow_runs.id"))
    step_order = Column(Integer)
    step_type = Column(String)
    output_text = Column(Text)

    workflow_run = relationship("WorkflowRun", back_populates="step_runs")
