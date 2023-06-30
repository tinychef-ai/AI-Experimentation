import pandas as pd
import pysolr
import csv

def convert_to_list(val):
    lst = []

    if type(val) is str:
        lst = val.split(',')

    for i in range(len(lst)):
        lst[i] = lst[i].strip()

    return lst


def index_recipes(recipe_file):
    solr = pysolr.Solr('http://localhost:8983/api/collections/recipesv4',
                       always_commit=True, timeout=10)

    df = pd.read_csv(recipe_file)
    df = df[(df["status"] == "active") & (df["languagesSupported"] == "en")]
    row_count = 0
    for index, row in df.iterrows():
        # print("indexing...", row["name"])
        solr.add([{"id": row["guid"],
                   "name": row["name"],
                   "cuisines": convert_to_list(row["cuisines"]),
                   "mealTypes": convert_to_list(row["mealTypes"]),
                   "diet_preferences": convert_to_list(row["diet_preferences"]),
                   "majorIngredients": convert_to_list(row["majorIngredients"]),
                   "descriptors": convert_to_list(row["descriptors"]),
                   "dishTypes": convert_to_list(row["dishTypes"]),
                   "skillLevels": convert_to_list(row["skillLevels"]),
                   "description": row["description"]}])

        row_count += 1
        if row_count % 100 == 0:
            print("indexed", row_count, "rows")


def generate_search_results(search_result_file1, search_result_file2):
    solr = pysolr.Solr('http://localhost:8983/solr/recipesv4',
                       always_commit=True, timeout=10)

    with open(search_result_file1) as input_file:
        with open(search_result_file2, "w") as output_file:
            reader = csv.reader(input_file)
            writer = csv.writer(output_file)

            headers = next(reader, None)
            output_header = ["Search_Text"]
            for i in range(1, 11):
                output_header.append("Result_" + str(i))

            writer.writerow(output_header)
            for row in reader:
                query = row[0]
                recipe_names = search_recipe(solr, query)
                output_row = [query]
                output_row.extend(recipe_names)
                writer.writerow(output_row)


def search_recipe(solr, query):

    results = solr.search(query, **{
        "defType": "dismax",
        "q.op": "OR",
        "qf" : "name description cuisines mealTypes diet_preferences majorIngredients dishTypes skillLevels descriptors",
        "pf" : "name description",
        # "mm" : "2<60%",
        "row" : "10"
    })

    response = []
    for result in results:
        response.append(result["name"])

    return response


# index_recipes("/Users/agaramit/Downloads/Recipe Tag Dump - Sheet1.csv")

# query_list = ["vegetarian soups",
#               "soups",
#               "vegetarian soup",
#               "soup",
#               "south indian breakfast",
#               "paneer",
#               "barfee",
#               "barfi",
#               "burfi",
#               "korma",
#               "veg korma",
#               "veg kurma",
#               "veg kurmaa"]
#
# for query in query_list:
#     print(query, search_recipe(query))

generate_search_results("/Users/agaramit/Downloads/Search Results - Skill_app_searches_1_sample.csv",
                        "/Users/agaramit/Downloads/Search Results - solr_nomm_sample.csv")
