import csv
import random
import json

with open("/Users/agaramit/Downloads/query_corrections.csv") as input_file:
    with open("/Users/agaramit/Downloads/query_corrections.train.jsonl", "w") as train_file:
        with open("/Users/agaramit/Downloads/query_corrections.test.jsonl", "w") as test_file:
            reader = csv.reader(input_file)
            header = next(reader, None)

            for row in reader:
                line = {"prompt": "canonicalize query \"" + row[0] + "\"",
                        "completion": row[1]}
                if random.random() <= 0.7:
                    train_file.write(json.dumps(line))
                    train_file.write("\n")
                else:
                    test_file.write(json.dumps(line))
                    test_file.write("\n")
