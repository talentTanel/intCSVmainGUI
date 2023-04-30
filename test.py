import json

# read the existing JSON data from the file
with open('points.json', 'r') as f:
    data = json.load(f)

# add a new item to the list
new_item = {"id": 3, "name": "Beach", "comment": "Sand"}
data.append(new_item)

# write the updated JSON data back to the file
with open('points.json', 'w') as f:
    json.dump(data, f)