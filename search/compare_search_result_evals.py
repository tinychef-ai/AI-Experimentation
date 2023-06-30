import json
import csv
import sys
import re
import constants
import file_parser as fp


def get_match_counts(result_eval):
    response_count = [0] * constants.TOP_K
    match_count = [0] * constants.TOP_K
    atleast_one_match = 0

    for recipe_name in result_eval.keys():
        pos = result_eval[recipe_name]["position"]-1
        response_count[pos] += 1
        assert(response_count[pos] == 1)
        if result_eval[recipe_name]["overall_match"] == "yes":
            atleast_one_match = 1
            match_count[pos] += 1
            assert(match_count[pos] == 1)

    return response_count, match_count, atleast_one_match


def add_list(lst1, lst2, weight2=1):
    assert(len(lst1) == len(lst2))
    assert(weight2 >= 1)

    lst = []
    for i in range(len(lst1)):
        lst.append(lst1[i] + lst2[i] * weight2)

    return lst


class Stats:
    query_count = 0
    query_recipe_match_count = 0
    query_recipe_eval_match_count = 0
    weighted_query_count = 0
    weighted_query_recipe_match_count = 0
    weighted_query_recipe_eval_match_count = 0

    response_count1 = [0] * constants.TOP_K
    response_count2 = [0] * constants.TOP_K
    match_count1 = [0] * constants.TOP_K
    match_count2 = [0] * constants.TOP_K
    atleast_one_match_count1 = 0
    atleast_one_match_count2 = 0

    weighted_response_count1 = [0] * constants.TOP_K
    weighted_response_count2 = [0] * constants.TOP_K
    weighted_match_count1 = [0] * constants.TOP_K
    weighted_match_count2 = [0] * constants.TOP_K
    weighted_atleast_one_match_count1 = 0
    weighted_atleast_one_match_count2 = 0


def compare_search_result_evals(search_result_eval_file1,
                                search_result_eval_file2,
                                query_frequency_file,
                                query_eval_file=None):
    search_result_eval1 = fp.parse_search_result_evals(search_result_eval_file1)
    search_result_eval2 = fp.parse_search_result_evals(search_result_eval_file2)
    query_frequencies = fp.parse_query_frequencies(query_frequency_file)
    query_evals = fp.parse_query_evals(query_eval_file) if query_eval_file is not None else None

    writer = csv.writer(sys.stdout)

    frequency_cutoffs = [None, 1, 2]
    query_length_cutoffs = [None, 1, 2, 3]
    bucket_stats = {}

    for frequency_cutoff in frequency_cutoffs:
        for query_length_cutoff in query_length_cutoffs:
            bucket = tuple([frequency_cutoff, query_length_cutoff])
            bucket_stats[bucket] = Stats()

    for query in search_result_eval1.keys():
        if query in search_result_eval2.keys():
            if query_evals is not None and (query not in query_evals.keys() or query_evals[query] is False):
                continue

            frequency = query_frequencies[query] if query in query_frequencies.keys() else 1
            query_length = len(re.findall(r'\w+', query))

            selected_frequency_cutoffs = [None]
            selected_query_length_cutoffs = [None]
            selected_buckets = []

            for frequency_cutoff in reversed(frequency_cutoffs):
                if frequency_cutoff is not None and frequency >= frequency_cutoff:
                    selected_frequency_cutoffs.append(frequency_cutoff)
                    break

            for query_length_cutoff in reversed(query_length_cutoffs):
                if query_length_cutoff is not None and query_length >= query_length_cutoff:
                    selected_query_length_cutoffs.append(query_length_cutoff)
                    break

            for selected_frequency_cutoff in selected_frequency_cutoffs:
                for selected_query_length_cutoff in selected_query_length_cutoffs:
                    selected_buckets.append(tuple([selected_frequency_cutoff, selected_query_length_cutoff]))

            for selected_bucket in selected_buckets:
                bucket_stats[selected_bucket].query_count += 1
                bucket_stats[selected_bucket].weighted_query_count += frequency

                rc1, mc1, atleast_one_m1 = get_match_counts(search_result_eval1[query])
                rc2, mc2, atleast_one_m2 = get_match_counts(search_result_eval2[query])

                bucket_stats[selected_bucket].response_count1 = add_list(bucket_stats[selected_bucket].response_count1, rc1)
                bucket_stats[selected_bucket].match_count1 = add_list(bucket_stats[selected_bucket].match_count1, mc1)
                bucket_stats[selected_bucket].atleast_one_match_count1 += atleast_one_m1
                bucket_stats[selected_bucket].weighted_response_count1 = add_list(bucket_stats[selected_bucket].weighted_response_count1, rc1, frequency)
                bucket_stats[selected_bucket].weighted_match_count1 = add_list(bucket_stats[selected_bucket].weighted_match_count1, mc1, frequency)
                bucket_stats[selected_bucket].weighted_atleast_one_match_count1 += atleast_one_m1 * frequency

                bucket_stats[selected_bucket].response_count2 = add_list(bucket_stats[selected_bucket].response_count2, rc2)
                bucket_stats[selected_bucket].match_count2 = add_list(bucket_stats[selected_bucket].match_count2, mc2)
                bucket_stats[selected_bucket].atleast_one_match_count2 += atleast_one_m2
                bucket_stats[selected_bucket].weighted_response_count2 = add_list(bucket_stats[selected_bucket].weighted_response_count2, rc2, frequency)
                bucket_stats[selected_bucket].weighted_match_count2 = add_list(bucket_stats[selected_bucket].weighted_match_count2, mc2, frequency)
                bucket_stats[selected_bucket].weighted_atleast_one_match_count2 += atleast_one_m2 * frequency

            for recipe_name in search_result_eval1[query].keys():
                if recipe_name in search_result_eval2[query].keys():
                    for selected_bucket in selected_buckets:
                        bucket_stats[selected_bucket].query_recipe_match_count += 1
                        bucket_stats[selected_bucket].weighted_query_recipe_match_count += frequency

                    if search_result_eval1[query][recipe_name]["overall_match"] != \
                            search_result_eval2[query][recipe_name]["overall_match"]:
                        writer.writerow(["evaluation verdict flipped", query, recipe_name,
                                         search_result_eval1[query][recipe_name]["overall_match"],
                                         search_result_eval1[query][recipe_name]["overall_match_reason"],
                                         search_result_eval2[query][recipe_name]["overall_match"],
                                         search_result_eval2[query][recipe_name]["overall_match_reason"]])
                    else:
                        for selected_bucket in selected_buckets:
                            bucket_stats[selected_bucket].query_recipe_eval_match_count += 1
                            bucket_stats[selected_bucket].weighted_query_recipe_eval_match_count += frequency

    for bucket in bucket_stats.keys():
        print("\nbucket:", bucket)
        print("query_recipe_match_count:", bucket_stats[bucket].query_recipe_match_count)
        print("query_recipe_eval_match_count:", bucket_stats[bucket].query_recipe_eval_match_count)
        print("query_count:", bucket_stats[bucket].query_count)
        print("response_count1:", bucket_stats[bucket].response_count1)
        print("match_count1:", bucket_stats[bucket].match_count1)
        print("atleast_one_match_count1:" , bucket_stats[bucket].atleast_one_match_count1)
        print("response_count2:", bucket_stats[bucket].response_count2)
        print("match_count2:", bucket_stats[bucket].match_count2)
        print("atleast_one_match_count2:" , bucket_stats[bucket].atleast_one_match_count2)
        print("weighted_query_recipe_match_count:", bucket_stats[bucket].weighted_query_recipe_match_count)
        print("weighted_query_recipe_eval_match_count:", bucket_stats[bucket].weighted_query_recipe_eval_match_count)
        print("weighted_query_count:", bucket_stats[bucket].weighted_query_count)
        print("weighted_response_count1:", bucket_stats[bucket].weighted_response_count1)
        print("weighted_match_count1:", bucket_stats[bucket].weighted_match_count1)
        print("weighted_atleast_one_match_count1:" , bucket_stats[bucket].weighted_atleast_one_match_count1)
        print("weighted_response_count2:", bucket_stats[bucket].weighted_response_count2)
        print("weighted_match_count2:", bucket_stats[bucket].weighted_match_count2)
        print("weighted_atleast_one_match_count2:" , bucket_stats[bucket].weighted_atleast_one_match_count2)
        print("overlap ratio:", (bucket_stats[bucket].weighted_query_recipe_match_count/
                                 sum(bucket_stats[bucket].weighted_response_count2)))


