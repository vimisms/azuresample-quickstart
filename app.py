from datetime import date, timedelta
from operator import concat
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
        
        
@app.route('/compliancecheck', methods=['GET', 'POST'])
def compliancecheck():
    try:
        global query_data_subscription 
        query_data_subscription = request.form['subscription']
        
        storage_account_checks_json = {}
        storage_account_checks_list = []
        storage_account_names = []
        stg_acct_uri = "https://management.azure.com/subscriptions/"+query_data_subscription+"/providers/Microsoft.Storage/storageAccounts?api-version=2021-09-01"
        req_headers = {'Authorization': 'Bearer ' +
                       json.loads(mgmtresponse.text)['access_token'], 'Content-Type': 'Application/JSON'}
        res_response = json.loads(requests.get(url=stg_acct_uri, headers=req_headers).text)
        for items in res_response['value']:
            if len(items['properties']['privateEndpointConnections']) == 0:
                storage_account_checks_json['ComplianceName'] = "All Storage accounts must have private end point connections"
                storage_account_checks_json['Status'] = "Failed"
                storage_account_checks_json['Resource'] = items['name']                             
                storage_account_checks_list.append(storage_account_checks_json.copy())                
            else:
                storage_account_checks_json['ComplianceName'] = "All Storage accounts must have private end point connections"
                storage_account_checks_json['Status'] = "Passed"
                storage_account_checks_list.append(storage_account_checks_json.copy())   
                
        for items in res_response['value']:
            if items['properties']['publicNetworkAccess'] == "Enabled":
                storage_account_checks_json['ComplianceName'] = "All Storage accounts must have publich access disabled"
                storage_account_checks_json['Status'] = "Failed"
                storage_account_checks_json['Resource'] = items['name']                             
                storage_account_checks_list.append(storage_account_checks_json.copy())                
            else:
                storage_account_checks_json['ComplianceName'] = "All Storage accounts must have publich access disabled"
                storage_account_checks_json['Status'] = "Passed"
                storage_account_checks_list.append(storage_account_checks_json.copy())
                
        for items in res_response['value']:
            if items['properties']['minimumTlsVersion'] == "TLS1_2":
                storage_account_checks_json['ComplianceName'] = "All Storage accounts must have TLS 1.2"
                storage_account_checks_json['Status'] = "Failed"
                storage_account_checks_json['Resource'] = items['name']                             
                storage_account_checks_list.append(storage_account_checks_json.copy())                
            else:
                storage_account_checks_json['ComplianceName'] = "All Storage accounts must have TLS 1.2"
                storage_account_checks_json['Status'] = "Passed"
                storage_account_checks_list.append(storage_account_checks_json.copy())
        
        for items in res_response['value']:            
            if items['properties']['encryption']['requireInfrastructureEncryption'] == "false":
                storage_account_checks_json['ComplianceName'] = "All Storage accounts must have encryption"
                storage_account_checks_json['Status'] = "Failed"
                storage_account_checks_json['Resource'] = items['name']                             
                storage_account_checks_list.append(storage_account_checks_json.copy())                
            else:
                storage_account_checks_json['ComplianceName'] = "All Storage accounts must have encryption"
                storage_account_checks_json['Status'] = "Passed"
                storage_account_checks_list.append(storage_account_checks_json.copy())
            
    
    except ClientAuthenticationError as ex:
        print(ex.message)
        return ex.message

    finally:
        print(storage_account_checks_list)
        return render_template("compliancecheck.html", compliancecheck_details = storage_account_checks_list)
    
                                                         

