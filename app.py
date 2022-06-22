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
###Get token for resource manager API###

mgmt_token_uri = "https://login.microsoftonline.com/e18a0c35-c3ed-46f4-8e69-018ca67f8288/oauth2/token"
mgmt_req_headers = {'content-type': 'application/x-www-form-urlencodeds'}
mgmt_req_body = 'grant_type=client_credentials&client_secret='+str(bank_secret.value)+'&client_id=2b0ce5a8-0146-4b0c-a7ef-eccdb99b555b&resource=https%3A%2F%2Fmanagement.azure.com%2F'
mgmtresponse = requests.request(
    "POST", mgmt_token_uri, headers=mgmt_req_headers, data=mgmt_req_body)
#print("mgmt token is \n" + str(mgmtresponse.text))


###Get token for Graph to get user name from principle ID###

graph_token_uri = "https://login.microsoftonline.com/e18a0c35-c3ed-46f4-8e69-018ca67f8288/oauth2/v2.0/token"
graph_req_headers = {'content-type': 'application/x-www-form-urlencodeds'}
graph_req_body = 'grant_type=client_credentials&client_secret='+str(bank_secret.value)+'&client_id=2b0ce5a8-0146-4b0c-a7ef-eccdb99b555b&scope=https%3A%2F%2Fgraph.microsoft.com%2F.default'
graphresponse = requests.request(
    "POST", graph_token_uri, headers=graph_req_headers, data=graph_req_body)
print("Subscription ID is:\n" + str(os.environ['AZURE_SUBS_ID']))


@app.route('/')
def index():
    try:
        management_groups_json = {}
        management_groups_list = []
        
        management_group_uri = "https://management.azure.com/providers/Microsoft.Management/managementGroups?api-version=2020-05-01"
        req_headers = {'Authorization': 'Bearer ' +
                       json.loads(mgmtresponse.text)['access_token'], 'Content-Type': 'Application/JSON'}
        res_response = json.loads(requests.get(url=management_group_uri, headers=req_headers).text)
        for items in res_response['value']:
            management_groups_json['name'] = items['properties']['displayName']
            management_groups_json['id'] = items['name']
            management_groups_list.append(management_groups_json.copy())

        return render_template("index.html", management_groups =management_groups_list)
    
    except ClientAuthenticationError as ex:
        print(ex.message)
        
@app.route('/subscription', methods=['GET', 'POST'])
def subscription():
    try:
        query_data = request.form['managementgroup']
        subscriptions_json = {}
        subscriptions_list = []
        
        subscriptions_uri = "https://management.azure.com/providers/Microsoft.Management/managementGroups/" +query_data+ "/subscriptions?api-version=2020-05-01"
        req_headers = {'Authorization': 'Bearer ' +
                       json.loads(mgmtresponse.text)['access_token'], 'Content-Type': 'Application/JSON'}
        res_response = json.loads(requests.get(url=subscriptions_uri, headers=req_headers).text)
        for items in res_response['value']:
            subscriptions_json['name'] = items['properties']['displayName']
            subscriptions_json['id'] = items['name']
            subscriptions_list.append(subscriptions_json.copy())

        return render_template("subscription.html", subscriptions =subscriptions_list)
    
    except ClientAuthenticationError as ex:
        print(ex.message)
            
        