def main():
    # compare_search_result_evals("/Users/agaramit/Downloads/Search Results - Skill_Sheet1_sample_eval.json",
    #                             "/Users/agaramit/Downloads/Search Results - Skill_app_searches_without_openai_sample_eval.json",
    #                             "/Users/agaramit/Downloads/Search Results - Skill_frequencies.csv")

    # compare_search_result_evals("/Users/agaramit/Downloads/Search Results - Skill_app_searches_without_openai_sample_eval.json",
    #                             "/Users/agaramit/Downloads/Search Results - Skill_app_searches_1_sample_eval.json",
    #                             "/Users/agaramit/Downloads/Search Results - Skill_frequencies.csv")

    # compare_search_result_evals("/Users/agaramit/Downloads/Search Results - Skill_Sheet1_sample_eval.json",
    #                             "/Users/agaramit/Downloads/Search Results - openai_faiss_sample_eval.json",
    #                             "/Users/agaramit/Downloads/Search Results - Skill_frequencies.csv")

    # compare_search_result_evals("/Users/agaramit/Downloads/Search Results - Skill_Sheet1_sample_eval.json",
    #                             "/Users/agaramit/Downloads/Search Results - openai_faiss5_1_sample_eval.json",
    #                             "/Users/agaramit/Downloads/Search Results - Skill_frequencies.csv")

    # compare_search_result_evals("/Users/agaramit/Downloads/Search Results - Skill_Sheet1_sample_eval.json",
    #                             "/Users/agaramit/Downloads/Search Results - solr_nomm_openai_sample_eval2.json",
    #                             "/Users/agaramit/Downloads/Search Results - Skill_frequencies.csv")
    # "/Users/agaramit/Downloads/query_eval_man_ovr.json")

    # compare_search_result_evals("/Users/agaramit/Downloads/Search Results - Skill_Sheet1_sample_eval.json",
    #                             "/Users/agaramit/Downloads/Search Results - openai_faiss5_expq1_sample_eval.json",
    #                             "/Users/agaramit/Downloads/Search Results - Skill_frequencies.csv")

    compare_search_result_evals("/Users/agaramit/Downloads/Search Results - Skill_Sheet1_sample_eval.json",
                                "/Users/agaramit/Downloads/Search Results - openai_faiss5_expq1_openai_sample_eval.json",
                                "/Users/agaramit/Downloads/Search Results - Skill_frequencies.csv")


if __name__ == '__main__':
    main()

