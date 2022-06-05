import requests
import json
from azure.core.exceptions import ClientAuthenticationError

query_data = "Owner"

mgmt_token_uri = "https://login.microsoftonline.com/e18a0c35-c3ed-46f4-8e69-018ca67f8288/oauth2/token"
mgmt_req_headers = {'content-type': 'application/x-www-form-urlencodeds'}
mgmt_req_body= 'grant_type=client_credentials&client_secret=2fG8Q~LNHsgveTV1FGW8Dg9Esme84ALK9Cm2Pdw2&client_id=2b0ce5a8-0146-4b0c-a7ef-eccdb99b555b&resource=https%3A%2F%2Fmanagement.azure.com%2F'
mgmtresponse = requests.request("POST",mgmt_token_uri,headers=mgmt_req_headers,data=mgmt_req_body)
#print("mgmt token is \n" +  str(mgmtresponse.text))

graph_token_uri = "https://login.microsoftonline.com/e18a0c35-c3ed-46f4-8e69-018ca67f8288/oauth2/v2.0/token"
graph_req_headers = {'content-type': 'application/x-www-form-urlencodeds'}
graph_req_body= 'grant_type=client_credentials&client_secret=2fG8Q~LNHsgveTV1FGW8Dg9Esme84ALK9Cm2Pdw2&client_id=2b0ce5a8-0146-4b0c-a7ef-eccdb99b555b&scope=https%3A%2F%2Fgraph.microsoft.com%2F.default'
graphresponse = requests.request("POST",graph_token_uri,headers=graph_req_headers,data=graph_req_body)


#print("graph token is \n" +  str(graphresponse.text))
try:
    g_res_list = []
    role_definition_uri = "https://management.azure.com/subscriptions/6e268af1-b2a7-44a7-9a1a-9025889dbe5d/providers/Microsoft.Authorization/roleDefinitions?api-version=2015-07-01"
    req_headers = {'Authorization': 'Bearer ' + json.loads(mgmtresponse.text)['access_token'], 'Content-Type': 'Application/JSON'}
    res_role_definition = json.loads((requests.get(url=role_definition_uri, headers=req_headers)).text)
    for items in res_role_definition['value']:
        if items['properties']['roleName'] == query_data:
            role_def_id = items['id']
            
    resource_URI = "https://management.azure.com/subscriptions/6e268af1-b2a7-44a7-9a1a-9025889dbe5d/providers/Microsoft.Authorization/roleAssignments?api-version=2015-07-01"
    req_headers = {'Authorization': 'Bearer ' + json.loads(mgmtresponse.text)['access_token'], 'Content-Type': 'Application/JSON'}
    res_response = json.loads((requests.get(url=resource_URI, headers=req_headers)).text)
    #print(res_response)
    for items in res_response['value']:
        if items['properties']['roleDefinitionId'] == role_def_id:
            g_uri = "https://graph.microsoft.com/v1.0/directoryObjects/"+items['properties']['principalId']
            g_headers = {'Authorization': 'Bearer ' + json.loads(graphresponse.text)['access_token'], 'Content-Type': 'Application/JSON'}
            g_res = json.loads((requests.get(url=g_uri,headers=g_headers)).text)
            g_res['scope'] = items['properties']['scope']
            g_res_list.append(g_res)

    print(g_res_list)
except ClientAuthenticationError as ex:
        print(ex.message)
                 
        
    
            
            
