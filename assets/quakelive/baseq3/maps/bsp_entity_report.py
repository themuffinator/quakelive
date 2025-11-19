import os
import struct
import re
import html
from collections import defaultdict, Counter
import pandas as pd

# Constants for .bsp lump
LUMP_ENTITIES = 0
HEADER_LUMPS = 17
LUMP_HEADER_FORMAT = "ii"  # offset, length

# Prepare entity counter per file
entity_counts = {}
all_entities = set()

# Scan all .bsp files in current dir
for filename in os.listdir():
    if not filename.endswith(".bsp"):
        continue

    with open(filename, "rb") as f:
        f.seek(0)
        magic = f.read(4)
        if magic != b"IBSP":
            continue  # Not a Quake III BSP

        version = struct.unpack("i", f.read(4))[0]
        if version not in (0x2E, 0x2F):  # Support both Q3 (46) and QL (47)
            continue

        # Read lump directory
        lumps = [struct.unpack("ii", f.read(8)) for _ in range(HEADER_LUMPS)]
        entities_offset, entities_length = lumps[LUMP_ENTITIES]

        # Read entity string
        f.seek(entities_offset)
        entity_str = f.read(entities_length).decode('latin1', errors='ignore')

        # Find all entities
        matches = re.findall(r'\{(.*?)\}', entity_str, re.DOTALL)
        counter = Counter()

        for match in matches:
            kv_pairs = re.findall(r'"([^"]+)"\s+"([^"]+)"', match)
            entity_dict = {k: v for k, v in kv_pairs}
            classname = entity_dict.get("classname")
            if classname:
                counter[classname] += 1
                all_entities.add(classname)

        entity_counts[filename] = counter

# Prepare HTML table using pandas
all_entities = sorted(all_entities)
rows = []
for mapname, counts in entity_counts.items():
    row = {"Map": mapname}
    for ent in all_entities:
        val = counts.get(ent)
        row[ent] = val if val else ""
    rows.append(row)

df = pd.DataFrame(rows)
df.to_html("bsp_entity_report.html", index=False)
print("Report saved to bsp_entity_report.html")
