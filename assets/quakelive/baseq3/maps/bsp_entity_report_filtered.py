import os
import struct
import re
import pandas as pd

# Constants for .bsp lump
LUMP_ENTITIES = 0
HEADER_LUMPS = 17

map_whitelist = {'Furious Heights', 'Dismemberment', 'Phrantic', 'Battleforged', 'Vertical Vengeance', 'House of Decay', 'Sinister', 'Hektik', 'Bloodrun', 'Campgrounds', 'Aerowalk', 'Silence', 'Lost World', 'Toxicity', 'Elder', 'Use and Abuse', 'Cure'}

# Prepare entity counter per file
entity_counts = {}
all_entities = set()

# Scan all .bsp files in current dir
for filename in os.listdir():
    if not filename.endswith(".bsp"):
        continue

    mapname = os.path.splitext(os.path.basename(filename))[0]
    clean_mapname = mapname.replace("_", " ").title()

    if clean_mapname not in map_whitelist:
        continue

    with open(filename, "rb") as f:
        if f.read(4) != b"IBSP":
            continue

        version = struct.unpack("i", f.read(4))[0]
        if version not in (0x2E, 0x2F):  # Quake III and Quake Live
            continue

        lumps = [struct.unpack("ii", f.read(8)) for _ in range(HEADER_LUMPS)]
        entities_offset, entities_length = lumps[LUMP_ENTITIES]

        if entities_length <= 0:
            continue

        f.seek(entities_offset)
        entity_str = f.read(entities_length).decode('latin1', errors='ignore')

        matches = re.findall(r'\{(.*?)\}', entity_str, re.DOTALL)
        from collections import Counter
        counter = Counter()

        for match in matches:
            kv_pairs = re.findall(r'"([^"]+)"\s+"([^"]+)"', match)
            entity_dict = {k: v for k, v in kv_pairs}
            classname = entity_dict.get("classname")
            if classname:
                counter[classname] += 1
                all_entities.add(classname)

        entity_counts[clean_mapname] = counter

# Prepare HTML table using pandas
all_entities = sorted(all_entities)
rows = []
for mapname, counts in entity_counts.items():
    row = {"Map": mapname}
    for ent in all_entities:
        row[ent] = counts.get(ent, "")
    rows.append(row)

df = pd.DataFrame(rows)
df.to_html("bsp_entity_report.html", index=False)
print("Report saved to bsp_entity_report.html")

