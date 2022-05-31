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
    print("\n.. Create Secret")
    expires = datetime.utcnow() + datetime.timedelta(days=365)
    secret = client.set_secret("helloWorldSecretName", "helloWorldSecretValue", expires_on=expires)
    print("Secret with name '{0}' created with value '{1}'".format(secret.name, secret.value))
    print("Secret with name '{0}' expires on '{1}'".format(secret.name, secret.properties.expires_on))
    try:
        bank_secret = client.get_secret(secret.name)
        print(secret)
        response = f'secret{str(secret)}'
        return response
        
    except ClientAuthenticationError as ex:
        print(ex.message)
        return ex.message
        

if __name__ == '__main__':
    app.run()