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
timeStamp = date.today()-timedelta(30)
fulltimeStamp = date.today()-timedelta(88)
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
        
        
@app.route('/defenderassesment', methods=['GET', 'POST'])
def defenderassesment():
        
    try:
        assesment_healthy_json = {}
        assesment_unhealthy_json = {}
        assesment_healthy = []
        assesment_unhealthy = []
        global query_data_subscription 
        query_data_subscription = request.form['subscription']
        assesment_URI = "https://management.azure.com/subscriptions/"+query_data_subscription+"/providers/Microsoft.Security/assessments?api-version=2020-01-01"
        req_headers = {'Authorization': 'Bearer ' +
                       json.loads(mgmtresponse.text)['access_token'], 'Content-Type': 'Application/JSON'}
        res_response = json.loads(requests.get(url=assesment_URI, headers=req_headers).text)    
        for items in res_response['value']:
            if items['properties']['status']['code'] == "Healthy":
                assesment_healthy_json['Resource'] = (items['properties']['resourceDetails']['Id']).split('/')[-1]
                assesment_healthy_json['Rule'] = items['properties']['displayName']
                assesment_healthy_json['Status'] = items['properties']['status']['code']
                assesment_healthy.append(assesment_healthy_json.copy())
                
            elif items['properties']['status']['code'] == "Unhealthy":
                assesment_unhealthy_json['Resource'] = (items['properties']['resourceDetails']['Id']).split('/')[-1]
                assesment_unhealthy_json['Rule'] = items['properties']['displayName']
                assesment_unhealthy_json['Status'] = items['properties']['status']['code']
                assesment_unhealthy.append(assesment_unhealthy_json.copy())    
    
    except ClientAuthenticationError as ex:
        print(ex.message)
        return ex.message

    finally:
        return render_template("defenderassesment.html", assesment_healthy = assesment_healthy, assesment_unhealthy=assesment_unhealthy )
    
                                                         

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
                if 'impactedField' in (items['properties']).keys():
                    sub_recom_json['impactedField'] = items['properties']['impactedField']
                else:
                    sub_recom_json['impactedField'] = ""
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
                data_sub_policy['policyDefinitionReferenceId'] = items['policyDefinitionReferenceId']
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
                data_sub_activity['Resource']=(items['resourceId']).split("/")[-1]
                data_sub_activity['ResourceType']=items['resourceType']['localizedValue']
                data_sub_activity['Status']=items['status']['localizedValue']
                data_sub_activity['EventTime']=items['eventTimestamp'] 
                activity_Logs.append(data_sub_activity)             
    
        #print(activity_Logs)    

    except ClientAuthenticationError as ex:
        print(ex.message)
        
    finally:
        
        return render_template("home.html", sub_details = json.loads(json.dumps(subscription_details)),res_type=data_by_type, res_location=json.loads(json.dumps(data_by_location)), res_rbac=json.loads(json.dumps(data_rbac)), recommendations=sub_recom, policy=sub_policy,activity_logs = json.loads(json.dumps(activity_Logs)))
    


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
        

@app.route('/policynoncompliance', methods=['GET', 'POST'])
def policynoncompliance():
    data_sub_policy = {}
    sub_policy = []
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
                data_sub_policy['policyDefinitionReferenceId'] = items['policyDefinitionReferenceId']
                data_sub_policy['policyDefinitionAction'] = items['policyDefinitionAction']
                data_sub_policy['Resource'] = (
                    items['resourceId']).split("/")[-1]
                data_sub_policy['policySetDefinitionCategory'] = items['policySetDefinitionCategory']
                sub_policy.append(data_sub_policy.copy())

    except ClientAuthenticationError as ex:
        print(ex.message)
    
    finally:
        return render_template("policynoncompliance.html", policy_details=sub_policy)
    
