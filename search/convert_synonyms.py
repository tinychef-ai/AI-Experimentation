import json

with open("/Users/agaramit/Downloads/Synonyms.json") as input_file:
    json_obj = json.load(input_file)

    for key in json_obj.keys():
        for val in json_obj[key]:
            print(val, ',', key)
