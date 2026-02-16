import json
import os

from app.core.scheduler import Scheduler
from app.core.dispatch_engine import apply_dispatch
from app.core.constraint_checker import ConstraintChecker


class EvaluationHarness:

    def __init__(self, scenario_folder="evaluation_scenarios", db=None):
        self.scenario_folder = scenario_folder
        self.db = db

    # --------------------------------------------------
    # Utility Metrics
    # --------------------------------------------------

    def _count_slots(self, roster):
        total = 0
        for day in roster:
            total += len(day.get("slots", []))
        return total

    def _count_citations(self, roster):
        cited = 0
        total = 0

        for day in roster:
            for slot in day.get("slots", []):
                total += 1
                if slot.get("citations"):
                    cited += 1

        return cited, total

    # --------------------------------------------------
    # Run Evaluation
    # --------------------------------------------------

    def run_all(self):
        results = []

        for file in os.listdir(self.scenario_folder):
            if not file.endswith(".json"):
                continue

            scenario_path = os.path.join(self.scenario_folder, file)

            with open(scenario_path, "r") as f:
                scenario = json.load(f)

            scheduler = Scheduler(
                scenario["students"],
                scenario["instructors"],
                scenario["aircraft"],
                scenario["simulators"],
                scenario["time_slots"]
            )

            roster, unassigned = scheduler.generate_weekly_roster()

            # Dispatch decisions
            roster = apply_dispatch(
                roster,
                scenario["base_icao"],
                self.db
            )

            # Constraint validation
            checker = ConstraintChecker()
            violations = checker.validate(roster)

            total_slots = self._count_slots(roster)
            cited, slot_count = self._count_citations(roster)

            violation_rate = (
                len(violations) / total_slots
                if total_slots > 0 else 0
            )

            coverage = (
                (total_slots - len(unassigned)) / total_slots
                if total_slots > 0 else 1
            )

            citation_coverage = (
                cited / slot_count
                if slot_count > 0 else 1
            )

            results.append({
                "scenario": file,
                "violations": violations,
                "violation_rate": violation_rate,
                "coverage": coverage,
                "citation_coverage": citation_coverage,
                "unassigned_count": len(unassigned)
            })

        return results
