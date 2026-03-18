from fastapi import FastAPI, Query
from typing import Optional
from pathlib import Path
from datetime import datetime
import json
import pytz


from location import get_closest_libraries, load_library
from retrieval import load_room_docstore, retrieve_5_rooms
from input import fetch_freebusy_from_api, parse_google_freebusy, get_free_times_for_day


app = FastAPI(title="Study Buddies API")

BASE = Path(__file__).parent.resolve()
STUDY_SPOTS_DIR = BASE / "Study Spots"
SCHEDULES_DIR = BASE / "Schedules"

LIBRARIES = []
ROOMS_LOADED = False


@app.on_event("startup")
def startup():
    global LIBRARIES, ROOMS_LOADED

    if not ROOMS_LOADED:
        load_room_docstore()
        ROOMS_LOADED = True

    langson = load_library(str(STUDY_SPOTS_DIR / "Langson_Library.json"))
    science = load_library(str(STUDY_SPOTS_DIR / "Science_Library.json"))
    LIBRARIES = [langson, science]


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/search")
def search(
    q: str = Query(...),
    cap: Optional[int] = None,
    dur: int = 30,
    k: int = 5,
):
    results = retrieve_5_rooms(
        q,
        max_capacity=cap,
        duration_minutes=dur,
        k=k,
    )

    return {
        "query": q,
        "cap": cap,
        "dur": dur,
        "results": results,
    }

@app.get("/study-spots")
def study_spots(
    q: str = Query(""),
    lat: float = Query(...),
    lon: float = Query(...),
    cap: Optional[int] = None, #max_cap
    dur: int = 30,
    k: int = 5,
    preferred_library: Optional[str] = None,
    features: Optional[str] = None
):
    user_location = (lat, lon)

    libraries_results = get_closest_libraries(user_location, LIBRARIES)
    closest_library = libraries_results[0][0]

    #enhanced_query = f"{closest_library} {q}".strip()

    features_list = []
    if features:
        features_list = [f.strip().lower() for f in features.split(",") if f.strip()]

    results = retrieve_5_rooms(
        q,
        max_capacity=cap,
        duration_minutes=dur,
        k=k,
        closest_library=closest_library,
        preferred_library=preferred_library,
        preferred_features=features_list,
    )

    formatted_libraries = [
        {
            "library": lib[0],
            "distance": lib[1],
        }
        for lib in libraries_results
    ]

    return {
        "query": q,
        #"enhanced_query": enhanced_query,
        "user_location": {
            "lat": lat,
            "lon": lon,
        },
        "closest_library": closest_library,
        "preferred_library": preferred_library,
        "features": features_list,
        "libraries_by_distance": formatted_libraries,
        "cap": cap,
        "dur": dur,
        "results": results,
    }


@app.get("/schedule")
def schedule(dur: int = 30):
    busy_intervals = fetch_freebusy_from_api(['primary'], days_ahead=7)

    if busy_intervals is None:
        try:
            with open(SCHEDULES_DIR / "mockweek.json", "r", encoding="utf-8") as f:
                mock_json = json.load(f)
            busy_intervals = parse_google_freebusy(mock_json)
        except FileNotFoundError:
            return {
                "ok": False,
                "error": "No schedule data available"
            }

    tz = pytz.timezone("America/Los_Angeles")
    today = datetime.now(tz).date()

    free_times = get_free_times_for_day(
        busy_intervals,
        today,
        tz,
        start_hour=8,
        end_hour=22,
        min_duration=dur
    )

    formatted_free_times = []
    for block in free_times:
        if isinstance(block, tuple) and len(block) >= 2:
            formatted_free_times.append({
                "start": str(block[0]),
                "end": str(block[1]),
            })
        else:
            formatted_free_times.append({
                "value": str(block)
            })

    return {
        "ok": True,
        "date": str(today),
        "timezone": "America/Los_Angeles",
        "duration_minutes": dur,
        "free_times": formatted_free_times,
    }


@app.get("/profile")
def profile():
    return {
        "name": "Emmanuel",
        "preferences": {
            "max_capacity": 4,
            "duration": 30,
            "features": ["quiet", "whiteboard"]
        }
    }