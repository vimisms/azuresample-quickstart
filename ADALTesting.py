import requests
import json


data_sub_policy={}
mgmt_token_uri = "https://login.microsoftonline.com/e18a0c35-c3ed-46f4-8e69-018ca67f8288/oauth2/token"
mgmt_req_headers = {'content-type': 'application/x-www-form-urlencodeds'}
#graph_req_body = 'grant_type=client_credentials&client_id=2b0ce5a8-0146-4b0c-a7ef-eccdb99b555b&scope=https%3A%2F%2Fgraph.microsoft.com%2F.default&client_secret=' + str(bank_secret)

mgmt_req_body = 'grant_type=client_credentials&client_secret=2fG8Q~LNHsgveTV1FGW8Dg9Esme84ALK9Cm2Pdw2&client_id=2b0ce5a8-0146-4b0c-a7ef-eccdb99b555b&resource=https%3A%2F%2Fmanagement.azure.com%2F'

response = requests.request(
    "POST", mgmt_token_uri, headers=mgmt_req_headers, data=mgmt_req_body)

#print("mgmt token is \n" + json.loads(response.text)['access_token'])

sub_policy_state_uri = "https://management.azure.com/subscriptions/6e268af1-b2a7-44a7-9a1a-9025889dbe5d/providers/Microsoft.PolicyInsights/policyStates/latest/queryResults?api-version=2019-10-01"
req_headers = {'Authorization': 'Bearer ' +
               json.loads(response.text)['access_token'], 'Content-Type': 'Application/JSON'}
res_sub_policy = json.loads(requests.post(url=sub_policy_state_uri, headers=req_headers).text)
print(res_sub_policy)
for items in res_sub_policy['value']:
    if items['complianceState'] == 'NonCompliant':
        data_sub_policy['policyAssignmentName'] = items['policyAssignmentName']
        data_sub_policy['policyDefinitionAction'] = items['policyDefinitionAction']
        data_sub_policy['Resource'] = (items['resourceId']).split("/")[7]
        data_sub_policy['policySetDefinitionCategory'] = items['policySetDefinitionCategory']
