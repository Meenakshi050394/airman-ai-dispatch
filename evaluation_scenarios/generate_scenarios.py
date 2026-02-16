"""
Scenario Generator for Evaluation Harness

Creates 30 varied evaluation scenarios by modifying
students, instructors, aircraft, and simulator availability.

Run:
    python generate_scenarios.py
"""

import json
import os
import copy

BASE_DATA_DIR = "../data"
OUTPUT_DIR = "."

FILES = [
    "students.json",
    "instructors.json",
    "aircraft.json",
    "simulators.json",
    "time_slots.json"
]

BASE_ICAO = "VOBG"


def load_base_data():
    data = {}
    for f in FILES:
        path = os.path.join(BASE_DATA_DIR, f)
        with open(path) as fp:
            data[f.replace(".json", "")] = json.load(fp)
    return data


def build_scenario(base_data, idx):
    scenario = copy.deepcopy(base_data)

    # -----------------------------
    # Scenario variations
    # -----------------------------

    # Student overload
    if idx % 4 == 0:
        scenario["students"] = scenario["students"] * 2

    # Limited aircraft
    if idx % 5 == 0:
        scenario["aircraft"] = scenario["aircraft"][:1]

    # Instructor shortage
    if idx % 6 == 0:
        scenario["instructors"] = scenario["instructors"][:1]

    # Simulator outage
    if idx % 8 == 0:
        scenario["simulators"] = []

    # Maintenance event
    if idx % 7 == 0 and scenario["aircraft"]:
        scenario["aircraft"][0]["maintenance_status"] = "MAINTENANCE"

    scenario["base_icao"] = BASE_ICAO

    return scenario


def main():
    base_data = load_base_data()

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for i in range(1, 31):
        scenario = build_scenario(base_data, i)

        filename = f"scenario_{str(i).zfill(2)}.json"
        path = os.path.join(OUTPUT_DIR, filename)

        with open(path, "w") as fp:
            json.dump(scenario, fp, indent=2)

        print("Generated:", filename)


if __name__ == "__main__":
    main()
