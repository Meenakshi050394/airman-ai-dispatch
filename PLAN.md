# System Design Plan

## Objective

Build a weekly flight training scheduler with dispatch intelligence and simulator fallback.

---

## Phase 1 – Data Layer

- Define JSON ingestion for:
  - Aircraft
  - Instructors
  - Students
  - Simulators
  - Time Slots
- Load weather and dispatch rules from markdown.

---

## Phase 2 – Scheduler Engine

- Priority-based student sorting
- Instructor availability validation
- Aircraft availability validation
- Slot-level double booking prevention
- Instructor duty hour tracking
- Simulator fallback logic

---

## Phase 3 – Weather Integration

- Fetch weather category via weather service
- Parse weather minima rules
- Match Aircraft_Type + Sortie_Type
- Determine weather compliance

---

## Phase 4 – Dispatch Engine

- Load dispatch_rules.md
- Match Weather_Category + Sortie_Type
- Apply rule:
  - PROCEED
  - CAUTION_PROCEED
  - CONVERT_TO_SIM
  - IFR_ALLOWED
  - CANCEL

---

## Phase 5 – Output

- Weekly roster JSON
- Unassigned slots list
- Dispatch decisions with rule citations
