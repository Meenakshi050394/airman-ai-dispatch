import re
from app.services.weather_service import get_weather
from app.utils.rule_loader import load_rule


# =====================================================
# Parse weather_minima.md into structured rules
# =====================================================

def parse_weather_rules(md_text: str):

    rules = {}
    blocks = re.split(r"## ", md_text)[1:]

    for block in blocks:
        lines = block.strip().split("\n")
        rule_id = lines[0].strip()

        rule_data = {}

        for line in lines[1:]:
            if ":" in line:
                key, value = line.split(":", 1)
                rule_data[key.strip()] = value.strip()

        aircraft_type = rule_data.get("Aircraft_Type")
        sortie_type = rule_data.get("Sortie_Type")

        if aircraft_type and sortie_type:
            rules[(aircraft_type, sortie_type)] = {
                "Min_Visibility": int(rule_data.get("Min_Visibility", 0)),
                "Min_Ceiling": int(rule_data.get("Min_Ceiling", 0)),
                "Max_Wind": int(rule_data.get("Max_Wind", 999)),
                "rule_id": rule_id
            }

    return rules


def parse_dispatch_rules(md_text: str):

    rules = []
    blocks = re.split(r"## ", md_text)[1:]

    for block in blocks:
        lines = block.strip().split("\n")
        rule_id = lines[0].strip()

        rule_data = {}

        for line in lines[1:]:
            if ":" in line:
                key, value = line.split(":", 1)
                rule_data[key.strip()] = value.strip()

        rules.append({
            "rule_id": rule_id,
            "Weather_Category": rule_data.get("Weather_Category"),
            "Sortie_Type": rule_data.get("Sortie_Type"),
            "Action": rule_data.get("Action"),
            "Description": rule_data.get("Description"),
        })

    return rules



# =====================================================
# Apply dispatch logic
# =====================================================

def apply_dispatch(roster, base_icao, db):

    weather_md = load_rule(db, "weather_minima.md")
    dispatch_md = load_rule(db, "dispatch_rules.md")

    weather_rules = parse_weather_rules(weather_md)

    for day in roster:
        slots = day.get("slots", [])

        for slot in slots:

            if slot["activity"] != "FLIGHT":
                continue

            aircraft_type = slot.get("aircraft_type")
            sortie_type = slot.get("sortie_type")

            if not aircraft_type or not sortie_type:
                continue

            rule = weather_rules.get((aircraft_type, sortie_type))
            if not rule:
                continue

            weather = get_weather(
                base_icao,
                slot["start"],
                slot["end"]
            )

            slot.setdefault("citations", [])
            slot.setdefault("reasons", [])

            # Safe weather handling
            if weather:
                slot["weather_category"] = weather.get("category")
            else:
                slot["weather_category"] = None

            # Handle missing weather safely
            if not weather or weather.get("confidence") == "fallback":
                slot["dispatch_decision"] = "NEEDS_REVIEW"
                slot["reasons"].append("WEATHER_UNAVAILABLE")
                slot["citations"].append(f"rules:{rule['rule_id']}")
                continue

            visibility_ok = weather["visibility"] >= rule["Min_Visibility"]
            ceiling_ok = weather["ceiling"] >= rule["Min_Ceiling"]
            wind_ok = weather["wind"] <= rule["Max_Wind"]

            slot.setdefault("citations", [])
            slot.setdefault("reasons", [])

            if visibility_ok and ceiling_ok and wind_ok:
                slot["dispatch_decision"] = "GO"
                slot["reasons"].append("WEATHER_OK")

            else:
                sim_available = slot.get("sim_available", True)

                if sim_available:
                    slot["dispatch_decision"] = "NO_GO"
                    slot["activity"] = "SIM"
                    slot["reasons"].append("WX_BELOW_MINIMA")

                    slot["resource_id"] = slot.get("sim_id", slot["resource_id"])

                else:
                    slot["dispatch_decision"] = "NEEDS_REVIEW"
                    slot["reasons"].append("NO_SIM_AVAILABLE")


            slot["citations"].append(f"rules:{rule['rule_id']}")

            
    return roster
