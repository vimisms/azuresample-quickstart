from datetime import date, timedelta
from urllib import response
import os
import requests
import json
import jinja2
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential, AzureCliCredential
from azure.core.exceptions import ClientAuthenticationError
import random

app = Flask(__name__)


vault_uri = "https://neo-rbac-webapp-kv.vault.azure.net/"
credential = DefaultAzureCredential()
client = SecretClient(vault_url=vault_uri, credential=credential)
secret_name = '2b0ce5a8-0146-4b0c-a7ef-eccdb99b555b'
bank_secret = client.get_secret(secret_name)
print("client secret is " + str(bank_secret.value))
timeStamp = date.today()-timedelta(30)
###Get token for resource manager API###

mgmt_token_uri = "https://login.microsoftonline.com/e18a0c35-c3ed-46f4-8e69-018ca67f8288/oauth2/token"
mgmt_req_headers = {'content-type': 'application/x-www-form-urlencodeds'}
#mgmt_req_body = 'grant_type=client_credentials&client_secret=2fG8Q~LNHsgveTV1FGW8Dg9Esme84ALK9Cm2Pdw2&client_id=2b0ce5a8-0146-4b0c-a7ef-eccdb99b555b&resource=https%3A%2F%2Fmanagement.azure.com%2F'
mgmt_req_body = 'grant_type=client_credentials&client_secret='+str(bank_secret.value)+'&client_id=2b0ce5a8-0146-4b0c-a7ef-eccdb99b555b&resource=https%3A%2F%2Fmanagement.azure.com%2F'
mgmtresponse = requests.request(
    "POST", mgmt_token_uri, headers=mgmt_req_headers, data=mgmt_req_body)
print("mgmt token is \n" + str(mgmtresponse.text))


###Get token for Graph to get user name from principle ID###

graph_token_uri = "https://login.microsoftonline.com/e18a0c35-c3ed-46f4-8e69-018ca67f8288/oauth2/v2.0/token"
graph_req_headers = {'content-type': 'application/x-www-form-urlencodeds'}
graph_req_body = 'grant_type=client_credentials&client_secret='+str(bank_secret.value)+'&client_id=2b0ce5a8-0146-4b0c-a7ef-eccdb99b555b&scope=https%3A%2F%2Fgraph.microsoft.com%2F.default'
graphresponse = requests.request(
    "POST", graph_token_uri, headers=graph_req_headers, data=graph_req_body)
print("graph token is \n" + str(graphresponse.text))
print("Subscription ID is:\n" + str(os.environ['AZURE_SUBS_ID']))


