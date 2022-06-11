x =  {
            "id": "/subscriptions/6e268af1-b2a7-44a7-9a1a-9025889dbe5d/resourceGroups/NEO-RBAC-WEBAPP/providers/Microsoft.ManagedIdentity/userAssignedIdentities/NEO-RBAC-WEBAPPIN",
            "name": "NEO-RBAC-WEBAPPIN",
            "type": "Microsoft.ManagedIdentity/userAssignedIdentities",
            "location": "eastus",
            "tags": {}
        }

#print(x)
print(type(x))

if 'name' in x:
  print('yes')