from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError



app = Flask(__name__)


@app.route('/')
def index():
    vault_uri = "https://neo-rbac-webapp-kv.vault.azure.net/"
    credential = DefaultAzureCredential()
    client = SecretClient(vault_uri=vault_uri,
                  credential=credential)
    existing_secret = client.get_secret('2b0ce5a8-0146-4b0c-a7ef-eccdb99b555b')
    print('Request for index page received')
    print(existing_secret)
    return render_template('index.html')


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/hello', methods=['POST'])
def hello():
    name = request.form.get('name')

    if name:
        print('Request for hello page received with name=%s' % name)
        return render_template('hello.html', name=name)
    else:
        print('Request for hello page received with no name or blank name -- redirecting')
        return redirect(url_for('index'))

    

if __name__ == '__main__':

    app.run()

