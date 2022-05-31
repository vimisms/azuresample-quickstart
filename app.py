from datetime import datetime
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
    try:
        secret = client.get_secret("2b0ce5a8-0146-4b0c-a7ef-eccdb99b555b")
        print(secret.Value)
        response = f'secret{str(secret.value)}'
        return response
        
    except ClientAuthenticationError as ex:
        print(ex.message)
        return ex.message
        

if __name__ == '__main__':
    app.run()