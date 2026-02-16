from collections import defaultdict


class ConstraintChecker:

    def __init__(self):
        self.violations = []

    # --------------------------------------------------
    # Student Double Booking
    # --------------------------------------------------
    def check_student_double_booking(self, roster):
        student_slots = defaultdict(set)

        for day in roster:
            assignments = day.get("assignments") or day.get("slots", [])

            for assignment in assignments:
                student = assignment.get("student_id")
                slot = assignment.get("slot_id")

                if student:
                    if slot in student_slots[student]:
                        self.violations.append(
                            f"Student {student} double-booked in slot {slot}"
                        )

                    student_slots[student].add(slot)

    # --------------------------------------------------
    # Instructor Double Booking
    # --------------------------------------------------
    def check_instructor_double_booking(self, roster):
        instructor_slots = defaultdict(set)

        for day in roster:
            assignments = day.get("assignments") or day.get("slots", [])

            for assignment in assignments:
                instructor = assignment.get("instructor_id")
                slot = assignment.get("slot_id")

                if instructor:
                    if slot in instructor_slots[instructor]:
                        self.violations.append(
                            f"Instructor {instructor} double-booked in slot {slot}"
                        )

                    instructor_slots[instructor].add(slot)

    # --------------------------------------------------
    # Aircraft / Simulator Double Booking
    # --------------------------------------------------
    def check_resource_double_booking(self, roster):
        resource_slots = defaultdict(set)

        for day in roster:
            assignments = day.get("assignments") or day.get("slots", [])

            for assignment in assignments:
                resource = assignment.get("resource_id")
                slot = assignment.get("slot_id")

                if resource:
                    if slot in resource_slots[resource]:
                        self.violations.append(
                            f"Resource {resource} double-booked in slot {slot}"
                        )

                    resource_slots[resource].add(slot)

    # --------------------------------------------------
    # Main Validation Entry
    # --------------------------------------------------
    def validate(self, roster):
        # Reset violations every run
        self.violations = []

        self.check_student_double_booking(roster)
        self.check_instructor_double_booking(roster)
        self.check_resource_double_booking(roster)

        return self.violations
