import datetime
import csv
from pprint import pprint as pp
import requests

import program_setup

# Batch vars
last_index_file = "last_index_processed.txt"
batch_size = 1000
throttle_secs = 20


# ================================
def main():
    create_log()
    args = program_setup.process_args()
    config = program_setup.get_config()

    # Get and prep input
    input_items = list(csv.DictReader(open(args.input_file)))
    prep_input_data(input_items)

    # Determine the start and end indexes
    start_index = int(open(last_index_file).read())
    end_index = start_index + batch_size
    print(f"Submitting batch: {start_index} - {end_index}")

    # Limit to current batch for uploading
    input_items = input_items[start_index:end_index]

    # loop the data, send reqs:
    update_eschol_api(args, config, input_items, start_index)

    print("Batch finished. Exiting.")


# Quick tool for adding CC licence strings
def prep_input_data(input_items):
    # Remove input data without CC values
    input_items = [i for i in input_items
                   if i['epmc_api_licence'] is not None
                   and i['epmc_api_licence'] != 'cc0']

    return input_items


def update_eschol_api(args, config, input_items, current_index):

    eschol_api = program_setup.get_eschol_api_connection(args.connection, config)

    test_query = 'query { item(id:"ark:/13030/qt001027fb") { id, title, rights } }'
    test_query_with_vars = 'query getItem($input_id: ID!){ item(id:$input_id) { id, title, rights } }'
    test_vars = {'input_id': 'ark:/13030/qt001027fb'}

    mutation = "mutation updateRights($input: UpdateRightsInput!){ updateRights(input: $input) { message } }"

    # Set cookies and headers
    if args.connection == 'QA':
        cookies = dict(ACCESS_COOKIE=eschol_api['cookie'])
        headers = dict(Priviliged=eschol_api['priv_key'])
    else:
        headers, cookies = {}, {}

    for item in input_items:
        print(f"Submitting: {item['escholID']}")

        mutation_vars = get_mutation_vars(item)

        response = requests.post(
            url=eschol_api['url'],
            headers=headers,
            cookies=cookies,
            json={"query": test_query_with_vars,
                  "variables": test_vars}
        )

        # Print response
        print(response.status_code)
        print(response.reason)
        print(response.json())

        # Logging
        item.update({'response_code': response.status_code,
                     'submission_index': current_index})
        write_log_row(item)

        current_index += 1
        with open(last_index_file, "w") as lif:
            lif.write(current_index)

        exit()


def get_mutation_vars(item):
    item_vars = {
        "input": {
            "id": f"ark:/13030/{item['escholID']}",
            "rights": f"https://creativecommons.org/licenses/{item['epmc_api_licence'][3:]}/4.0/"
        }
    }
    return item_vars


# ================================
# LOGGING
run_time = datetime.datetime.now().replace(microsecond=0).isoformat()
log_file = f"output/europmc-cc-updates-{run_time}.csv"
log_fields = ["escholID", "elementsID", "epmc_med_id", "epmc_api_licence", "response_code", "submission_index"]


def create_log():
    with open(log_file, 'w') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=log_fields)
        writer.writeheader()


def write_log_row(lr):
    with open(log_file, 'a') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=log_fields)
        writer.writerow(lr)


# ================================
if __name__ == '__main__':
    main()

# Mutation reference
# mutation {
#   updateRights(
#     input: {
#     	id: "qt12345678"
#     	rights: "https://creativecommons.org/licenses/by-nc/4.0/"
#   	}
#   )
#   {
#     message
#   }
# }

# Mutation with Vars:

# mutation updateRights($input: UpdateRightsInput!){
#   updateRights(input: $input)
#   { message }
# }

# Vars:
# {
#   "input": {
#   	"id":"qt12345678",
#   	"rights":"https://creativecommons.org/licenses/by-nc-sa/4.0/"
#   }
# }
