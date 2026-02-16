# CUTS – Constraints, Uncertainties, Tradeoffs & Scope

## 1. Constraints

- Scheduling uses greedy allocation (no optimization solver).
- All bookings are handled in-memory (no persistent booking DB).
- Weather data is assumed to return valid weather category (VMC, MVFR, IMC, LIFR).
- Aircraft and simulator availability are date-based (not time-based granularity).
- Instructor duty hours are calculated using slot hour difference only.
- No rest-period regulation is implemented.
- Maintenance status is static (no dynamic flying-hour tracking).

---

## 2. Uncertainties

- Weather API reliability and response time.
- Edge cases when no aircraft or simulator is available.
- Future expansion to support multi-stage training programs.
- Handling overlapping slot times (currently assumes non-overlapping slots).

---

## 3. Tradeoffs

- Used greedy scheduling for simplicity and performance.
- Chose JSON-based ingestion instead of database seeding for faster prototyping.
- Used markdown-based rule engine instead of hardcoded rules for flexibility.
- Slot-level booking instead of minute-level booking for performance.

---

## 4. Scope

Included:
- Aircraft scheduling
- Instructor allocation
- Duty hour tracking
- Weather minima rule parsing
- Dispatch decision engine
- Simulator fallback
- Double booking prevention (slot-level)

Not Included:
- Optimization algorithms
- Real-time weather streaming
- Advanced regulatory compliance logic
- Aircraft flying-hour tracking