@app.route('/home', methods=['GET', 'POST'])
def home():

    try:

        subscription_details={}
        resource_by_type = []
        resource_by_location = []
        role_definition_name = []
        role_definition_name = []
        sub_policy = []
        activity_Logs = []
        data_by_type = {}
        data_by_location = {}
        data_sub_policy = {}
        data_sub_activity = {}

        data_rbac = {}
        
        subscription_detail_uri = "https://management.azure.com/subscriptions/"+query_data_subscription+"?api-version=2020-01-01"
        req_headers = {'Authorization': 'Bearer ' +
                       json.loads(mgmtresponse.text)['access_token'], 'Content-Type': 'Application/JSON'}
        res_response = json.loads(requests.get(url=subscription_detail_uri, headers=req_headers).text)
        subscription_details['SubscriptionID']=res_response['subscriptionId']
        subscription_details['SubscriptionName']=res_response['displayName']
             
        

        resource_URI = 'https://management.azure.com/subscriptions/'+query_data_subscription+'/resources?api-version=2021-04-01'
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
        sub_role_assignment_Uri = "https://management.azure.com/subscriptions/"+query_data_subscription+"/providers/Microsoft.Authorization/roleAssignments?api-version=2015-07-01"
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
        sub_recom_json = {}
        sub_recom= []
        
        sub_recommendation_uri = "https://management.azure.com/subscriptions/"+query_data_subscription+"/providers/Microsoft.Advisor/recommendations?api-version=2020-01-01"
        req_headers = {'Authorization': 'Bearer ' +
                       json.loads(mgmtresponse.text)['access_token'], 'Content-Type': 'Application/JSON'}
        res_sub_recommendations = json.loads(requests.get(
            url=sub_recommendation_uri, headers=req_headers).text)
        if(len(res_sub_recommendations['value']) == 0):
            recommendations = "Congrats !!! your subscription has no Advisor Recommendations"
            #print(recommendations)

        else:
            for items in res_sub_recommendations['value']:
                sub_recom_json['category'] = items['properties']['category']
                sub_recom_json['impact'] = items['properties']['impact']
                sub_recom_json['impactedField'] = items['properties']['impactedField']
                sub_recom_json['impactedValue'] = items['properties']['impactedValue']
                sub_recom_json['problem'] = items['properties']['shortDescription']['problem']
                sub_recom_json['solution'] = items['properties']['shortDescription']['solution']
                sub_recom.append(sub_recom_json.copy())

    except ClientAuthenticationError as ex:
        print(ex.message)

    try:
        sub_policy_state_uri = "https://management.azure.com/subscriptions/"+query_data_subscription+"/providers/Microsoft.PolicyInsights/policyStates/latest/queryResults?api-version=2019-10-01"
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
        sub_activity_uri = "https://management.azure.com/subscriptions/"+query_data_subscription+"/providers/Microsoft.Insights/eventtypes/management/values?api-version=2015-04-01&$filter=eventTimestamp ge '" + str(timeStamp) +"'"
        req_headers = {'Authorization': 'Bearer ' +
                       json.loads(mgmtresponse.text)['access_token'], 'Content-Type': 'Application/JSON'}
        res_sub_activity = json.loads(requests.get(
            url=sub_activity_uri, headers=req_headers).text)
        if(len(res_sub_activity['value']) != 0):
            for items in res_sub_activity['value']:
                data_sub_activity['Action']=items['authorization']['action']
                data_sub_activity['Caller']=items['caller']
                data_sub_activity['Category']=items['category']['localizedValue']
                data_sub_activity['ResourceId']=items['resourceId']
                data_sub_activity['ResourceType']=items['resourceType']['localizedValue']
                data_sub_activity['OperationName']=items['operationName']['localizedValue']
                data_sub_activity['Status']=items['status']['localizedValue']
                data_sub_activity['EventTime']=items['eventTimestamp'] 
                activity_Logs.append(data_sub_activity)             
    
        #print(activity_Logs)    

    except ClientAuthenticationError as ex:
        print(ex.message)
        
    finally:
        return render_template("home.html", sub_details = json.loads(json.dumps(subscription_details)),res_type=json.loads(json.dumps(data_by_type)), res_location=json.loads(json.dumps(data_by_location)), res_rbac=json.loads(json.dumps(data_rbac)), recommendations=sub_recom, policy=sub_policy,activity_logs = json.loads(json.dumps(activity_Logs)))
    


