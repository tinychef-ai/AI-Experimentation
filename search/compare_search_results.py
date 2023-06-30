import json
import csv
import sys
import unicodedata
import file_parser as fp
import constants


def detect_lang_dist(search_results):
    lang_dist = {}

    for k in search_results.keys():
        if len(search_results[k]) > 0:
            lang = unicodedata.name(search_results[k][0][0]).split(' ')[0]
            if lang not in lang_dist.keys():
                lang_dist[lang] = 0

            lang_dist[lang] = lang_dist[lang] + 1

    return lang_dist


def compare_search_results(search_result_file1,
                           search_result_file2, has_openai_results2):
    search_results1, _ = fp.parse_search_results(search_result_file1, False)
    search_results2, openai_results2 = fp.parse_search_results(search_result_file2, has_openai_results2)

    query_count = 0
    missing_query_count = 0
    results_increase_count = 0
    results_decrease_count = 0
    position_mismatch_count = [0] * constants.TOP_K
    content_mismatch_count = [0] * constants.TOP_K
    query_count_with_position_mismatch = 0
    query_count_with_content_mismatch = 0
    openai_response_as_top_response_count = 0

    results_count1 = 0
    results_count2 = 0
    lang_dist1 = detect_lang_dist(search_results1)
    lang_dist2 = detect_lang_dist(search_results2)

    writer = csv.writer(sys.stdout)

    for k in search_results1.keys():
        if len(search_results1[k]) > 0 and "DEVANAGARI" in unicodedata.name(search_results1[k][0][0]):
            continue

        query_count = query_count + 1
        if k not in search_results2.keys():
            missing_query_count = missing_query_count + 1
            writer.writerow([None, None, None, k])
            continue

        results_count1 = results_count1 + len(search_results1[k])
        results_count2 = results_count2 + len(search_results2[k])

        results_inc_dec = 0
        if len(search_results1[k]) > len(search_results2[k]):
            results_decrease_count = results_decrease_count + 1
            results_inc_dec = -1
        elif len(search_results1[k]) < len(search_results2[k]):
            results_increase_count = results_increase_count + 1
            results_inc_dec = 1

        position_mismatch = False
        for i in range(len(search_results1[k])):
            if i >= len(search_results2[k]):
                break

            if search_results1[k][i] != search_results2[k][i]:
                position_mismatch_count[i] = position_mismatch_count[i] + 1
                position_mismatch = True

        content_mismatch = False
        val2_dict = dict.fromkeys(search_results2[k])
        for index, val1 in enumerate(search_results1[k]):
            if val1 not in val2_dict:
                content_mismatch = True
                content_mismatch_count[index] = content_mismatch_count[index] + 1

        if position_mismatch:
            query_count_with_position_mismatch = query_count_with_position_mismatch + 1

        if content_mismatch:
            query_count_with_content_mismatch = query_count_with_content_mismatch + 1

        if k in openai_results2.keys() and \
                len(search_results2[k]) > 0 and \
                search_results2[k][0] in openai_results2[k]:
            openai_response_as_top_response_count = openai_response_as_top_response_count + 1

        writer.writerow(
            [results_inc_dec, position_mismatch, content_mismatch, k, search_results1[k], search_results2[k]])

    print("lang_dist1:", lang_dist1)
    print("lang_dist2:", lang_dist2)
    print("query_count:", query_count)
    print("results_count1:", results_count1)
    print("results_count2:", results_count2)
    print("missing_query_count:", missing_query_count)
    print("results_increase_count:", results_increase_count)
    print("results_decrease_count:", results_decrease_count)
    print("position_mismatch_count:", position_mismatch_count)
    print("content_mismatch_count:", content_mismatch_count)
    print("query_count_with_position_mismatch:", query_count_with_position_mismatch)
    print("query_count_with_content_mismatch:", query_count_with_content_mismatch)
    print("openai_response_as_top_response_count:", openai_response_as_top_response_count)


def main():
    # compare_search_results("/Users/agaramit/Downloads/Search Results - Skill_Sheet1_sample.csv",
    #                        "/Users/agaramit/Downloads/Search Results - Skill_app_searches.csv", True)

    # compare_search_results("/Users/agaramit/Downloads/Search Results - Skill_app_searches_without_openai_sample.csv",
    #                        "/Users/agaramit/Downloads/Search Results - Skill_app_searches.csv", True)

    # compare_search_results("/Users/agaramit/Downloads/Search Results - Skill_Sheet1_sample.csv",
    #                        "/Users/agaramit/Downloads/Search Results - Skill_app_searches_without_openai_sample.csv", False)

    # compare_search_results("/Users/agaramit/Downloads/Search Results - openai_faiss5_1_sample.csv",
    #                        "/Users/agaramit/Downloads/Search Results - openai_faiss5_2_sample.csv", False)

    compare_search_results("/Users/agaramit/Downloads/Search Results - Skill_Sheet1_sample.csv",
                           "/Users/agaramit/Downloads/Search Results - openai_faiss5_expq1_sample.csv", False)


if __name__ == '__main__':
    main()
