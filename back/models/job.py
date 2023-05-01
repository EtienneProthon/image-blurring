from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from back.database import Base

View = declarative_base()


@dataclass
class JobGroup(Base):
    id: int
    created_at: datetime
    __tablename__ = "job_groups"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    jobs = relationship("Job", back_populates="job_group")


@dataclass
class JobGroupView(View):
    id: int
    created_at: datetime
    total_jobs: int
    completed_jobs: int
    finished_at: datetime
    __tablename__ = "job_groups_view"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    total_jobs = Column(Integer)
    completed_jobs = Column(Integer)
    finished_at = Column(DateTime)


@dataclass
class Job(Base):
    id: int
    job_group_id: int
    created_at: datetime
    started_at: datetime
    finished_at: datetime
    status: str
    image_url: str
    process_params: JSONB
    original_image_s3: str
    processed_image_s3: str

    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True)
    job_group_id = Column(Integer, ForeignKey("job_groups.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    finished_at = Column(DateTime)
    status = Column(String)
    image_url = Column(String)
    process_params = Column(JSONB)
    original_image_s3 = Column(String)
    processed_image_s3 = Column(String)

    job_group = relationship("JobGroup", back_populates="jobs")
