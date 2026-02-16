from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import init_db, get_db
from app.services.ingestion_service import IngestionService
from app.models.db_models import (
    Student,
    Instructor,
    Aircraft,
    Simulator,
    TimeSlot
)
from app.core.scheduler import Scheduler
from app.core.dispatch_engine import apply_dispatch
from app.schemas.roster_schema import WeeklyRosterResponse
from app.core.constraint_checker import ConstraintChecker
from app.core.reallocation_engine import ReallocationEngine
from app.evaluation.harness import EvaluationHarness
from app.config import settings


app = FastAPI(title=settings.APP_NAME)

init_db()


# =====================================================
# INGESTION
# =====================================================

@app.post("/ingest/run")
def run_ingestion(db: Session = Depends(get_db)):
    service = IngestionService(db)
    return service.run_ingestion()


# =====================================================
# ROSTER GENERATION
# =====================================================

@app.post("/roster/generate", response_model=WeeklyRosterResponse)
def generate_roster(db: Session = Depends(get_db)):

    students = db.query(Student).all()
    instructors = db.query(Instructor).all()
    aircraft = db.query(Aircraft).all()
    simulators = db.query(Simulator).all()
    time_slots = db.query(TimeSlot).all()

    students_data = [{
        "id": s.id,
        "stage": s.stage,
        "priority": s.priority,
        "solo_eligible": s.solo_eligible,
        "required_sorties_per_week": s.required_sorties_per_week,
        "availability": s.availability
    } for s in students]

    instructors_data = [{
        "id": i.id,
        "ratings": i.ratings,
        "availability": i.availability,
        "max_duty_hours_per_day": i.max_duty_hours_per_day,
        "sim_instructor": i.sim_instructor
    } for i in instructors]

    aircraft_data = [{
        "id": a.id,
        "type": a.type,
        "availability": a.availability,
        "maintenance": a.maintenance_status
    } for a in aircraft]

    simulators_data = [{
        "id": s.id,
        "type": s.type,
        "availability": s.availability,
        "max_sessions_per_day": s.max_sessions_per_day
    } for s in simulators]

    slots_by_date = {}
    for slot in time_slots:
        date_str = str(slot.date)
        slots_by_date.setdefault(date_str, []).append({
            "slot_id": slot.id,
            "start": slot.start_time,
            "end": slot.end_time
        })

    structured_slots = [
        {"date": d, "slots": s}
        for d, s in slots_by_date.items()
    ]

    scheduler = Scheduler(
        students_data,
        instructors_data,
        aircraft_data,
        simulators_data,
        structured_slots
    )

    roster, unassigned = scheduler.generate_weekly_roster()

    roster = apply_dispatch(
        roster,
        base_icao=settings.DEFAULT_BASE_ICAO,
        db=db
    )

    for day in roster:
        if "slots" in day:
            assignments = day.pop("slots")

            for a in assignments:
                resource_id = a.get("resource_id")

                if a.get("activity") == "SIM":
                    a["session_type"] = "SIM"
                    a["simulator_id"] = resource_id
                    a["aircraft_id"] = None
                else:
                    a["session_type"] = "AIRCRAFT"
                    a["aircraft_id"] = resource_id
                    a["simulator_id"] = None

                a["status"] = "PLANNED"

                day["assignments"] = assignments

    checker = ConstraintChecker()
    violations = checker.validate(roster)

    if violations:
        raise HTTPException(status_code=400, detail=violations)

    return {
        "week_start": datetime.utcnow().strftime("%Y-%m-%d"),
        "base_icao": settings.DEFAULT_BASE_ICAO,
        "roster": roster,
        "unassigned": unassigned
    }


# =====================================================
# DISPATCH RECOMPUTE
# =====================================================

@app.post("/dispatch/recompute")
def recompute(event: dict, db: Session = Depends(get_db)):

    students = db.query(Student).all()
    instructors = db.query(Instructor).all()
    aircraft = db.query(Aircraft).all()
    simulators = db.query(Simulator).all()
    time_slots = db.query(TimeSlot).all()

    students_data = [{
        "id": s.id,
        "stage": s.stage,
        "priority": s.priority,
        "solo_eligible": s.solo_eligible,
        "required_sorties_per_week": s.required_sorties_per_week,
        "availability": s.availability
    } for s in students]

    instructors_data = [{
        "id": i.id,
        "ratings": i.ratings,
        "availability": i.availability,
        "max_duty_hours_per_day": i.max_duty_hours_per_day,
        "sim_instructor": i.sim_instructor
    } for i in instructors]

    aircraft_data = [{
        "id": a.id,
        "type": a.type,
        "availability": a.availability,
        "maintenance": a.maintenance_status
    } for a in aircraft]

    simulators_data = [{
        "id": s.id,
        "type": s.type,
        "availability": s.availability,
        "max_sessions_per_day": s.max_sessions_per_day
    } for s in simulators]

    slots_map = {}
    for slot in time_slots:
        slots_map.setdefault(str(slot.date), []).append({
            "slot_id": slot.id,
            "start": slot.start_time,
            "end": slot.end_time
        })

    structured_slots = [{"date": d, "slots": s} for d, s in slots_map.items()]

    current_roster = event.get("current_roster")
    if not current_roster:
        raise HTTPException(
            status_code=400,
            detail="current_roster must be provided"
        )

    engine = ReallocationEngine(
        students_data,
        instructors_data,
        aircraft_data,
        simulators_data,
        structured_slots
    )

    updated_roster, diff = engine.reallocate(current_roster, event)

    updated_roster = apply_dispatch(
        updated_roster,
        base_icao=settings.DEFAULT_BASE_ICAO,
        db=db
    )

    return {"status": "replanned", "diff": diff, "roster": updated_roster}


# =====================================================
# EVALUATION ENDPOINT
# =====================================================

@app.post("/eval/run")
def run_evaluation(db: Session = Depends(get_db)):
    harness = EvaluationHarness(db=db)
    return harness.run_all()
