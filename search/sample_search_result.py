import csv
import random


def sample_search_results(search_result_file, sample_result_file):
    query = {}
    with open(sample_result_file, "w") as output_file:
        line = 0
        error_count = 0
        with open(search_result_file) as input_file:
            reader = csv.reader(input_file)
            writer = csv.writer(output_file)
            headers = next(reader, None)
            writer.writerow(headers)
            for row in reader:
                line=line+1
                if row[0] in query.keys():
                    continue
                if random.random()<0.8:
                    writer.writerow(row)
                    query[row[0]] = ""


sample_search_results("/Users/agaramit/Downloads/Search Results - Skill_Sheet1.csv",
                       "/Users/agaramit/Downloads/Search Results - Skill_Sheet1_sample.csv")
