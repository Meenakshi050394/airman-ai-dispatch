# Flight Training Dispatch & Scheduling System

## Overview

This project implements a flight training dispatch and scheduling system with integrated weather-based decision logic and dynamic roster repair.

## The system automatically:

* Schedules student training sessions
* Allocates instructors and aircraft
* Applies dispatch rules based on weather minima
* Converts flights to simulators when required
* Prevents double booking of resources
* Repairs schedules after disruptions
* Evaluates scheduling quality across multiple scenarios

The system is exposed via REST APIs using FastAPI and runs fully in Docker.

## Core Capabilities
### Scheduling Engine

* Priority-based student scheduling
* Aircraft–instructor compatibility validation
* Instructor duty-hour enforcement
* Maintenance-aware aircraft filtering
* Simulator fallback when aircraft unavailable

## Dispatch Engine

* Weather-based dispatch decision logic
* Rule-driven minima validation
* Automatic SIM conversion when weather fails
* Citation tracking for dispatch rules

## Constraint Protection

* Instructor double booking prevention
* Aircraft double booking prevention
* Slot conflict detection

## Dynamic Reallocation Engine

* Repairs only disrupted slots
* Minimizes roster churn
* Produces diff showing schedule changes

## Evaluation Harness

Runs scheduling across multiple scenarios
Computes scheduling metrics:

* Coverage
* Constraint violations
* Citation coverage
* Unassigned workload

## Architecture

### Data Layer

* JSON ingestion pipeline
* PostgreSQL database storage
* Rule documents stored in DB

## Engines

* Scheduler
* Dispatch Engine
* Constraint Checker
* Reallocation Engine
* Evaluation Harness

## Rule System

Rules are defined using Markdown documents:

* weather_minima.md
* dispatch_rules.md

These are parsed and applied dynamically during dispatch decisions.

## Project Structure
app/
├── core/
│   ├── scheduler.py
│   ├── dispatch_engine.py
│   ├── constraint_checker.py
│   └── reallocation_engine.py
│
├── services/
│   ├── ingestion_service.py
│   └── weather_service.py
│
├── evaluation/
│   └── harness.py
│
├── models/
├── schemas/
└── main.py

data/
├── aircraft.json
├── instructors.json
├── students.json
├── simulators.json
├── time_slots.json
├── weather_minima.md
└── dispatch_rules.md

## API Endpoints

1. Run ingestion

POST /ingest/run

Loads JSON and rule data into the database.

2. Generate roster

POST /roster/generate

Creates weekly roster and applies dispatch decisions.

Returns:

* Weekly assignments
* Dispatch status
* Unassigned slots

3. Recompute after disruption

POST /dispatch/recompute

Repairs affected slots after disruption events:

Examples:

* Aircraft unserviceable
* Instructor unavailable
* Student unavailable
* Weather updates

Returns updated roster and change diff.

4. Evaluation harness

POST /eval/run

Runs scheduling across evaluation scenarios and returns:

* Constraint violations
* Coverage metrics
* Citation coverage
* Unassigned workload

## Running with Docker

Build and start services

- docker compose up --build

Services started:

* FastAPI server (port 8000)
* PostgreSQL database

## Open API docs

### Open browser:

- http://localhost:8000/docs

All endpoints can be tested interactively.

## Dispatch Logic

Supported weather categories:

* VMC
* MVFR
* IMC
* LIFR

Dispatch actions:

* PROCEED
* CAUTION_PROCEED
* CONVERT_TO_SIM
* IFR_ALLOWED
* CANCEL

## Evaluation Metrics

Evaluation harness computes:

* Constraint violation rate
* Scheduling coverage
* Citation coverage
* Unassigned workload
  
Used to measure scheduling quality across scenarios.

## Future Improvements

Possible extensions:

* Optimization-based scheduling
* Real-time weather API integration
* Aircraft utilization analytics
* Multi-base scheduling support
* Advanced regulatory compliance checks
* Instructor workload balancing

## Submission Notes

This implementation demonstrates:

* End-to-end ingestion → scheduling → dispatch → repair workflow
* Rule-driven decision engine
* Scenario-based evaluation harness
* Dockerized deployment
* REST API integration