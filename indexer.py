import os
import re
import json
import string
from pathlib import Path
from nltk.stem import PorterStemmer

class Posting:
    def __init__(self, uid: str, doc_id: int):
        self.doc_id = doc_id
        self.term_freq = 1 # binary presence
        self.term_weight = 1.0

    def post_report(self):
        return {
            "doc_id": self.doc_id,
            "term frequency": self.term_freq,
            "term weight (importance)" : self.term_weight
        }
    
# tokenization -> not really using weights
stemmer = PorterStemmer()
TOKEN_RE = re._compiler(r"\b[a-zA-Z0-9]+\b")

def tokenize_and_stem(text):
    # return set of stems for this test -> binary presence
    if not isinstance(text, str) or not text.strip():
        return set()
        
    stems = set()
    for tok in TOKEN_RE.findall(text.lower()):
        stems.add(stemmer.stem(tok))
    return stems

# make partitions for easy indexing
letters = list(string.ascii_lowercase)
PARTITIONS = (
    ["other"]
    + letters
    + [a + b for a in letters for b in letters]
    + [a + b + c for a in letters for b in letters for c in letters]
)

def get_partition(token):
    if not token:
        return "other"
    token = token.lower()

    if token[0] not in string.ascii_lowercase:
        return "other"
    
    if len(token) == 1 or token[1] not in string.ascii_letters:
        return token[0]
    
    if len(token) == 2 or token[2] not in string.ascii_letters:
        return token[:2]
    
    return token[:3]

# get one doc per room
def extract_room_docs(file_path):
    '''
    returns {
        uid : identifier
        terms: set(stems)
        store : metadata (slots bitset)
    }
    '''
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    space = data.get("space", {}) or {}
    space_id = space.get("id", file_path.stem)
    space_name = space.get("name", file_path.stem)
    day = data.get("date", "")

    docs = []
    rooms = data.get("rooms", []) or []

    for room in rooms:
        room_id = room.get("id", "")
        room_name = room.get("name", "")
        capacity = room.get("capacity", "")
        bitset = room.get("slots_bitset", "")

        uid = f"{space_id}:{room_id}:{day}"

        # making searchable text fields
        searchable_text = " ".join([
            str(space_name),
            str(space_id),
            str(day),
            str(room_name),
            str(room_id),
            "capacity",
            str(capacity),
        ]).strip()

        terms = set()
        terms |= tokenize_and_stem(searchable_text)

        docs.append({
            "uid": uid,
            "terms": terms,
            "store": {
                "uid" : uid,
                "space": space,
                "date" : day,
                "room" : {
                    "id" : room_id,
                    "name" : room_name,
                    "capacity" : capacity,
                    "slots_bitset" : bitset 
                }
            }
        })
    
    return docs

# index writing
def flush_partial_index(partial_index, out_folder, run_id):
    out_folder = Path(out_folder)

    for part, index in partial_index.items():
        if not index:
            continue
        
        posting_obj_map = {}
        for term, postings_dict in index.items():
            sorted_postings = sorted(postings_dict.values, key=lambda p:p.doc_id)
            posting_obj_map[term] = [p.post_report() for p in sorted_postings]
        
        posting_obj_map = dict(sorted(posting_obj_map.items()))
        out_path = out_folder / f"Inverted_index_part{run_id}.json"
        with open(out_path, 'w', encoding="utf-8") as f:
            json.dump(posting_obj_map, f, ensure_ascii=False)