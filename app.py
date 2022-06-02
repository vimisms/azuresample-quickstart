from datetime import datetime, timedelta
from urllib import response
import requests
import json
import jinja2
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential, AzureCliCredential
from azure.core.exceptions import ClientAuthenticationError
import adal
import random

app = Flask(__name__)

resource_by_type = []
resource_by_location = []
data_by_type = {}
data_by_location = {}
vault_uri = "https://neo-rbac-webapp-kv.vault.azure.net/"
credential = DefaultAzureCredential()
client = SecretClient(vault_url=vault_uri, credential=credential)
secret_name = '2b0ce5a8-0146-4b0c-a7ef-eccdb99b555b'
bank_secret = client.get_secret(secret_name)

###Get token for resource manager API###
authority = (
    'https://login.microsoftonline.com/e18a0c35-c3ed-46f4-8e69-018ca67f8288')
context = adal.AuthenticationContext(authority)
token = context.acquire_token_with_client_credentials(
    "https://management.azure.com", bank_secret.name, bank_secret.value)
print(token)

###Get token for Graph to get user name from principle ID###

graph_token_uri = "https://login.microsoftonline.com/e18a0c35-c3ed-46f4-8e69-018ca67f8288/oauth2/v2.0/token"
graph_req_headers = {'Content-Type': 'x-www-forum-urlencoded'}
graph_req_body = {'grant_type':'client_credentials','client_id':'2b0ce5a8-0146-4b0c-a7ef-eccdb99b555b','scope': 'https://graph.microsoft.com/.default','client_secret':str(bank_secret) }

graph_token_res = requests.post(url=graph_token_uri,headers=graph_req_headers,json=graph_req_body)

print("graph token is \n" +  str(graph_token_res.text))




@app.route('/')
def index():

    try:
        resource_by_type = []
        resource_by_location = []
        data_by_type = {}
        data_by_location = {}

        response = str("Secret name is:" + secret_name + " and secret value is " + str(bank_secret.value) + "and token is " + str(token['accessToken']))
        resource_URI = 'https://management.azure.com/subscriptions/6e268af1-b2a7-44a7-9a1a-9025889dbe5d/resources?api-version=2021-04-01'
        req_headers = {'Authorization': 'Bearer ' +
                       token['accessToken'], 'Content-Type': 'Application/JSON'}
        res_response = requests.get(url=resource_URI, headers=req_headers)
        sub_resources = json.loads(res_response.text)
        print(sub_resources)
        #res_five = random.sample(sub_resources['value'],5)
        # return render_template("index.html",res_five=res_five)
        for i in sub_resources['value']:
            resource_by_type.append(i['type'])
            resource_by_location.append(i['location'])

        print(resource_by_type)
        for x in resource_by_type:
            data_by_type[x] = resource_by_type.count(x)

        for x in resource_by_location:
            data_by_location[x] = resource_by_location.count(x)

        print(data_by_type)
        print(data_by_location)
        return render_template("index.html", res_type=json.loads(json.dumps(data_by_type)), res_location=json.loads(json.dumps(data_by_location)))

    except ClientAuthenticationError as ex:
        print(ex.message)
        return ex.message
    
    finally:
        print("Request succeeded")
    
    try:
        sub_role_assignment_Uri = "https://management.azure.com/subscriptions/6e268af1-b2a7-44a7-9a1a-9025889dbe5d/providers/Microsoft.Authorization/roleAssignments?api-version=2015-07-01"
        req_headers = {'Authorization': 'Bearer ' +
                       token['accessToken'], 'Content-Type': 'Application/JSON'}
        res_sub_role_assignments = requests.get(url=sub_role_assignment_Uri, headers=req_headers)
        sub_role_assignments = json.loads(res_sub_role_assignments.text)
        print(sub_role_assignments)
        
    except:
        print(ex.message)
        


if __name__ == '__main__':
    app.run()
