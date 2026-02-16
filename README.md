# Flight Training Dispatch & Scheduling System

## Overview

This project implements a flight training dispatch and scheduling system with integrated weather-based decision logic and dynamic roster repair.

The system automatically:

- Schedules student training sessions
- Allocates instructors and aircraft
- Applies dispatch rules based on weather minima
- Converts flights to simulators when required
- Prevents double booking of resources
- Repairs schedules after disruptions

The system is exposed via REST APIs using FastAPI and runs fully in Docker.

---

## Core Capabilities

### Scheduling Engine
- Priority-based student scheduling
- Aircraft and instructor compatibility checks
- Instructor duty constraints
- Maintenance-aware aircraft filtering

### Dispatch Engine
- Weather category evaluation
- Rule-based dispatch decisions
- Simulator fallback conversion
- Citation tracking for rule decisions

### Constraint Protection
- Instructor double booking prevention
- Aircraft double booking prevention

### Dynamic Reallocation Engine
- Repairs only affected slots after disruption
- Minimal schedule churn
- Produces change diffs

---

## Architecture

### Data Layer
- JSON ingestion pipeline
- PostgreSQL database storage

### Engines
- Scheduler
- Dispatch engine
- Constraint checker
- Reallocation engine

### Rule System
- weather_minima.md
- dispatch_rules.md

---

## Project Structure

app/
core/
scheduler.py
dispatch_engine.py
constraint_checker.py
reallocation_engine.py
services/
ingestion_service.py
weather_service.py
evaluation/
harness.py

data/
aircraft.json
instructors.json
students.json
simulators.json
time_slots.json
weather_minima.md
dispatch_rules.md

---

## API Endpoints

### 1. Run ingestion

POST /ingest/run

Loads JSON data into database.

---

### 2. Generate roster

POST /roster/generate

Creates weekly roster and applies dispatch logic.

---

### 3. Recompute after disruption

POST /dispatch/recompute

Repairs affected slots after aircraft, instructor, or weather events.

---

### 4. Evaluation harness

POST /eval/run

Runs predefined evaluation scenarios.

---

## Running with Docker

### Build and start services

docker compose up --build

Services started:

    FastAPI server (port 8000)

    PostgreSQL database

Open API docs

http://localhost:8000/docs

## Dispatch Logic

Supported weather categories:

VMC
MVFR
IMC
LIFR

Dispatch decisions:

PROCEED
CAUTION_PROCEED
CONVERT_TO_SIM
IFR_ALLOWED
CANCEL

Future Improvements: 

Optimization-based scheduling
Real-time weather API integration
Utilization analytics
Multi-base operations
Advanced regulatory checks
Future Improvements
Optimization-based scheduling
Real-time weather API integration
Utilization analytics
Multi-base operations
Advanced regulatory checks

---

