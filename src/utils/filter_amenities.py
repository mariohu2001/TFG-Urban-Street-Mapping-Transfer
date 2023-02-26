import json


json_file = open("./amenity_values.json","r",encoding="UTF-8")


json_full_values = json.loads(json_file.read())

valid_amenities = []
not_valid_amenities = []


for amenity in json_full_values["data"]:
    if amenity["in_wiki"] == True:
        valid_amenities.append(amenity)
    else:
        not_valid_amenities.append(amenity)


json_file.close()

json_output = json.dumps(valid_amenities,indent=4)
with open("./wiki_amenities.json","w",encoding="UTF-8") as output:
    output.write(json_output)
with open("./not_valid_wiki.json","w",encoding="UTF-8") as output:
    output.write(json.dumps(not_valid_amenities, indent=4))

print(f"Válidas: {len(valid_amenities)} Inválidas: {len(not_valid_amenities)}")


