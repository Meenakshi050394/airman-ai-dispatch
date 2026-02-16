# Flight Training Dispatch & Scheduling System

## Overview

This project implements a flight training scheduling system with integrated weather-based dispatch intelligence and simulator fallback logic.

The system supports:

- Aircraft allocation
- Instructor duty tracking
- Student priority scheduling
- Weather minima rule validation
- Dispatch decision engine
- Simulator fallback allocation
- Slot-level double booking prevention

---

## Architecture

Data Layer:
- JSON-based ingestion
- Markdown rule engine

Core Engines:
- Scheduler (Greedy allocation)
- Weather service
- Dispatch engine

Rule System:
- weather_minima.md
- dispatch_rules.md

---

## Key Features

- Priority-based student scheduling
- Aircraft-instructor compatibility check
- Instructor duty hour enforcement
- Maintenance-aware aircraft filtering
- Weather category based dispatch decisions
- Automatic simulator conversion
- Slot-level resource protection

---

## File Structure

app/
  core/
    schedule.py
    dispatch_engine.py
  services/
    ingestion_service.py
    weather_service.py
  utils/
    rule_loader.py

data/
  aircraft.json
  instructors.json
  students.json
  simulators.json
  time_slots.json
  weather_minima.md
  dispatch_rules.md

---

## Dispatch Logic

Weather categories supported:
- VMC
- MVFR
- IMC
- LIFR

Dispatch actions:
- PROCEED
- CAUTION_PROCEED
- CONVERT_TO_SIM
- IFR_ALLOWED
- CANCEL

---

## Future Enhancements

- Optimization-based scheduling
- Advanced regulatory compliance
- Real-time weather API integration
- Aircraft utilization analytics
- Database persistence