@app.route('/resourcelocation', methods=['GET', 'POST'])
def resourcelocation():
    query_data = request.form['location']
    try:
        res_loc = []
        res_loc_json = {}
        resource_URI = "https://management.azure.com/subscriptions/"+query_data_subscription+"/resources?$filter=location eq '" + \
            query_data+"'&api-version=2021-04-01"
        req_headers = {'Authorization': 'Bearer ' +
                       json.loads(mgmtresponse.text)['access_token'], 'Content-Type': 'Application/JSON'}
        loc_response = requests.get(url=resource_URI, headers=req_headers)
        loc_resources = json.loads(loc_response.text)
        print(loc_resources)
        for items in loc_resources['value']:
            res_loc_json['name'] = items['name']
            res_loc_json['location'] = items['location']
            res_loc_json['type'] = items['type']
            if 'tags' in items:
                res_loc_json['tags'] = str(items['tags'])
            else:
                res_loc_json['tags'] = 'NULL'
                
            res_loc.append(res_loc_json.copy())
            #print(res_loc)
        
        

    except ClientAuthenticationError as ex:
        print(ex.message)

    return render_template("resourcelocation.html",resourcebylocation=res_loc)

@app.route('/resourcetype', methods=['GET', 'POST'])
def resourcetype():
    query_data = request.form['resourcetype']
    if query_data == 'Microsoft.Compute/virtualMachines':
        try:
            res_type = []
            res_type_json = {}
        
            resource_URI = "https://management.azure.com/subscriptions/"+query_data_subscription+"/providers/Microsoft.Compute/virtualMachines?api-version=2022-03-01"
            req_headers = {'Authorization': 'Bearer ' +
                       json.loads(mgmtresponse.text)['access_token'], 'Content-Type': 'Application/JSON'}
            res_response = requests.get(url=resource_URI, headers=req_headers)
            sub_resources = json.loads(res_response.text)
            for items in sub_resources['value']:
                res_type_json['name'] = items['name']  
                res_type_json['location'] = items['location']            
                res_type_json['hardwareProfile'] = items['properties']['hardwareProfile']['vmSize']
                res_type_json['OS'] = items['properties']['storageProfile']['osDisk']['osType']
                res_type_json['OSDiskType'] = items['properties']['storageProfile']['osDisk']['managedDisk']['storageAccountType']  
                res_type_json['Imagereference'] = str(items['properties']['storageProfile']['imageReference']['publisher']) +' '+ str(items['properties']['storageProfile']['imageReference']['exactVersion'])
                res_type.append(res_type_json.copy())
                
        except ClientAuthenticationError as ex:
            print(ex.message)
        finally:
            return render_template("virtualmachines.html",virtualmachines=res_type)
        
    elif query_data == 'Microsoft.Web/serverFarms':
        try:
            res_type = []
            res_type_json = {}
        
            resource_URI = "https://management.azure.com/subscriptions/"+query_data_subscription+"/providers/Microsoft.Web/serverfarms?api-version=2021-02-01"
            req_headers = {'Authorization': 'Bearer ' +
                       json.loads(mgmtresponse.text)['access_token'], 'Content-Type': 'Application/JSON'}
            res_response = requests.get(url=resource_URI, headers=req_headers)
            sub_resources = json.loads(res_response.text)
            for items in sub_resources['value']:
                res_type_json['name'] = items['name']  
                res_type_json['location'] = items['location']            
                res_type_json['Kind'] = items['kind']
                res_type_json['SKUName'] = items['sku']['name']
                res_type_json['SKUTier'] = items['sku']['tier']
                res_type_json['SKUSize'] = items['sku']['size']
                res_type_json['family'] = items['sku']['family']
                res_type_json['capacity'] = items['sku']['capacity']
                
                res_type.append(res_type_json.copy())
            
            print(res_type)
                
        except ClientAuthenticationError as ex:
            print(ex.message)           
            
        finally:
            return render_template("appserviceplans.html",appserviceplans=res_type)
            
    elif query_data == 'Microsoft.Storage/storageAccounts':
        try:
            res_type = []
            res_type_json = {}
        
            resource_URI = "https://management.azure.com/subscriptions/"+query_data_subscription+"/providers/Microsoft.Storage/storageAccounts?api-version=2021-09-01"
            req_headers = {'Authorization': 'Bearer ' +
                       json.loads(mgmtresponse.text)['access_token'], 'Content-Type': 'Application/JSON'}
            res_response = requests.get(url=resource_URI, headers=req_headers)
            sub_resources = json.loads(res_response.text)
            for items in sub_resources['value']:
                res_type_json['name'] = items['name']  
                res_type_json['location'] = items['location']            
                res_type_json['Kind'] = items['kind']
                res_type_json['SKUName'] = items['sku']['name']
                res_type_json['SKUTier'] = items['sku']['tier']                
                res_type.append(res_type_json.copy())
                
        except ClientAuthenticationError as ex:
            print(ex.message)
            
        finally:
            return render_template("storageaccount.html",storageaccounts=res_type)
            
    elif query_data == 'Microsoft.Network/virtualNetworks':
        try:
            res_type = []
            res_type_json = {}
        
            resource_URI = "https://management.azure.com/subscriptions/"+query_data_subscription+"/providers/Microsoft.Network/virtualNetworks?api-version=2021-08-01"
            req_headers = {'Authorization': 'Bearer ' +
                       json.loads(mgmtresponse.text)['access_token'], 'Content-Type': 'Application/JSON'}
            res_response = requests.get(url=resource_URI, headers=req_headers)
            sub_resources = json.loads(res_response.text)
            for items in sub_resources['value']:
                res_type_json['name'] = items['name']  
                res_type_json['location'] = items['location']            
                res_type_json['addressSpace'] = items['properties']['addressSpace']['addressPrefixes'][0]
                res_type_json['subnets'] = len(items['properties']['subnets'])              
                res_type_json['virtualNetworkPeerings'] = len(items['properties']['virtualNetworkPeerings'])
                res_type_json['enableDdosProtection'] = items['properties']['enableDdosProtection']
                res_type.append(res_type_json.copy())
            print(res_type)
                
        except ClientAuthenticationError as ex:
            print(ex.message)   
            
            
        finally:
            return render_template("virtualnetworks.html",virtualnetworks=res_type)

    else:
        try:
            res_type = []
            res_type_json = {}
            resource_URI = "https://management.azure.com/subscriptions/"+query_data_subscription+"/resources?$filter=resourceType eq '" + \
            query_data+"'&api-version=2021-04-01"
            req_headers = {'Authorization': 'Bearer ' +
                       json.loads(mgmtresponse.text)['access_token'], 'Content-Type': 'Application/JSON'}
            res_response = requests.get(url=resource_URI, headers=req_headers)
            sub_resources = json.loads(res_response.text)
            for items in sub_resources['value']:
                res_type_json['id'] = items['id']  
                res_type_json['location'] = items['location']            
                res_type_json['name'] = items['name']
                res_type_json['type'] = items['type']
                res_type.append(res_type_json.copy())
        except ClientAuthenticationError as ex:
            print(ex.message) 
        
        finally:
            return render_template("resourcetype.html", resourcetype=res_type)
            


@app.route('/rbac', methods=['GET', 'POST'])
def rbac():
    query_data = request.form['rbactype']
    try:
        g_res_list = []
        role_definition_uri = "https://management.azure.com/subscriptions/"+query_data_subscription+"/providers/Microsoft.Authorization/roleDefinitions?api-version=2015-07-01"
        req_headers = {'Authorization': 'Bearer ' + json.loads(mgmtresponse.text)['access_token'], 'Content-Type': 'Application/JSON'}
        res_role_definition = json.loads((requests.get(url=role_definition_uri, headers=req_headers)).text)
        for items in res_role_definition['value']:
            if items['properties']['roleName'] == query_data:
                role_def_id = items['id']

        r_assignment_uri = "https://management.azure.com/subscriptions/"+query_data_subscription+"/providers/Microsoft.Authorization/roleAssignments?api-version=2015-07-01"
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

        