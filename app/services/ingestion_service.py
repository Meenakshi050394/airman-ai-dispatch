import os
import json
import uuid
import hashlib
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.db_models import (
    Student,
    Instructor,
    Aircraft,
    Simulator,
    TimeSlot,
    RuleDocument,
    IngestionRun
)

# =====================================================
# Resolve data directory dynamically (CI/Docker safe)
# =====================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")


class IngestionService:

    def __init__(self, db: Session):
        self.db = db

    # =====================================================
    # Compute data signature for idempotency
    # =====================================================
    def _compute_signature(self):
        hasher = hashlib.sha256()

        for filename in sorted(os.listdir(DATA_DIR)):
            path = os.path.join(DATA_DIR, filename)

            if os.path.isfile(path):
                with open(path, "rb") as f:
                    hasher.update(f.read())

        return hasher.hexdigest()

    # =====================================================
    # Safe JSON loader
    # =====================================================
    def _load_json(self, path):
        with open(path) as f:
            try:
                return json.load(f)
            except Exception as e:
                raise Exception(f"Invalid JSON in {path}: {e}")

    # =====================================================
    # MAIN INGESTION RUN
    # =====================================================
    def run_ingestion(self):

        existing_running = (
            self.db.query(IngestionRun)
            .filter_by(status="RUNNING")
            .first()
        )

        if existing_running:
            raise Exception("Another ingestion process is already running.")

        run_id = str(uuid.uuid4())

        ingestion_run = IngestionRun(
            run_id=run_id,
            started_at=datetime.utcnow(),
            status="RUNNING",
            diff_summary={}
        )

        self.db.add(ingestion_run)
        self.db.commit()

        diff_summary = {}

        latest_success = (
            self.db.query(IngestionRun)
            .filter_by(status="SUCCESS")
            .order_by(IngestionRun.started_at.desc())
            .first()
        )

        current_signature = self._compute_signature()

        if (
            latest_success
            and latest_success.diff_summary
            and latest_success.diff_summary.get("signature") == current_signature
        ):
            ingestion_run.status = "SUCCESS"
            ingestion_run.completed_at = datetime.utcnow()
            ingestion_run.diff_summary = {"skipped": True}
            self.db.commit()

            return {"run_id": run_id, "diff_summary": {"skipped": True}}

        try:
            diff_summary["students"] = self._ingest_students()
            diff_summary["instructors"] = self._ingest_instructors()
            diff_summary["aircraft"] = self._ingest_aircraft()
            diff_summary["simulators"] = self._ingest_simulators()
            diff_summary["time_slots"] = self._ingest_time_slots()
            diff_summary["rules"] = self._ingest_rules()

            ingestion_run.status = "SUCCESS"
            ingestion_run.completed_at = datetime.utcnow()

            diff_summary["signature"] = current_signature
            ingestion_run.diff_summary = diff_summary

            self.db.commit()

        except Exception as e:
            self.db.rollback()

            ingestion_run.status = "FAILED"
            ingestion_run.completed_at = datetime.utcnow()
            ingestion_run.diff_summary = {"error": str(e)}

            self.db.commit()
            raise e

        return {
            "run_id": run_id,
            "diff_summary": diff_summary
        }

    # =====================================================
    # STUDENTS
    # =====================================================
    def _ingest_students(self):

        path = os.path.join(DATA_DIR, "students.json")
        data = self._load_json(path)

        changes = {"inserted": 0, "updated": 0}

        for item in data:
            existing = self.db.query(Student).filter_by(id=item["id"]).first()

            if existing:
                existing.stage = item["stage"]
                existing.priority = item["priority"]
                existing.solo_eligible = item.get(
                    "solo_eligible",
                    existing.solo_eligible
                )
                existing.required_sorties_per_week = item.get(
                    "required_sorties_per_week",
                    existing.required_sorties_per_week
                )
                existing.availability = item["availability"]
                changes["updated"] += 1
            else:
                self.db.add(Student(**item))
                changes["inserted"] += 1

        self.db.commit()
        return changes

    # =====================================================
    # INSTRUCTORS
    # =====================================================
    def _ingest_instructors(self):

        path = os.path.join(DATA_DIR, "instructors.json")
        data = self._load_json(path)

        changes = {"inserted": 0, "updated": 0}

        for item in data:
            existing = self.db.query(Instructor).filter_by(id=item["id"]).first()

            if existing:
                existing.ratings = item["ratings"]
                existing.availability = item["availability"]
                existing.max_duty_hours_per_day = item["max_duty_hours_per_day"]
                existing.sim_instructor = item["sim_instructor"]
                changes["updated"] += 1
            else:
                self.db.add(Instructor(**item))
                changes["inserted"] += 1

        self.db.commit()
        return changes

    # =====================================================
    # AIRCRAFT
    # =====================================================
    def _ingest_aircraft(self):

        path = os.path.join(DATA_DIR, "aircraft.json")
        data = self._load_json(path)

        changes = {"inserted": 0, "updated": 0}

        for item in data:
            existing = self.db.query(Aircraft).filter_by(id=item["id"]).first()

            if existing:
                existing.type = item["type"]
                existing.availability = item["availability"]
                existing.maintenance_status = item["maintenance_status"]
                changes["updated"] += 1
            else:
                self.db.add(Aircraft(**item))
                changes["inserted"] += 1

        self.db.commit()
        return changes

    # =====================================================
    # SIMULATORS
    # =====================================================
    def _ingest_simulators(self):

        path = os.path.join(DATA_DIR, "simulators.json")
        data = self._load_json(path)

        changes = {"inserted": 0, "updated": 0}

        for item in data:
            existing = self.db.query(Simulator).filter_by(id=item["id"]).first()

            if existing:
                existing.type = item["type"]
                existing.availability = item["availability"]
                existing.max_sessions_per_day = item.get(
                    "max_sessions_per_day",
                    existing.max_sessions_per_day
                )
                changes["updated"] += 1
            else:
                self.db.add(Simulator(**item))
                changes["inserted"] += 1

        self.db.commit()
        return changes

    # =====================================================
    # TIME SLOTS
    # =====================================================
    def _ingest_time_slots(self):

        path = os.path.join(DATA_DIR, "time_slots.json")
        data = self._load_json(path)

        changes = {"inserted": 0, "updated": 0}

        for day in data:
            for slot in day["slots"]:

                existing = (
                    self.db.query(TimeSlot)
                    .filter_by(id=slot["slot_id"])
                    .first()
                )

                slot_data = {
                    "id": slot["slot_id"],
                    "date": day["date"],
                    "start_time": slot["start"],
                    "end_time": slot["end"]
                }

                if existing:
                    existing.date = slot_data["date"]
                    existing.start_time = slot_data["start_time"]
                    existing.end_time = slot_data["end_time"]
                    changes["updated"] += 1
                else:
                    self.db.add(TimeSlot(**slot_data))
                    changes["inserted"] += 1

        self.db.commit()
        return changes

    # =====================================================
    # RULE DOCUMENTS
    # =====================================================
    def _ingest_rules(self):

        changes = {"inserted": 0, "updated": 0}

        for doc_name in ["weather_minima.md", "dispatch_rules.md"]:

            path = os.path.join(DATA_DIR, doc_name)

            with open(path) as f:
                content = f.read()

            existing = (
                self.db.query(RuleDocument)
                .filter_by(doc_name=doc_name)
                .first()
            )

            if existing:
                existing.content = content
                changes["updated"] += 1
            else:
                self.db.add(
                    RuleDocument(
                        doc_name=doc_name,
                        content=content
                    )
                )
                changes["inserted"] += 1

        self.db.commit()
        return changes
