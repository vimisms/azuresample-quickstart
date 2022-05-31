from datetime import datetime,timedelta
from urllib import response
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential,AzureCliCredential
from azure.core.exceptions import ClientAuthenticationError

app = Flask(__name__)	

@app.route('/')
def index():
    vault_uri = "https://neo-rbac-webapp-kv.vault.azure.net/"
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=vault_uri, credential=credential)
    secret_name = '2b0ce5a8-0146-4b0c-a7ef-eccdb99b555b'
    #print("\n.. Create Secret")
    #expires = datetime.now() + timedelta(days=365)
    #secret = client.set_secret("helloWorldSecretName", "helloWorldSecretValue", expires_on=expires)
    #print("Secret with name '{0}' created with value '{1}'".format(secret.name, secret.value))
    #print("Secret with name '{0}' expires on '{1}'".format(secret.name, secret.properties.expires_on))
    try:
        bank_secret = client.get_secret(secret_name)
        print(bank_secret.value)
        response = str("Secret name is:" + secret_name + " and secret value is " + str(bank_secret.value))
        
        return response
        
    except ClientAuthenticationError as ex:
        print(ex.message)
        return ex.message
        

if __name__ == '__main__':
    app.run()