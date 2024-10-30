import datetime
import csv
from pprint import pprint as pp
import requests

import program_setup

# ================================
# LOGGING
run_time = datetime.datetime.now().replace(microsecond=0).isoformat()
log_file = f"output/europmc-cc-updates-{run_time}.csv"
log_fields = []


def create_log():
    with open(log_file, 'w') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=log_fields)
        writer.writeheader()


def write_log_row(lr):
    with open(log_file, 'a') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=log_fields)
        writer.writerow(lr)


# ================================
def main():
    create_log()
    args = program_setup.process_args()
    config = program_setup.get_config()

    # Get and prep input
    input_items = list(csv.DictReader(open(args.input_file)))
    prep_input_data(input_items)

    # loop the data, send reqs:
    update_eschol_api(args, config, input_items)

    exit(0)


def prep_input_data(input_items):
    # Remove input data without CC values
    input_items = [i for i in input_items
                   if i['epmc_api_licence'] is not None
                   and i['epmc_api_licence'] != 'cc0']

    # prep the EuroPMC licences for URL format
    for i in input_items:
        i['graphql_cc'] = f"https://creativecommons.org/licenses/{i['epmc_api_licence'][3:]}/4.0/"


def update_eschol_api(args, config, input_items):

    eschol_api = program_setup.get_eschol_api_connection(args.connection, config)

    mutation = "mutation updateRights($input: UpdateRightsInput!){ updateRights(input: $input) { message } }"
    check = 'query { item(id:"ark:/13030/qt001027fb") { id, title, rights } }'

    # Set headers, add the cookie for DEV or QA
    headers = {'Content-Type': 'application/json',
               'Privileged': eschol_api['priv_key']}

    if args.connection == 'QA' or args.connection == 'DEV':
        headers['Cookie'] = f"ACCESS_COOKIE={eschol_api['cookie']}"

    for item in input_items:
        print(f"Processing: {item['escholID']}")
        print(eschol_api['url'])
        pp(headers)
        mutation_vars = get_mutation_vars(item)

        response = requests.get(
            url=eschol_api['url'],
            headers=headers,
            json={"query": check}
        )

        # send the query
        # response = requests.post(
        #     url=eschol_api['url'],
        #     headers=headers,
        #     json={"query": mutation,
        #           "variables": mutation_vars}
        # )

        print(response.status_code)
        if response.status_code == 200:
            print(response.reason)

        exit()


def get_mutation_vars(item):
    return '{ "input": { "id":"' + item['escholID'] + '", "rights":"' + item['graphql_cc'] + '"} }'


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

# {
#   "input": {
#   	"id":"qt12345678",
#   	"rights":"https://creativecommons.org/licenses/by-nc-sa/4.0/"
#   }
# }
