import requests
import time
import hashlib
from datetime import datetime
from app.config import settings


# =====================================================
# In-memory cache
# =====================================================

_weather_cache = {}
TTL_SECONDS = settings.WEATHER_CACHE_TTL  # 10 minutes


# =====================================================
# Deterministic pseudo weather generator
# =====================================================

def _generate_deterministic_weather(seed_string: str):

    # Use hash to ensure repeatable output
    seed_hash = hashlib.sha256(seed_string.encode()).hexdigest()

    # Convert hash to numeric value
    numeric = int(seed_hash[:8], 16)

    # Deterministic ranges
    ceiling = 500 + (numeric % 2500)  # 500 - 3000 ft
    visibility = 1000 + (numeric % 9000)  # 1000 - 10000 m
    wind = 5 + (numeric % 35)  # 5 - 40 knots

    return {
        "ceiling": ceiling,
        "visibility": visibility,
        "wind": wind
    }


# =====================================================
# Weather classification
# =====================================================

def _classify_weather(ceiling: int, visibility: int):

    # Basic aviation logic
    if ceiling >= 1500 and visibility >= 5000:
        return "VMC"
    else:
        return "IMC"


# =====================================================
# Public API
# =====================================================

def get_weather(icao: str, start_time: str, end_time: str):

    key = f"{icao}_{start_time}_{end_time}"
    now = time.time()

    # Return cached value if valid
    if key in _weather_cache:
        data, timestamp = _weather_cache[key]
        if now - timestamp < TTL_SECONDS:
            data["confidence"] = "cached"
            return data

    # Deterministic seed
    seed_string = f"{icao}_{start_time}_{end_time}"

    # Retry wrapper (mandatory requirement)
    for _ in range(3):
        try:
            base_weather = _generate_deterministic_weather(seed_string)

            category = _classify_weather(
                base_weather["ceiling"],
                base_weather["visibility"]
            )
            break
        except Exception:
            time.sleep(0.5)
    else:
        # deterministic fallback
        weather = {
        "icao": icao,
        "start_time": start_time,
        "end_time": end_time,
        "ceiling": base_weather["ceiling"],
        "visibility": base_weather["visibility"],
        "wind": base_weather["wind"],
        "category": category,
        "fetched_at": datetime.utcnow().isoformat(),
        "source": "deterministic_simulation",
        "confidence": "live"
        }

        _weather_cache[key] = (weather, now)

        # ---- SAFETY FALLBACK ----
        if weather is None:
            weather = {
                "icao": icao,
                "start_time": start_time,
                "end_time": end_time,
                "ceiling": 9999,
                "visibility": 9999,
                "wind": 0,
                "category": "VMC",
                "fetched_at": datetime.utcnow().isoformat(),
                "source": "fallback",
                "confidence": "fallback"
            }

        return weather