import requests
def submit_request(token, request_method, url, payload={}):
    headers = {
        'Accept': 'application/json',
        'Authorization': 'Bearer ' + token["access_token"]
    }
    
    response = requests.request(request_method, url, headers=headers, data=payload)
    print("Response Code: {0}\nResponse Body: {1}".format(response.status_code, response.text))
    
    return response