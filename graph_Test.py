import requests

url = "https://login.microsoftonline.com/e18a0c35-c3ed-46f4-8e69-018ca67f8288/oauth2/v2.0/token"

payload = 'grant_type=client_credentials&client_secret=2fG8Q~LNHsgveTV1FGW8Dg9Esme84ALK9Cm2Pdw2&client_id=2b0ce5a8-0146-4b0c-a7ef-eccdb99b555b&scope=https%3A%2F%2Fgraph.microsoft.com%2F.default'
headers = {
    'content-type': 'application/x-www-form-urlencoded',
    'Cookie': 'esctx=AQABAAAAAAD--DLA3VO7QrddgJg7WevrxRwJM58XrDX6xb39CqEHR-8AoZWxZfy9jImPXv8z4iORWfzFMDCFPV-vPczQa6JzmTh2oSlXtL2ia8S7JWulE05vGt2xeMUXjDU7QPWGZpht8XplDm1CGkKgKRADyl6l7m_gnj7RLlr7-3pAhVAomTflZ1XoY-y_y6lIspXQLFkgAA; fpc=Ah-5rgbocY9HkIaOAn1DTWuoxdgDAQAAAKSpKtoOAAAA; stsservicecookie=estsfd; x-ms-gateway-slice=estsfd'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