@app.route('/activitylogs', methods=['GET', 'POST'])
def activitylogs():
    data_sub_activity = {}
    activity_Logs = []
    try:
        sub_activity_uri = "https://management.azure.com/providers/Microsoft.Management/managementGroups/SHELLCORP-AZMG-TENANT-TC-DEV/providers/microsoft.insights/eventtypes/management/values"
        req_headers = {'Authorization': 'Bearer ' +
                       json.loads(mgmtresponse.text)['access_token'], 'Content-Type': 'Application/JSON'}
        res_sub_activity = json.loads(requests.get(
            url=sub_activity_uri, headers=req_headers).text)
        if(len(res_sub_activity['value']) != 0):
            for items in res_sub_activity['value']:
                if items['caller'] == '13f6808c-5df7-4fe7-bd9b-11445e0e6797':
                    data_sub_activity['Action']=items['authorization']['action']
                    data_sub_activity['Category']=items['category']['localizedValue']
                    data_sub_activity['Resource']=(items['resourceId']).split("/")[4]
                    data_sub_activity['ResourceType']=items['resourceType']['localizedValue']
                    data_sub_activity['Status']=items['status']['localizedValue']
                    data_sub_activity['EventTime']=items['eventTimestamp']
                    activity_Logs.append(data_sub_activity.copy())             
    
        #print(activity_Logs)    

    except ClientAuthenticationError as ex:
        print(ex.message)
        
    finally:
        return render_template("activitylogs.html", activity_logs = activity_Logs)
    
@app.route('/criticalorerrorlogs', methods=['GET', 'POST'])
def criticalorerrorlogs():
    data_cri_activity = {}
    critical_Logs = []
    try:
        sub_activity_uri = "https://management.azure.com/subscriptions/"+query_data_subscription+"/providers/Microsoft.Insights/eventtypes/management/values?api-version=2015-04-01&$filter=eventTimestamp ge '" + str(fulltimeStamp) +"'"
        req_headers = {'Authorization': 'Bearer ' +
                       json.loads(mgmtresponse.text)['access_token'], 'Content-Type': 'Application/JSON'}
        res_sub_activity = json.loads(requests.get(
            url=sub_activity_uri, headers=req_headers).text)
        if(len(res_sub_activity['value']) != 0):
            for items in res_sub_activity['value']:
                if items['level'] == 'Error'or items['level'] == 'Critical':
                    data_cri_activity['Action']=items['authorization']['action']
                    data_cri_activity['Category']=items['category']['localizedValue']
                    data_cri_activity['Resource']=(items['resourceId']).split("/")[4]
                    data_cri_activity['ResourceType']=items['resourceType']['localizedValue']
                    data_cri_activity['Status']=items['status']['localizedValue']
                    data_cri_activity['EventTime']=items['eventTimestamp']
                    critical_Logs.append(data_cri_activity.copy())             
    
        #print(activity_Logs)    

    except ClientAuthenticationError as ex:
        print(ex.message)
        
    finally:
        return render_template("criticalLogs.html", activity_logs = critical_Logs)
    
@app.route('/recommendations', methods=['GET', 'POST'])
def recommendations():
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
                if items['properties']['impactedField'] != "":
                    sub_recom_json['impactedField'] = items['properties']['impactedField']
                else:
                    sub_recom_json['impactedField'] = ""
                sub_recom_json['impactedValue'] = items['properties']['impactedValue']
                sub_recom_json['problem'] = items['properties']['shortDescription']['problem']
                sub_recom_json['solution'] = items['properties']['shortDescription']['solution']
                sub_recom.append(sub_recom_json.copy())

    except ClientAuthenticationError as ex:
        print(ex.message)
        
    finally:
        return render_template("recommendations.html", recommendations = sub_recom)
    
@app.route('/policyexemptions', methods=['GET', 'POST'])
def policyexemptions():
    try:
        sub_exempt_json = {}
        sub_exempt= []
        
        sub_exempt_uri = "https://management.azure.com/subscriptions/"+query_data_subscription+"/providers/Microsoft.Authorization/policyExemptions?api-version=2020-07-01-preview"
        req_headers = {'Authorization': 'Bearer ' +
                       json.loads(mgmtresponse.text)['access_token'], 'Content-Type': 'Application/JSON'}
        res_sub_exempt = json.loads(requests.get(
            url=sub_exempt_uri, headers=req_headers).text)
        if(len(res_sub_exempt['value']) == 0):
            sub_exempt = "Congrats !!! your subscription has no exemptions"
            #print(recommendations)

        else:
            for items in res_sub_exempt['value']:
                sub_exempt_json['Policy'] = (items['properties']['policyAssignmentId']).split('/')[-1]
                sub_exempt_json['exemptionCategory'] = items['properties']['exemptionCategory']
                sub_exempt_json['displayName'] = items['properties']['displayName']
                sub_exempt_json['createdBy'] = items['systemData']['createdBy']
                sub_exempt_json['createdAt'] = items['systemData']['createdAt']
            
                sub_exempt.append(sub_exempt_json.copy())

    except ClientAuthenticationError as ex:
        print(ex.message)
        
    finally:
        return render_template("policyexemptions.html", exemptions = sub_exempt)
    
