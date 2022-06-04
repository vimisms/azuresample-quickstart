import requests
import json
mgmt_token_uri = "https://login.microsoftonline.com/e18a0c35-c3ed-46f4-8e69-018ca67f8288/oauth2/token"
mgmt_req_headers = {'content-type': 'application/x-www-form-urlencodeds'}
#graph_req_body = 'grant_type=client_credentials&client_id=2b0ce5a8-0146-4b0c-a7ef-eccdb99b555b&scope=https%3A%2F%2Fgraph.microsoft.com%2F.default&client_secret=' + str(bank_secret)

mgmt_req_body= 'grant_type=client_credentials&client_secret=2fG8Q~LNHsgveTV1FGW8Dg9Esme84ALK9Cm2Pdw2&client_id=2b0ce5a8-0146-4b0c-a7ef-eccdb99b555b&resource=https%3A%2F%2Fmanagement.azure.com%2F'

response = requests.request("POST",mgmt_token_uri,headers=mgmt_req_headers,data=mgmt_req_body)

print("mgmt token is \n" +  json.loads(response.text)['access_token'])

