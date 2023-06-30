import csv
import json
import constants


def parse_search_results(search_result_file, has_openai_responses=False):
    query_results = {}
    openai_results = {}
    with open(search_result_file) as input_file:
        reader = csv.reader(input_file)
        headers = next(reader, None)

        for row in reader:
            query = row[0].strip().lower()
            results = []
            start_index = 1

            if has_openai_responses:
                openai_query_responses = {}
                start_index = 2
                for v in row[1].split(','):
                    openai_query_responses[v.strip().lower()] = None
                openai_results[query] = openai_query_responses

            for i in range(start_index, constants.TOP_K + start_index):
                if row[i] and len((row[i]).strip()) > 0:
                    results.append(row[i].strip().lower())
                else:
                    break

            query_results[query] = results

    return query_results, openai_results


def parse_search_result_evals(search_result_eval_file):
    search_result_evals = {}
    with open(search_result_eval_file) as input_file:
        for line in input_file:
            json_obj = json.loads(line)
            query = json_obj[0].strip().lower()
            result_evals = {}

            for i in range(1, len(json_obj)):
                if json_obj[i]["parse_success"]:
                    json_obj[i]["recipe_name"] = json_obj[i]["recipe_name"].strip().lower()
                    json_obj[i]["position"] = i
                    if json_obj[i]["recipe_name"] not in result_evals.keys():
                        result_evals[json_obj[i]["recipe_name"]] = json_obj[i]

            search_result_evals[query] = result_evals

    return search_result_evals


def parse_query_frequencies(query_frequency_file):
    query_frequencies = {}
    with open(query_frequency_file) as input_file:
        reader = csv.reader(input_file)
        headers = next(reader, None)

        for row in reader:
            query = row[0].strip().lower()
            frequency = int(row[1].strip())

            query_frequencies[query] = frequency

    return query_frequencies


def parse_query_evals(query_eval_file):
    query_evals = {}
    with open(query_eval_file) as input_file:
        for line in input_file:
            json_obj = json.loads(line.strip())
            if json_obj["parse_success"] is False:
                continue
            query = json_obj["query"].strip().lower()
            valid = True if json_obj["query_valid"] == "yes" else False
            query_evals[query] = valid

    return query_evals