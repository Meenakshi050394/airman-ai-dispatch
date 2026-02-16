from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean,
    Date,
    DateTime,
    JSON,
    Text
)
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


# ==========================
# INGESTION TRACKING
# ==========================

class IngestionRun(Base):
    __tablename__ = "ingestion_runs"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, unique=True, index=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    status = Column(String)  # SUCCESS / FAILED
    diff_summary = Column(JSON)  # what changed since last ingestion


# ==========================
# RULE DOCUMENTS (RAG source)
# ==========================

class RuleDocument(Base):
    __tablename__ = "rules_docs"

    id = Column(Integer, primary_key=True, index=True)
    doc_name = Column(String, unique=True)
    content = Column(Text)
    uploaded_at = Column(DateTime, default=datetime.utcnow)


# ==========================
# STUDENTS
# ==========================

class Student(Base):
    __tablename__ = "students"

    id = Column(String, primary_key=True)
    stage = Column(String)
    priority = Column(Integer)
    solo_eligible = Column(Boolean)
    required_sorties_per_week = Column(Integer)

    availability = Column(JSON)  # ["2025-02-10", "2025-02-11"]

    created_at = Column(DateTime, default=datetime.utcnow)


# ==========================
# INSTRUCTORS
# ==========================

class Instructor(Base):
    __tablename__ = "instructors"

    id = Column(String, primary_key=True)

    ratings = Column(JSON)  # ["H125", "C172"]
    availability = Column(JSON)

    max_duty_hours_per_day = Column(Integer)
    sim_instructor = Column(Boolean)

    created_at = Column(DateTime, default=datetime.utcnow)


# ==========================
# AIRCRAFT
# ==========================

class Aircraft(Base):
    __tablename__ = "aircraft"

    id = Column(String, primary_key=True)

    type = Column(String)
    availability = Column(JSON)

    # 🔴 MUST BE STRING (scheduler expects AVAILABLE / DOWN / MAINTENANCE)
    maintenance_status = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)


# ==========================
# SIMULATORS
# ==========================

class Simulator(Base):
    __tablename__ = "simulators"

    id = Column(String, primary_key=True)

    type = Column(String)
    availability = Column(JSON)
    max_sessions_per_day = Column(Integer)

    created_at = Column(DateTime, default=datetime.utcnow)


# ==========================
# TIME SLOTS
# ==========================

class TimeSlot(Base):
    __tablename__ = "time_slots"

    id = Column(String, primary_key=True)

    date = Column(Date)
    start_time = Column(String)
    end_time = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)


# ==========================
# ROSTER VERSIONING (LEVEL-2 REQUIREMENT)
# ==========================

class RosterVersion(Base):
    """
    Stores every generated roster version.
    Required for:
    - Auditability
    - Change tracking
    - Dynamic reallocation trace
    """

    __tablename__ = "roster_versions"

    id = Column(Integer, primary_key=True, index=True)

    # e.g. "v1", "v2", "weather_fix_01"
    version = Column(String, index=True)

    # Why this roster was created
    reason = Column(String)  # INITIAL_BUILD / WEATHER / AIRCRAFT_DOWN

    date_range = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String)

    # Diff from previous roster
    diff_json = Column(JSON)

    # 🔴 FULL SNAPSHOT (MANDATORY FOR EVALUATION)
    roster_snapshot = Column(JSON)

    correlation_id = Column(String)
