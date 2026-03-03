from fastapi import FastAPI, Query
from typing import Optional
from pathlib import Path

from location import get_closest_libraries, load_library
from retrieval import load_room_docstore, retrieve_5_rooms

app = FastAPI(title="Study Buddies API")

BASE = Path(__file__).parent.resolve()
STUDY_SPOTS_DIR = BASE / "Study Spots"

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
        min_capacity=cap,
        duration_minutes=dur,
        k=k,
    )

    return {
        "query": q,
        "cap": cap,
        "dur": dur,
        "results": results,
    }