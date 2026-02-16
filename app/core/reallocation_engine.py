"""
Dynamic Reallocation Engine
Level-2 Requirement:
Repair roster after disruption with minimal churn.
"""

from copy import deepcopy
from typing import Dict, List, Any

from app.core.scheduler import Scheduler


class ReallocationEngine:
    """
    Repairs an existing roster after a disruption
    instead of regenerating everything.
    """

    # ============================================================
    # INIT
    # ============================================================

    def __init__(self, students, instructors, aircraft, simulators, time_slots):
        self.students = students
        self.instructors = instructors
        self.aircraft = aircraft
        self.simulators = simulators
        self.time_slots = time_slots

    # ============================================================
    # PUBLIC ENTRYPOINT
    # ============================================================

    def reallocate(self, current_roster: List[Dict], event: Dict[str, Any]):
        """
        Workflow:
        1️⃣ Identify affected slots
        2️⃣ Remove only those slots
        3️⃣ Re-run scheduler ONLY for missing work
        4️⃣ Merge results
        5️⃣ Produce diff
        """

        original = deepcopy(current_roster)

        affected_slots = self._identify_affected_slots(current_roster, event)

        if not affected_slots:
            return current_roster, self._build_diff(original, current_roster)

        pruned_roster = self._remove_affected(current_roster, affected_slots)

        scheduler = Scheduler(
            self.students,
            self.instructors,
            self.aircraft,
            self.simulators,
            self.time_slots
        )

        repaired_roster, _ = scheduler.generate_weekly_roster()

        merged = self._merge_rosters(pruned_roster, repaired_roster, affected_slots)

        diff = self._build_diff(original, merged)

        return merged, diff

    # ============================================================
    # IMPACT ANALYSIS
    # ============================================================

    def _identify_affected_slots(self, roster, event):
        affected = []

        for day in roster:
            date = day.get("date")

            for slot in day["slots"]:

                if event["type"] == "AIRCRAFT_UNSERVICEABLE":
                    if slot["resource_id"] == event["aircraft_id"]:
                        affected.append(slot["slot_id"])

                elif event["type"] == "INSTRUCTOR_UNAVAILABLE":
                    if slot["instructor_id"] == event["instructor_id"]:
                        affected.append(slot["slot_id"])

                elif event["type"] == "STUDENT_UNAVAILABLE":
                    if slot["student_id"] == event["student_id"]:
                        affected.append(slot["slot_id"])

                elif event["type"] == "WEATHER_UPDATE":
                    # Only affect specified dates if provided
                    event_dates = event.get("dates")
                    if not event_dates or date in event_dates:
                        affected.append(slot["slot_id"])

        return affected

    # ============================================================
    # REMOVE INVALID ASSIGNMENTS
    # ============================================================

    def _remove_affected(self, roster, affected_slot_ids):
        new_roster = deepcopy(roster)

        for day in new_roster:
            day["slots"] = [
                slot for slot in day["slots"]
                if slot["slot_id"] not in affected_slot_ids
            ]

        return new_roster

    # ============================================================
    # MERGE REPAIRED ASSIGNMENTS BACK
    # ============================================================

    def _merge_rosters(self, base_roster, repaired_roster, affected_slot_ids):
        merged = deepcopy(base_roster)

        repaired_lookup = {}
        slot_day_lookup = {}

        # Build lookup from repaired roster
        for day in repaired_roster:
            date = day["date"]
            for slot in day["slots"]:
                repaired_lookup[slot["slot_id"]] = slot
                slot_day_lookup[slot["slot_id"]] = date

        # Insert repaired slots into correct day
        for sid in affected_slot_ids:
            if sid not in repaired_lookup:
                continue

            repaired_slot = repaired_lookup[sid]
            target_date = slot_day_lookup[sid]

            for day in merged:
                if day["date"] == target_date:
                    day["slots"].append(repaired_slot)
                    break

        return merged

    # ============================================================
    # CHANGE DIFF (Audit Trail)
    # ============================================================

    def _build_diff(self, old, new):

        def flatten(roster):
            return {
                slot["slot_id"]: slot
                for day in roster
                for slot in day["slots"]
            }

        old_map = flatten(old)
        new_map = flatten(new)

        added = [sid for sid in new_map if sid not in old_map]
        removed = [sid for sid in old_map if sid not in new_map]
        changed = [
            sid for sid in new_map
            if sid in old_map and new_map[sid] != old_map[sid]
        ]

        return {
            "added": added,
            "removed": removed,
            "changed": changed,
            "summary": f"{len(changed)} adjusted | {len(added)} added | {len(removed)} removed"
        }
