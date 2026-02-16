from collections import defaultdict
from copy import deepcopy
import random


class Scheduler:
    """
    Non-Greedy Scheduler with Weighted Optimization
    Keeps your constraint logic but improves assignment quality using scoring + local repair.
    """

    # -----------------------------
    # Objective Function Weights
    # (Document these in PLAN.md)
    # -----------------------------
    WEIGHTS = {
        "priority_match": 50,
        "instructor_continuity": 20,
        "workload_balance": 10,
        "sim_penalty": -80,
        "reassignment_penalty": -40,
    }

    def __init__(self, students, instructors, aircraft, simulators, time_slots):

        self.students = students
        self.instructors = instructors
        self.aircraft = aircraft
        self.simulators = simulators
        self.time_slots = time_slots

        # Track bookings to prevent double booking
        self.booked_students = set()
        self.booked_instructors = set()
        self.booked_resources = set()

        # Track instructor duty hours
        self.instructor_duty = defaultdict(lambda: defaultdict(int))

        # Context tracking (used for optimization)
        self.last_instructor = {}
        self.instructor_load = defaultdict(int)

    # ============================================================
    # PUBLIC METHOD
    # ============================================================

    def generate_weekly_roster(self):
        """
        Step 1: Build feasible roster (constraint-safe)
        Step 2: Improve roster using local search optimization
        """

        base_roster, unassigned = self._build_initial_roster()

        optimized = self._optimize_roster(base_roster)

        return optimized, unassigned

    # ============================================================
    # INITIAL FEASIBLE ROSTER (your logic but scored)
    # ============================================================

    def _build_initial_roster(self):

        roster = []
        unassigned = []

        for day in self.time_slots:
            date = day["date"]
            day_entry = {"date": date, "slots": []}

            for slot in day["slots"]:

                assignment = self._select_best_candidate(date, slot)

                if assignment:
                    day_entry["slots"].append(assignment)
                else:
                    unassigned.append({
                        "entity": "slot",
                        "id": slot["slot_id"],
                        "reason": "No valid assignment found"
                    })

            roster.append(day_entry)

        return roster, unassigned

    # ============================================================
    # NON-GREEDY SELECTION (Scoring Instead of First Match)
    # ============================================================

    def _select_best_candidate(self, date, slot):

        candidates = []

        for student in sorted(self.students, key=lambda s: s["priority"], reverse=True):

            if not self._student_available(student, date):
                continue

            if (student["id"], date) in self.booked_students:
                continue

            for instructor in self.instructors:

                if not self._instructor_valid(instructor, student, date, slot):
                    continue

                if (instructor["id"], date) in self.booked_instructors:
                    continue

                # Try AIRCRAFT first
                for ac in self.aircraft:

                    if not self._aircraft_valid(ac, date):
                        continue

                    if (ac["id"], date) in self.booked_resources:
                        continue

                    if ac["type"] not in instructor["ratings"]:
                        continue

                    candidate = self._build_assignment(
                        student, instructor, ac, slot, date, "FLIGHT"
                    )

                    score = self._score_assignment(candidate)
                    candidates.append((score, candidate))

                # Try SIM fallback
                sim = self._allocate_simulator(student["stage"], date)
                if sim and (sim["id"], date) not in self.booked_resources:
                    candidate = self._build_assignment(
                        student, instructor, sim, slot, date, "SIM"
                    )
                    score = self._score_assignment(candidate)
                    candidates.append((score, candidate))

        if not candidates:
            return None

        # Select BEST candidate (not first valid)
        best = max(candidates, key=lambda x: x[0])[1]

        self._book_resources(best, date, slot)

        return best

    # ============================================================
    # OBJECTIVE FUNCTION (THE IMPORTANT PART)
    # ============================================================

    def _score_assignment(self, assignment):

        score = 0
        student_id = assignment["student_id"]
        instructor_id = assignment["instructor_id"]

        # Prioritize training progression
        score += self.WEIGHTS["priority_match"]

        # Prefer same instructor continuity
        if self.last_instructor.get(student_id) == instructor_id:
            score += self.WEIGHTS["instructor_continuity"]

        # Balance workload
        score -= self.instructor_load[instructor_id] * self.WEIGHTS["workload_balance"]

        # Penalize SIM if aircraft possible
        if assignment["activity"] == "SIM":
            score += self.WEIGHTS["sim_penalty"]

        return score

    # ============================================================
    # LOCAL SEARCH OPTIMIZATION (Improves Initial Roster)
    # ============================================================

    def _optimize_roster(self, roster, iterations=150):

        best = deepcopy(roster)
        best_score = self._evaluate_roster(best)

        for _ in range(iterations):
            trial = self._mutate_roster(best)
            trial_score = self._evaluate_roster(trial)

            if trial_score > best_score:
                best = trial
                best_score = trial_score

        return best

    def _mutate_roster(self, roster):
        """
        Small repair mutation (swap two slots).
        This is what makes it 'local search'.
        """

        new_roster = deepcopy(roster)

        day = random.choice(new_roster)
        if len(day["slots"]) < 2:
            return new_roster

        i, j = random.sample(range(len(day["slots"])), 2)
        day["slots"][i], day["slots"][j] = day["slots"][j], day["slots"][i]

        return new_roster

    def _evaluate_roster(self, roster):
        load = defaultdict(int)
        total = 0

        for day in roster:
            for slot in day["slots"]:
                iid = slot["instructor_id"]
                load[iid] += 1

        for day in roster:
            for slot in day["slots"]:
                total += self._score_assignment(slot)

        return total

    # ============================================================
    # ASSIGNMENT BUILDERS + CONSTRAINT HELPERS (UNCHANGED LOGIC)
    # ============================================================

    def _build_assignment(self, student, instructor, resource, slot, date, activity):

        return {
            "slot_id": slot["slot_id"],
            "start": slot["start"],
            "end": slot["end"],
            "activity": activity,  # FLIGHT or SIM
            "student_id": student["id"],
            "instructor_id": instructor["id"],
            "resource_id": resource["id"],
            "sortie_type": student["stage"],
            "dispatch_decision": None,
            "reasons": [],
            "citations": [],
            "aircraft_type": student["stage"],
        }


    def _student_available(self, student, date):
        return date in student["availability"]

    def _instructor_valid(self, instructor, student, date, slot):

        if date not in instructor["availability"]:
            return False

        duration = self._calculate_duration(slot)

        if self.instructor_duty[instructor["id"]][date] + duration > instructor["max_duty_hours_per_day"]:
            return False

        return True

    def _aircraft_valid(self, aircraft, date):

        if aircraft.get("maintenance") != "AVAILABLE":
            return False

        if date not in aircraft["availability"]:
            return False

        return True

    def _allocate_simulator(self, aircraft_type, date):

        for sim in self.simulators:
            if sim["type"] == f"{aircraft_type}_SIM" and date in sim["availability"]:
                return sim

        return None

    def _book_resources(self, assignment, date, slot):

        sid = assignment["student_id"]
        iid = assignment["instructor_id"]
        rid = assignment["resource_id"]

        self.booked_students.add((sid, date))
        self.booked_instructors.add((iid, date))
        self.booked_resources.add((rid, date))

        duration = self._calculate_duration(slot)
        self.instructor_duty[iid][date] += duration

        self.last_instructor[sid] = iid
        self.instructor_load[iid] += 1

    def _calculate_duration(self, slot):
        start = int(slot["start"].split(":")[0])
        end = int(slot["end"].split(":")[0])
        return end - start