@app.route('/stgcompliance', methods=['GET', 'POST'])
def stgcompliance():
        
    try:
               
        storage_account_pvt_json = {}
        storage_account_pub_json = {}
        storage_account_tls_json = {}
        storage_account_enc_json = {}   
        storage_account_diag_json = {}
        blob_diag_json = {}
        table_diag_json = {}
        file_diag_json = {}
        queue_diag_json = {}
        storage_account_checks_list = []
        resource_pvt_name = []
        resource_tls_name = []
        resource_enc_name = []
        resource_pub_name = []
        stg_diag = []
        blob_diag = []
        que_diag = []
        file_diag = []
        table_diag = []
        stg_acct_uri = "https://management.azure.com/subscriptions/"+query_data_subscription+"/providers/Microsoft.Storage/storageAccounts?api-version=2021-09-01"
        req_headers = {'Authorization': 'Bearer ' +
                       json.loads(mgmtresponse.text)['access_token'], 'Content-Type': 'Application/JSON'}
        res_response = json.loads(requests.get(url=stg_acct_uri, headers=req_headers).text)
        for items in res_response['value']:
            if len(items['properties']['privateEndpointConnections']) == 0:
                resource_pvt_name.append(items['name'])
        if len(resource_pvt_name) != 0:
            storage_account_pvt_json['ComplianceName'] = "All Storage accounts must have private end point connections"
            storage_account_pvt_json['Status'] = "Failed"
            storage_account_pvt_json['Resource'] = str(",".join(resource_pvt_name))
            storage_account_checks_list.append(storage_account_pvt_json.copy())
        else:
            storage_account_pvt_json['ComplianceName'] = "All Storage accounts must have private end point connections"
            storage_account_pvt_json['Status'] = "Passed"
            
                
        for items in res_response['value']:
            if items['properties']['minimumTlsVersion'] != "TLS1_2":
                resource_tls_name.append(items['name'])
        
        if len(resource_tls_name) != 0:
            storage_account_tls_json['ComplianceName'] = "All Storage accounts must have at least TLS 1.2"
            storage_account_tls_json['Status'] = "Failed"
            storage_account_tls_json['Resource'] = str(",".join(resource_tls_name))
            storage_account_checks_list.append(storage_account_tls_json.copy())
        else:
            storage_account_tls_json['ComplianceName'] = "All Storage accounts must have at least TLS 1.2"
            storage_account_tls_json['Status'] = "Passed"
                       
                 
                
        for items in res_response['value']:            
            if items['properties']['encryption']['keySource'] != "Microsoft.Keyvault":
                resource_enc_name.append(items['name'])
        
        if len(resource_enc_name) != 0:
            storage_account_enc_json['ComplianceName'] = "All Storage accounts must have customer managed encryption"
            storage_account_enc_json['Status'] = "Failed"
            storage_account_enc_json['Resource'] = str(",".join(resource_enc_name))
            storage_account_checks_list.append(storage_account_enc_json.copy())                                        
        else:
            storage_account_enc_json['ComplianceName'] = "All Storage accounts must have customer managed encryption"
            storage_account_enc_json['Status'] = "Passed"
            
                
        for items in res_response['value']:
            if items['properties']['networkAcls']['defaultAction']  == 'Allow':
                resource_pub_name.append(items['name'])
                   
        if len(resource_pub_name) != 0:
            storage_account_pub_json['ComplianceName'] = "All Storage accounts must have public network disabled"
            storage_account_pub_json['Status'] = "Failed"
            storage_account_pub_json['Resource'] = str(",".join(resource_pub_name))
            storage_account_checks_list.append(storage_account_pub_json.copy()) 
        else:
            storage_account_pub_json['ComplianceName'] = "All Storage accounts must have public network disabled"
            storage_account_pub_json['Status'] = "Passed"
            
        for items in res_response['value']:
            stg_diag_uri = "https://management.azure.com"+items['id']+"/providers/Microsoft.Insights/diagnosticSettings?api-version=2021-05-01-preview"
            req_headers = {'Authorization': 'Bearer ' + json.loads(mgmtresponse.text)['access_token'], 'Content-Type': 'Application/JSON'}
            res_response = json.loads(requests.get(url=stg_diag_uri, headers=req_headers).text)
            if len(res_response['value']) == 0:
                stg_diag.append(items['name'])
                
        if len(stg_diag) != 0:
            storage_account_diag_json['ComplianceName'] = "All Storage accounts must have diagnostic enabled"
            storage_account_diag_json['Status'] = "Failed"
            storage_account_diag_json['Resource'] = str(",".join(stg_diag))
            storage_account_checks_list.append(storage_account_diag_json.copy())    
            
        for items in res_response['value']:
            blob_diag_uri = "https://management.azure.com"+items['id']+"/blobServices/default/providers/Microsoft.Insights/diagnosticSettings?api-version=api-version=2021-05-01-preview"
            print(blob_diag_uri)
            req_headers = {'Authorization': 'Bearer ' + json.loads(mgmtresponse.text)['access_token'], 'Content-Type': 'Application/JSON'}
            res_response = json.loads(requests.get(url=blob_diag_uri, headers=req_headers).text)
            print(res_response)
            if len(res_response['value']) == 0:
                blob_diag.append(items['name'])
                
        if len(blob_diag) != 0:
            blob_diag_json['ComplianceName'] = "All Storage accounts BLOB Service must have diagnostic enabled"
            blob_diag_json['Status'] = "Failed"
            blob_diag_json['Resource'] = str(",".join(blob_diag))
            storage_account_checks_list.append(blob_diag_json.copy()) 
            
        for items in res_response['value']:
            table_diag_uri = "https://management.azure.com"+items['id']+"/tableServices/default/providers/Microsoft.Insights/diagnosticSettings?api-version=api-version=2021-05-01-preview"
            req_headers = {'Authorization': 'Bearer ' + json.loads(mgmtresponse.text)['access_token'], 'Content-Type': 'Application/JSON'}
            res_response = json.loads(requests.get(url=table_diag_uri, headers=req_headers).text)
            if len(res_response['value']) == 0:
                table_diag.append(items['name'])
                
        if len(table_diag) != 0:
            table_diag_json['ComplianceName'] = "All Storage accounts TABLE Service must have diagnostic enabled"
            table_diag_json['Status'] = "Failed"
            table_diag_json['Resource'] = str(",".join(table_diag))
            storage_account_checks_list.append(table_diag_json.copy())    
            
        for items in res_response['value']:
            file_diag_uri = "https://management.azure.com"+items['id']+"/fileServices/default/providers/Microsoft.Insights/diagnosticSettings?api-version=api-version=2021-05-01-preview"
            req_headers = {'Authorization': 'Bearer ' + json.loads(mgmtresponse.text)['access_token'], 'Content-Type': 'Application/JSON'}
            res_response = json.loads(requests.get(url=file_diag_uri, headers=req_headers).text)
            if len(res_response['value']) == 0:
                file_diag.append(items['name'])
                
        if len(file_diag) != 0:
            file_diag_json['ComplianceName'] = "All Storage accounts FILE Service must have diagnostic enabled"
            file_diag_json['Status'] = "Failed"
            file_diag_json['Resource'] = str(",".join(file_diag))
            storage_account_checks_list.append(file_diag_json.copy()) 
            
        for items in res_response['value']:
            queue_diag_uri = "https://management.azure.com"+items['id']+"/queueServices/default/providers/Microsoft.Insights/diagnosticSettings?api-version=2021-09-01"
            req_headers = {'Authorization': 'Bearer ' + json.loads(mgmtresponse.text)['access_token'], 'Content-Type': 'Application/JSON'}
            res_response = json.loads(requests.get(url=queue_diag_uri, headers=req_headers).text)
            if len(res_response['value']) == 0:
                que_diag.append(items['name'])
                
        if len(que_diag) != 0:
            queue_diag_json['ComplianceName'] = "All Storage accounts FILE Service must have diagnostic enabled"
            queue_diag_json['Status'] = "Failed"
            queue_diag_json['Resource'] = str(",".join(que_diag))
            storage_account_checks_list.append(queue_diag_json.copy())
            
    except ClientAuthenticationError as ex:
        print(ex.message)
        
    finally:
        return render_template("stgcompliance.html", stg_compliance = storage_account_checks_list)
    
