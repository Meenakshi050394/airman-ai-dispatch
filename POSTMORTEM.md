# Postmortem Analysis

## What Worked Well

- Clear separation of scheduling and dispatch logic.
- Markdown-based rule engine allowed flexibility.
- Simulator fallback improved operational continuity.
- Slot-level booking prevented major conflicts.

---

## What Was Challenging

- Aligning aircraft types between JSON and rule files.
- Ensuring dispatch rules matched student stage.
- Handling booking granularity correctly.
- Preventing global booking lock issues.

---

## Bugs Encountered

- Aircraft maintenance key mismatch.
- Instructor double booking logic mismatch.
- Simulator booking attribute missing.
- Weather rule mismatch with aircraft types.

---

## Lessons Learned

- Consistency across data models is critical.
- Rule engines must match system entities exactly.
- Slot-level tracking is necessary for realistic scheduling.
- Documentation improves system clarity significantly.

---

## Future Improvements

- Optimization solver instead of greedy algorithm.
- Time-level booking granularity.
- Aircraft flying-hour tracking.
- Rest-period compliance logic.
- Database-backed scheduling.
- Real-time weather streaming.
