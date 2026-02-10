import os
import re
import json
import string
from pathlib import Path
from nltk.stem import PorterStemmer

class Posting:
    def __init__(self, room_doc_id: int):
        self.room_doc_id = room_doc_id
        self.term_freq = 1 # binary presence
        self.term_weight = 1.0

    def post_report(self):
        return {
            "room_doc_id": self.room_doc_id,
            "term frequency": self.term_freq,
            "term weight (importance)" : self.term_weight
        }
    
# tokenization -> not really using weights
stemmer = PorterStemmer()
TOKEN_RE = re.compile(r"\b[a-zA-Z0-9]+\b")

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

    space_loc = space.get("location", {}) or {}
    space_lat = space_loc.get("lat", None)
    space_lon = space_loc.get("lon", None)

    docs = []
    rooms = data.get("rooms", []) or []

    for room in rooms:
        room_id = room.get("id", "")
        room_name = room.get("name", "")
        capacity = room.get("capacity", "")
        bitset = room.get("slots_bitset", "")

        features = room.get("features", []) or []
        features = [str(x).strip().lower() for x in features if str(x).strip()]

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
            " ".join(features)
        ]).strip()

        terms = tokenize_and_stem(searchable_text)

        docs.append({
            "uid": uid,
            "terms": terms,
            "store": {
                "uid" : uid,
                "space": {
                    "id": space_id,
                    "name" : space_name,
                    "timezone": space.get("timezone"),
                    "hours": space.get("hours"),
                    "slot_minutes" : space.get("slot_minutes"),
                    "slot_count": space.get("slot_count"),
                    "location": {"lat":space_lat, "lon":space_lon}
                },
                "date" : day,
                "room" : {
                    "id" : room_id,
                    "name" : room_name,
                    "capacity" : capacity,
                    "features": features,
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
            sorted_postings = sorted(postings_dict.values(), key=lambda p: p.room_doc_id)
            posting_obj_map[term] = [p.post_report() for p in sorted_postings]
        
        posting_obj_map = dict(sorted(posting_obj_map.items()))
        out_path = out_folder / f"inverted_index_{part}_run{run_id}.json"
        with open(out_path, 'w', encoding="utf-8") as f:
            json.dump(posting_obj_map, f, ensure_ascii=False)

def make_partial_inverted_indexes(folderpath, out_folder, batch_size=10000):
    #do partial run (probably wont see it but would help for larger expansion)
    partial_index = {p: {} for p in PARTITIONS}
    room_doc_id = 0
    rooms_in_batch =  0
    run_id = 0

    folder = Path(folderpath)
    out_folder = Path(out_folder)
    out_folder.mkdir(parents=True, exist_ok=True)

    docmap_path = out_folder / "roomdocmap.tsv"
    docstore_path = out_folder / "roomdocstore.jsonl"

    print("Creating Study Spot (binary) Index...")

    with open(docmap_path, "w", encoding="utf-8") as docmap, \
        open(docstore_path, "w", encoding="utf-8") as docstore:
        
            for root, _, files in os.walk(folder):
                for file_name in files:
                    if not file_name.lower().endswith(".json"):
                        continue

                    file_path = Path(root) / file_name

                    try:
                        room_docs = extract_room_docs(file_path)
                    except Exception as e:
                        print(f"Skipping {file_path} (parse error): {e}")
                        continue

                    for d in room_docs:
                        uid = d["uid"]
                        terms = d["terms"]

                        # docmap: doc id -> uid
                        docmap.write(f"{room_doc_id}\t{uid}\n")

                        # docstore: meta data for filtering
                        docstore.write(json.dumps(d["store"], ensure_ascii=False) + "\n")

                        for term in terms:
                            part = get_partition(term)
                            index = partial_index[part]

                            if term not in index:
                                index[term] = {}

                            postings_for_term = index[term]
                            if room_doc_id not in postings_for_term:
                                postings_for_term[room_doc_id] = Posting(room_doc_id)

                        room_doc_id += 1
                        rooms_in_batch += 1

                        if rooms_in_batch >= batch_size:
                            flush_partial_index(partial_index, out_folder, run_id)
                            partial_index = {p: {} for p in PARTITIONS}
                            rooms_in_batch = 0
                            run_id += 1
    
    if any(partial_index[p] for p in PARTITIONS):
        flush_partial_index(partial_index, out_folder, run_id)
        run_id += 1

    print(f"Indexing Done, Created {run_id} partial runs.")
    return room_doc_id, run_id

def merge_partial_indexes(out_folder, num_runs):
    out_folder = Path(out_folder)

    for part in PARTITIONS:
        merged = {}

        for run_id in range(num_runs):
            path = out_folder / f"inverted_index_{part}_run{run_id}.json"
            if not path.exists():
                continue

            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            for term, postings in data.items():
                merged.setdefault(term, []).extend(postings)

        if not merged:
            continue

        for term in merged:
            merged[term].sort(key=lambda p: p["room_doc_id"])

        merged = dict(sorted(merged.items()))
        final_path = out_folder / f"inverted_index_{part}.json"
        with open (final_path, "w", encoding="utf-8") as f:
            json.dump(merged, f, ensure_ascii=False)

def index_analytics(out_folder, num_rooms):
    out_folder = Path(out_folder)

    num_unique_tokens = 0
    total_bytes = 0

    for part in PARTITIONS:
        index_path = out_folder / f"inverted_index_{part}.json"
        if index_path.exists():
            with open(index_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            num_unique_tokens += len(data)
            total_bytes += index_path.stat().st_size

    for extra in ["docmap.tsv", "docstore.jsonl"]:
        p = out_folder / extra
        if p.exists():
            total_bytes += p.stat().st_size

    total_kb = round(total_bytes / 1024, 2)

    report_path = out_folder / "index_report.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(
            f"Number of Indexed Rooms: {num_rooms}\n"
            f"Number of Unique tokens: {num_unique_tokens}\n"
            f"Index size on disk (final index + docmap + docstore): {total_kb} KB\n"
        )


def main():
    input_folder = "/home/ebivian/CS125/CS125-Study-Buddies/Study Spots"
    output_folder = "/home/ebivian/CS125/CS125-Study-Buddies/Index"

    batch_size = 10000

    num_docs, num_runs = make_partial_inverted_indexes(input_folder, output_folder, batch_size)
    merge_partial_indexes(output_folder, num_runs)
    index_analytics(output_folder, num_docs)

    print("DONE.")

if __name__ == "__main__":
    main()