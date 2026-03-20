import json

# Teeno files load karo
with open('ayurvedic_database.json', 'r', encoding='utf-8') as f:
    db1 = json.load(f)

with open('plant_details_4plants.json', 'r', encoding='utf-8') as f:
    db2 = json.load(f)

with open('plants_detail.json', 'r', encoding='utf-8') as f:
    db3 = json.load(f)

# Merge karo
merged = {}
merged.update(db1)
merged.update(db2)
merged.update(db3)

with open('merged_database.json', 'w', encoding='utf-8') as f:
    json.dump(merged, f, ensure_ascii=False, indent=2)

print("Merge complete! Total entries:", len(merged))