import json
import math
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
    with open(ROOMDOCMAP, "r", encoding="utf-8") as f:
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