@app.route('/sqlcompliance', methods=['GET', 'POST'])
def sqlcompliance():
    try:
        sql_pvt_json={}
        sql_pvt=[]
        sql_aad_json={}
        sql_aad=[]
        sql_pri_json={}
        sql_pri=[]
        sql_aadonly_json = {}
        sql_aadonly=[]
        sql_pub_json={}
        sql_pub=[]
        sql_auth_json={}
        sql_auth=[]
        
        sql_check_list=[]
        sql_uri = "https://management.azure.com/subscriptions/"+query_data_subscription+"/providers/Microsoft.Sql/servers?api-version=2020-11-01-preview"
        req_headers = {'Authorization': 'Bearer ' +
                       json.loads(mgmtresponse.text)['access_token'], 'Content-Type': 'Application/JSON'}
        res_sql = json.loads(requests.get(
            url=sql_uri, headers=req_headers).text)
        for items in res_sql['value']:
            if len(items['properties']['privateEndpointConnections']) == 0:
                sql_pvt.append(items['name'])
                
        if len(sql_pvt) != 0:
            sql_pvt_json['ComplianceName'] = "All SQLs must have private end point connections"
            sql_pvt_json['Status'] = "Failed"
            sql_pvt_json['Resource'] = str(",".join(sql_pvt))
            sql_check_list.append(sql_pvt_json.copy())
        else:
            sql_pvt_json['ComplianceName'] = "All Storage accounts must have at least TLS 1.2"
            sql_pvt_json['Status'] = "Passed"
                
        for items in res_sql['value']:
            if items['properties']['publicNetworkAccess'] == "Enabled":
                sql_pub.append(items['name'])
                
        if len(sql_pub) != 0:
            sql_pub_json['ComplianceName'] = "All SQLs must have public network disabled"
            sql_pub_json['Status'] = "Failed"
            sql_pub_json['Resource'] = str(",".join(sql_pub))
            sql_check_list.append(sql_pub_json.copy())
        else:
            sql_pub_json['ComplianceName'] = "All SQLs must have public network disabled"
            sql_pub_json['Status'] = "Passed"  
        
        for items in res_sql['value']:
            if 'administrators' in (items['properties']).keys():
                if 'azureADOnlyAuthentication' in (items['properties']['administrators']).keys() and items['properties']['administrators']['azureADOnlyAuthentication'] != 'true':
                    sql_aadonly.append(items['name'])
                elif 'administrators' in (items['properties']).keys() and items['properties']['administrators']['principalType'] != "Group":
                    sql_pri.append(items['name'])
                elif 'administrators' in (items['properties']).keys() and items['properties']['administrators']['administratorType'] != "ActiveDirectory":
                    sql_aad.append(items['name'])
            else:
                sql_auth.append(items['name'])
        
        if len(sql_auth) != 0:
            sql_auth_json['ComplianceName'] = "All SQLs must have AD authentication enabled"
            sql_auth_json['Status'] = "Failed"
            sql_auth_json['Resource'] = str(",".join(sql_auth))
            sql_check_list.append(sql_auth_json.copy())
        
        if len(sql_aadonly) != 0:
            sql_aadonly_json['ComplianceName'] = "All SQLs must have only AAD authentication"
            sql_aadonly_json['Status'] = "Failed"
            sql_aadonly_json['Resource'] = str(",".join(sql_aadonly))
            sql_check_list.append(sql_aadonly_json.copy())
            
        if len(sql_pri) != 0:
            sql_pri_json['ComplianceName'] = "All SQLs must have AD group as Active directory owner"
            sql_pri_json['Status'] = "Failed"
            sql_pri_json['Resource'] = str(",".join(sql_pri))
            sql_check_list.append(sql_pri_json.copy())
               
                                     
        
    except ClientAuthenticationError as ex:
        print(ex.message)
        
    finally:
        print(sql_check_list)
        return render_template("sqlcompliance.html", sql_compliance = sql_check_list)
    