@app.route('/')
def index():

    try:
        resource_by_type = []
        resource_by_location = []
        role_definition_name = []
        role_definition_name = []
        sub_policy = []
        data_by_type = {}
        data_by_location = {}
        data_sub_policy = {}

        data_rbac = {}

        resource_URI = 'https://management.azure.com/subscriptions/'+str(os.environ['AZURE_SUBS_ID'])+'/resources?api-version=2021-04-01'
        req_headers = {'Authorization': 'Bearer ' +
                       json.loads(mgmtresponse.text)['access_token'], 'Content-Type': 'Application/JSON'}
        res_response = requests.get(url=resource_URI, headers=req_headers)
        sub_resources = json.loads(res_response.text)
        for i in sub_resources['value']:
            resource_by_type.append(i['type'])
            resource_by_location.append(i['location'])

        for x in resource_by_type:
            data_by_type[x] = resource_by_type.count(x)

        for x in resource_by_location:
            data_by_location[x] = resource_by_location.count(x)

        

    except ClientAuthenticationError as ex:
        print(ex.message)
        return ex.message

    finally:
        print("Request succeeded")

    try:
        sub_role_assignment_Uri = "https://management.azure.com/subscriptions/"+str(os.environ['AZURE_SUBS_ID'])+"/providers/Microsoft.Authorization/roleAssignments?api-version=2015-07-01"
        req_headers = {'Authorization': 'Bearer ' +
                       json.loads(mgmtresponse.text)['access_token'], 'Content-Type': 'Application/JSON'}
        res_sub_role_assignments = requests.get(
            url=sub_role_assignment_Uri, headers=req_headers)
        sub_role_assignments = json.loads(res_sub_role_assignments.text)
        

        for items in sub_role_assignments['value']:
            role_definition_id = items['properties']['roleDefinitionId']
            role_definition_uri = "https://management.azure.com" + \
                str(role_definition_id) + "?api-version=2015-07-01"
            res_role_definition = json.loads(
                (requests.get(url=role_definition_uri, headers=req_headers)).text)
            role_definition_name.append(
                res_role_definition['properties']['roleName'])

        for x in role_definition_name:
            data_rbac[x] = role_definition_name.count(x)

        # print(data_rbac)

    except ClientAuthenticationError as ex:
        print(ex.message)

    try:
        sub_recommendation_uri = "https://management.azure.com/subscriptions/"+str(os.environ['AZURE_SUBS_ID'])+"/providers/Microsoft.Advisor/recommendations?api-version=2020-01-01"
        req_headers = {'Authorization': 'Bearer ' +
                       json.loads(mgmtresponse.text)['access_token'], 'Content-Type': 'Application/JSON'}
        res_sub_recommendations = json.loads(requests.get(
            url=sub_recommendation_uri, headers=req_headers).text)
        if(len(res_sub_recommendations['value']) == 0):
            recommendations = "Congrats !!! your subscription has no Advisor Recommendations"
            print(recommendations)

        else:
            recommendations = "Oops !!! There are some Advisor Recommendations"
            print(recommendations)

    except ClientAuthenticationError as ex:
        print(ex.message)

    try:
        sub_policy_state_uri = "https://management.azure.com/subscriptions/"+str(os.environ['AZURE_SUBS_ID'])+"/providers/Microsoft.PolicyInsights/policyStates/latest/queryResults?api-version=2019-10-01"
        req_headers = {'Authorization': 'Bearer ' +
                       json.loads(mgmtresponse.text)['access_token'], 'Content-Type': 'Application/JSON'}
        res_sub_policy = json.loads(requests.post(
            url=sub_policy_state_uri, headers=req_headers).text)
        # print(res_sub_policy)
        for items in res_sub_policy['value']:
            if items['complianceState'] == 'NonCompliant':
                data_sub_policy['policyAssignmentName'] = items['policyAssignmentName']
                data_sub_policy['policyDefinitionAction'] = items['policyDefinitionAction']
                data_sub_policy['Resource'] = (
                    items['resourceId']).split("/")[-1]
                data_sub_policy['policySetDefinitionCategory'] = items['policySetDefinitionCategory']
                sub_policy.append(data_sub_policy.copy())

    except ClientAuthenticationError as ex:
        print(ex.message)

    
    try:
        sub_activity_uri = "https://management.azure.com/subscriptions/"+str(os.environ['AZURE_SUBS_ID'])+"/providers/Microsoft.Insights/eventtypes/management/values?api-version=2015-04-01&$filter=eventTimestamp ge '" + str(timeStamp) +"'"
        req_headers = {'Authorization': 'Bearer ' +
                       json.loads(mgmtresponse.text)['access_token'], 'Content-Type': 'Application/JSON'}
        res_sub_activity = json.loads(requests.get(
            url=sub_activity_uri, headers=req_headers).text)
        if(len(res_sub_activity['value']) == 0):
            activity_logs = res_sub_activity['value']           

        else:
            activity_logs = "Oops !!! There are some Advisor Recommendations"
            print(activity_logs)

    except ClientAuthenticationError as ex:
        print(ex.message)
        
    finally:
        return render_template("index.html", res_type=json.loads(json.dumps(data_by_type)), res_location=json.loads(json.dumps(data_by_location)), res_rbac=json.loads(json.dumps(data_rbac)), recommendations=recommendations, policy=sub_policy,activity_logs = json.loads(json.dumps(activity_logs)))
    


