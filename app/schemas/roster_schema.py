from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date


# =====================================================
# 1️⃣ Individual Assignment Schema
# =====================================================

class Assignment(BaseModel):
    student_id: str = Field(..., description="Unique student identifier")
    instructor_id: Optional[str] = Field(
        None,
        description="Instructor assigned (None if solo)"
    )
    aircraft_id: Optional[str] = Field(
        None,
        description="Aircraft assigned (None if SIM)"
    )
    simulator_id: Optional[str] = Field(
        None,
        description="Simulator assigned (None if aircraft sortie)"
    )
    slot_id: str = Field(..., description="Time slot identifier")
    session_type: str = Field(
        ...,
        description="AIRCRAFT or SIM"
    )
    status: str = Field(
        ...,
        description="SCHEDULED / CONVERTED_TO_SIM / CANCELLED"
    )
    weather_category: Optional[str] = Field(
        None,
        description="VMC / IMC / UNKNOWN"
    )
    citations: List[str] = Field(
        default_factory=list,
        description="Regulatory citations applied"
    )


# =====================================================
# 2️⃣ Day-Level Schema
# =====================================================

class DailyRoster(BaseModel):
    date: date
    assignments: List[Assignment]


# =====================================================
# 3️⃣ Unassigned Students Schema
# =====================================================

class Unassigned(BaseModel):
    student_id: str
    reason: str


# =====================================================
# 4️⃣ Final Roster Response Schema
# =====================================================

class WeeklyRosterResponse(BaseModel):
    week_start: date
    base_icao: str
    roster: List[DailyRoster]
    unassigned: List[Unassigned]
