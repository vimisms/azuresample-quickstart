from datetime import datetime,timedelta
from urllib import response
import requests, json
import jinja2
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential,AzureCliCredential
from azure.core.exceptions import ClientAuthenticationError
import adal
import random

app = Flask(__name__)	

@app.route('/')
def index():
    resource_by_type = []
    vault_uri = "https://neo-rbac-webapp-kv.vault.azure.net/"
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=vault_uri, credential=credential)
    secret_name = '2b0ce5a8-0146-4b0c-a7ef-eccdb99b555b'

    try:
        bank_secret = client.get_secret(secret_name)
        authority = ('https://login.microsoftonline.com/e18a0c35-c3ed-46f4-8e69-018ca67f8288')
        context = adal.AuthenticationContext(authority)
        token = context.acquire_token_with_client_credentials("https://management.azure.com",bank_secret.name , bank_secret.value)
        print(token)
        response = str("Secret name is:" + secret_name + " and secret value is " + str(bank_secret.value) + "and token is " + str(token['accessToken']))
        resource_URI = 'https://management.azure.com/subscriptions/6e268af1-b2a7-44a7-9a1a-9025889dbe5d/resources?api-version=2021-04-01'
        req_headers = {'Authorization':'Bearer ' + token['accessToken'], 'Content-Type': 'Application/JSON'}
        res_response = requests.get(url=resource_URI,headers=req_headers)
        sub_resources = json.loads(res_response.text)
        print(sub_resources)
        #res_five = random.sample(sub_resources['value'],5)
        #return render_template("index.html",res_five=res_five)
        for i in sub_resources['value']:
            resource_by_type.append(i['type'])
            
        res = {}
        for i in resource_by_type:
            res[i] = resource_by_type.count[i]
            
        print(res)
        return render_template("index.html",res=json.loads(json.dumps(res)))
            
        
    except ClientAuthenticationError as ex:
        print(ex.message)
        return ex.message
        

if __name__ == '__main__':
    app.run()