@app.route('/resourcelocation', methods=['GET', 'POST'])
def resourcelocation():
    query_data = request.form['location']
    try:

        resource_URI = "https://management.azure.com/subscriptions/"+str(os.environ['AZURE_SUBS_ID'])+"/resources?$filter=location eq '" + \
            query_data+"'&api-version=2021-04-01"
        req_headers = {'Authorization': 'Bearer ' +
                       json.loads(mgmtresponse.text)['access_token'], 'Content-Type': 'Application/JSON'}
        res_response = requests.get(url=resource_URI, headers=req_headers)
        sub_resources = json.loads(res_response.text)
        

    except ClientAuthenticationError as ex:
        print(ex.message)

    return render_template("resourcelocation.html")

@app.route('/resourcetype', methods=['GET', 'POST'])
def resourcetype():
    query_data = request.form['resourcetype']
    try:
        res_type = []
        res_type_json = {}
        resource_URI = "https://management.azure.com/subscriptions/"+str(os.environ['AZURE_SUBS_ID'])+"/resources?$resourceType=location eq '" + \
            query_data+"'&api-version=2021-04-01"
        req_headers = {'Authorization': 'Bearer ' +
                       json.loads(mgmtresponse.text)['access_token'], 'Content-Type': 'Application/JSON'}
        res_response = requests.get(url=resource_URI, headers=req_headers)
        sub_resources = json.loads(res_response.text)
        for items in sub_resources['value']:
            res_type_json['name'] = items['name']  
            res_type_json['type'] = items['type']            
            res_type_json['kind'] = items['kind']
            res_type_json['location'] = items['location']
            res_type.append(res_type_json)
        
        return render_template("resourcetype.html", resource_type=res_type)      
                
                
        

    except ClientAuthenticationError as ex:
        print(ex.message)

    return render_template("resourcelocation.html")


@app.route('/rbac', methods=['GET', 'POST'])
def rbac():
    query_data = request.form['rbactype']
    try:
        g_res_list = []
        role_definition_uri = "https://management.azure.com/subscriptions/"+str(os.environ['AZURE_SUBS_ID'])+"/providers/Microsoft.Authorization/roleDefinitions?api-version=2015-07-01"
        req_headers = {'Authorization': 'Bearer ' + json.loads(mgmtresponse.text)['access_token'], 'Content-Type': 'Application/JSON'}
        res_role_definition = json.loads((requests.get(url=role_definition_uri, headers=req_headers)).text)
        for items in res_role_definition['value']:
            if items['properties']['roleName'] == query_data:
                role_def_id = items['id']

        r_assignment_uri = "https://management.azure.com/subscriptions/"+str(os.environ['AZURE_SUBS_ID'])+"/providers/Microsoft.Authorization/roleAssignments?api-version=2015-07-01"
        req_headers = {'Authorization': 'Bearer ' + json.loads(mgmtresponse.text)['access_token'], 'Content-Type': 'Application/JSON'}
        r_assignment_res = json.loads((requests.get(url=r_assignment_uri, headers=req_headers)).text)
        for items in r_assignment_res['value']:
            if items['properties']['roleDefinitionId'] == role_def_id:
                g_uri = "https://graph.microsoft.com/v1.0/directoryObjects/" + items['properties']['principalId']
                g_headers = {'Authorization': 'Bearer ' + json.loads(graphresponse.text)['access_token'], 'Content-Type': 'Application/JSON'}
                #g_res = requests.request("GET", g_uri, headers=g_headers)
                g_res = json.loads((requests.get(url=g_uri,headers=g_headers)).text)
                g_res['scope'] = items['properties']['scope']
                g_res_list.append(g_res)
        
        return render_template("rbac.html", rbac_details=g_res_list)

    except ClientAuthenticationError as ex:
        print(ex.message)



if __name__ == '__main__':
    app.run()
