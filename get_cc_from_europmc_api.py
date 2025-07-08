import requests

api_url = "https://www.ebi.ac.uk/europepmc/webservices/rest/article/med/"
api_params = "?resultType=core&format=json"


# API query step
def get_europmc_license(pub):

	if pub['epmc_med_id'] is None:
		return None

	else:
		# Build the request URL
		req_url = f"{api_url}{str(pub['epmc_med_id'])}{api_params}"

		try:
			response = requests.get(req_url)
			if response.status_code >= 300:
				print(f"Unsuccessful request status: {response.status_code}")
				return None

			else:
				epmc_data = response.json()
				return epmc_data.get('result', {}).get('license')

		except:
			print("Req. Error occured")
			return None


# Translation step
def translate_europmc_cc_for_eschol_api(europmc_cc):
	if europmc_cc == 'cc0':
		return "https://creativecommons.org/publicdomain/zero/1.0/"
	else:
		return f"https://creativecommons.org/licenses/{europmc_cc[3:]}/4.0/"


# Example pub from sql query
example_pub = {
	'publicaiton_id': 8419,
	'epmc_med_id': 23737753
}

# Send example to API
example_europmc_cc = get_europmc_license(example_pub)
print(example_europmc_cc)

# Translate for eSchol GraphQL, skip if none.
if example_europmc_cc:
	example_europmc_cc = translate_europmc_cc_for_eschol_api(example_europmc_cc)
	print(example_europmc_cc)