@app.route('/kvcompliance', methods=['GET', 'POST'])
def kvcompliance():
    try:
        kv_pub_json={}
        kv_pub=[]
        kv_rbac_json={}
        kv_rbac=[]
        kv_sd_json={}
        kv_sd=[]
        kv_pp_json = {}
        kv_pp=[]
        kv_sku_json={}
        kv_sku=[]
        
        
        kv_check_list=[]
        kv_uri = "https://management.azure.com/subscriptions/"+query_data_subscription+"/providers/Microsoft.KeyVault/vaults?api-version=2021-10-01"
        req_headers = {'Authorization': 'Bearer ' +
                       json.loads(mgmtresponse.text)['access_token'], 'Content-Type': 'Application/JSON'}
        res_kv = json.loads(requests.get(
            url=kv_uri, headers=req_headers).text)
        for items in res_kv['value']:
            if items['properties']['publicNetworkAccess'] == 'Enabled':
                kv_pub.append(items['name'])
                
        if len(kv_pub) != 0:
            kv_pub_json['ComplianceName'] = "All Key Vaults must have public network disabled"
            kv_pub_json['Status'] = "Failed"
            kv_pub_json['Resource'] = str(",".join(kv_pub))
            kv_check_list.append(kv_pub_json.copy())
        else:
            kv_pub_json['ComplianceName'] = "All Key Vaults must have public network disabled"
            kv_pub_json['Status'] = "Passed"
                
        for items in res_kv['value']:
            if items['properties']['enableRbacAuthorization'] == False:
                kv_rbac.append(items['name'])
                
        if len(kv_rbac) != 0:
            kv_rbac_json['ComplianceName'] = "All Key Vaults must have RBAC enabled"
            kv_rbac_json['Status'] = "Failed"
            kv_rbac_json['Resource'] = str(",".join(kv_rbac))
            kv_check_list.append(kv_rbac_json.copy())
        else:
            kv_rbac_json['ComplianceName'] = "All Key Vaults must have RBAC enabled"
            kv_rbac_json['Status'] = "Passed"  
            
        for items in res_kv['value']:
            if items['properties']['enableSoftDelete'] == False:
                kv_sd.append(items['name'])
                
        if len(kv_sd) != 0:
            kv_sd_json['ComplianceName'] = "All Key Vaults must have Soft Delete enabled"
            kv_sd_json['Status'] = "Failed"
            kv_sd_json['Resource'] = str(",".join(kv_sd))
            kv_check_list.append(kv_sd_json.copy())
        else:
            kv_sd_json['ComplianceName'] = "All Key Vaults must have Soft Delete enabled"
            kv_sd_json['Status'] = "Passed" 
        
        for items in res_kv['value']:
            if items['properties']['enablePurgeProtection'] == False:
                kv_pp.append(items['name'])
                
        if len(kv_pp) != 0:
            kv_pp_json['ComplianceName'] = "All Key Vaults must have Purge protection enabled"
            kv_pp_json['Status'] = "Failed"
            kv_pp_json['Resource'] = str(",".join(kv_pp))
            kv_check_list.append(kv_pp_json.copy())
        else:
            kv_pp_json['ComplianceName'] = "All Key Vaults must have Purge protection enabled"
            kv_pp_json['Status'] = "Passed" 
            
        for items in res_kv['value']:
            if items['properties']['sku']['name'] != "Premium":
                kv_sku.append(items['name'])
                
        if len(kv_sku) != 0:
            kv_sku_json['ComplianceName'] = "All Key Vaults must have premium SKU"
            kv_sku_json['Status'] = "Failed"
            kv_sku_json['Resource'] = str(",".join(kv_sku))
            kv_check_list.append(kv_sku_json.copy())
        else:
            kv_sku_json['ComplianceName'] = "All Key Vaults must have premium SKU"
            kv_sku_json['Status'] = "Passed"
        
               
                                     
        
    except ClientAuthenticationError as ex:
        print(ex.message)
        
    finally:
        
        return render_template("kvcompliance.html", kv_compliance = kv_check_list)
                
        
            
    
             


if __name__ == '__main__':
    app.run()

        