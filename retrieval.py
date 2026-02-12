import json
import math
import time
import re
from indexer import get_partition
from pathlib import Path
from nltk.stem import PorterStemmer
from collections import OrderedDict

BASE = Path(__file__).parent
INDEX_DIR = BASE / "Index"

ROOMDOCMAP_PATH = INDEX_DIR / "roomdocmap.tsv"
ROOMDOCSTORE_PATH = INDEX_DIR / "roomdocstore.jsonl"
PARTIAL_PREFIX = "inverted_index_"

stemmer = PorterStemmer()
TOKEN_RE = re.compile(r"\b[a-zA-Z0-9]+\b")

ROOMDOCMAP = {}
ROOMDOCSTORE = {}

def load_room_docmap():
    with open(ROOMDOCMAP_PATH, "r", encoding="utf-8") as f:
        for line in f:
            room_doc_id, uid = line.strip().split("\t", 1)
            ROOMDOCMAP[int(room_doc_id)] = uid

def load_room_docstore():
    with open(ROOMDOCSTORE_PATH, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            ROOMDOCSTORE[i] = json.loads(line)

def normalize_query(q):
    tokens = TOKEN_RE.findall(q.lower())
    return [stemmer.stem(t) for t in tokens]

MAX_PARTIALS = 3
loaded_partials = OrderedDict()

def load_partial(part):
    if part in loaded_partials:
        loaded_partials.move_to_end(part)
        return loaded_partials[part]
    
    path = INDEX_DIR / f"{PARTIAL_PREFIX}{part}.json"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            loaded_partials[part] = json.load(f)
    else:
        loaded_partials[part] = {}

    loaded_partials.move_to_end(part)
    if len(loaded_partials) > MAX_PARTIALS:
        loaded_partials.popitem(last=False)
    
    return loaded_partials[part]

def get_postings_binary(term):
    part = get_partition(term)
    partial = load_partial(part)
    postings = partial.get(term, [])
    if not postings:
        return set()
    
    return {p["room_doc_id"] for p in postings}


# availabilty checker
def hhmm_to_minutes(hhmm):
    h, m = map(int, hhmm.split(":"))
    return h * 60 + m

def minutes_to_12h(minutes):
    h = minutes // 60
    m = minutes % 60
    suffix = "AM" if h < 12 else "PM"
    h = h % 12
    if h == 0:
        h = 12
    return f"{h}:{m:02d} {suffix}"

def slot_to_12h(slot_indx, start_hhm, slot_minutes):
    start_mintes = hhmm_to_minutes(start_hhm)
    return minutes_to_12h(start_mintes + slot_indx * slot_minutes)

def ceil_div(a, b):
    return (a + b - 1) // b

def is_range_available(bitset, start_slot, needed_slots):
    end = start_slot + needed_slots
    if start_slot < 0 or end > len(bitset):
        return False
    return all(bitset[i] == "1" for i in range(start_slot, end))

def first_available_start(meta, duration_minutes):
    room = meta["room"]
    space = meta ["space"]

    bitset = room.get("slots_bitset", "")
    start_hhmm = space["hours"]["start"]
    slot_minutes = space.get("slot_minutes", 30)

    needed = ceil_div(duration_minutes, slot_minutes)

    for i in range(len(bitset) - needed + 1):
        if is_range_available(bitset, i , needed):
            return slot_to_12h(i, start_hhmm, slot_minutes)
    return None

# 
def search_or(query):
    stems = normalize_query(query)
    matches = {}

    for s in stems:
        for d in get_postings_binary(s):
            if d not in matches:
                matches[d] = set()
            matches[d].add(s)
    return matches

def retrieve_5_rooms(query, min_capacity=None, duration_minutes=None, k=5):
    if duration_minutes is None:
        duration_minutes = 30
    
    t0 = time.perf_counter()
    matches = search_or(query)
    results = []

    for roomdoc_id, matched_terms in matches.items():
        meta = ROOMDOCSTORE.get(roomdoc_id)
        if not meta:
            continue

        cap = meta["room"].get("capacity")
        if min_capacity is not None and (cap is None or cap < min_capacity):
            continue

        start_time = first_available_start(meta, duration_minutes)
        if start_time is None:
            continue

        match_count = len(matched_terms)
        results.append((roomdoc_id, match_count, start_time, matched_terms))
    
    results.sort(key=lambda x: x[1], reverse=True)
    results = results[:k]

    ms = (time.perf_counter() - t0) * 1000
    print(f"Search time: {ms:.2f} ms")
    return results

# output results
def print_topres(results):
    print("\nTop 5 Recommended Study Spots")
    print("-" * 35)

    if not results:
        print("No available study spots match the query")
        return
    
    for i, (roomdoc_id, match_count, start_time, matched_terms) in enumerate(results, 1):
        meta = ROOMDOCSTORE[roomdoc_id]
        space = meta["space"]
        room = meta["room"]
        matched_terms = ", ".join(sorted(matched_terms))

        print(
            f"{i}. {space['name']} - {room['name']}\n"
            f"    Capacity: {room['capacity']} | "
            f"Matched keywords: {matched_terms}"
        )

        if start_time:
            print(f"    First available start time: {start_time}")
        print()

def main():
    load_room_docstore()
    print("\nStudy Spot Seach (Early Demo)")
    print("Type a query. Optional commands:")
    print("     :cap N")
    print("     :dur MIN")
    print("     :clear")
    print("     quit/exit")

    min_cap = None
    duration= None

    while True:
        query = input("\nSearch for: ").strip()
        if not query:
            continue
        
        if query.lower() in {"quit", "exit"}:
            break

        if query.startswith(":cap"):
            min_cap = int(query.split()[1])
            print(f"Min capacity set to {min_cap}")
            continue

        if query.startswith(":dur"):
            duration = int(query.split()[1])
            print(f"Duration set to {duration} minutes")
            continue

        if query.startswith(":clear"):
            min_cap = None
            duration = None
            print(f"Filters cleared")
            continue

        results = retrieve_5_rooms(query, min_capacity=min_cap, duration_minutes=(duration or 30), k=5)
        print_topres(results)


if __name__ == "__main__":
    main()

