from tabulate import tabulate
from dotenv import load_dotenv
import requests
import json
import csv
import os

import datetime
import time
import pytz

# Load environment variables from .env file
load_dotenv()

auth_url = "https://auth.apps.paloaltonetworks.com/oauth2/access_token"
client_id = os.getenv("PRISMA_CLIENT_ID")
client_secret = os.getenv("PRISMA_SECRET_KEY")
tsg_id = os.getenv("PRISMA_TSG_ID")

address_url_prefix = "https://api.sase.paloaltonetworks.com/sse/config/v1/addresses/"
address_url = "https://api.sase.paloaltonetworks.com/sse/config/v1/addresses?folder=All"

csv_file = "export_objects_addresses_full.csv"
tags_csv_file = "export_objects_tags_full.csv"

prisma_topics = [["1", "Objects:Addresses"],["2", "Objects:Tags"]]
# login_timestamp = datetime.datetime.utcnow()

def login():
    data = {
        "grant_type": "client_credentials",
        "scope": f"tsg_id:{tsg_id}"
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    # Encode client_id and client_secret for HTTP Basic Authentication
    auth = (client_id, client_secret)

    response = requests.post(auth_url, data=data, headers=headers, auth=auth)
    json_response = response.json()
    
    print(json_response)
    return json_response


def validate_token():
    global login_timestamp
    global token
    # Default token is expired in 15 minutes. Minus 60 seconds for refresh token in 14 minutes.
    expire_in_seconds = token["expires_in"] - 60
    # Calculate the expiration time based on 'expires_in' duration
    expiration_time_utc = login_timestamp + datetime.timedelta(seconds=expire_in_seconds)
    # print("Time UTC Token Expire: {0}".format(expiration_time_utc))
    
    # Convert expiration time to Bangkok timezone
    current_time_utc = datetime.datetime.utcnow()
    bangkok_timezone = pytz.timezone('Asia/Bangkok')
    current_time_bangkok = current_time_utc.replace(tzinfo=pytz.utc).astimezone(bangkok_timezone)
    expiration_time_bangkok = expiration_time_utc.replace(tzinfo=pytz.utc).astimezone(bangkok_timezone)
    print("Time Zone Now: {0}".format(current_time_bangkok))
    print("Time Zone Expiration: {0}".format(expiration_time_bangkok))
    
    if expiration_time_utc < current_time_utc:
        print("Token Expired!!")
        print("Refresh Token...")
        token = login()
        login_timestamp = datetime.datetime.utcnow()

    return token


def get_address_id():
    global token
    final_url = address_url + '&limit=10000'
    payload={}
    headers = {
        'Accept': 'application/json',
        'Authorization': 'Bearer ' + token["access_token"]
    }

    response = requests.request("GET", final_url, headers=headers, data=payload)
    print(response.json())
    return response.json()


def send_request(address, action):
    global token
    validate_token()
    method = None
    
    headers = {
        'Accept': 'application/json',
        'Authorization': 'Bearer ' + token["access_token"]
    }
    
    if action == 'Create' or action == 'c':
        method = "POST"
        final_url = address_url
        if address[2] == 'IP Netmask':
            payload={
                "description": "",
                "name": address[0],
                "ip_netmask": address[3]
            }
        elif address[2] == 'IP Range':
            payload={
                "description": "",
                "name": address[0],
                "ip_range": address[3]
            }
        elif address[2] == 'FQDN':
            payload={
                "description": "",
                "name": address[0],
                "fqdn": address[3]
            }     

    elif action == 'Delete' or action == 'd':
        final_url = address_url_prefix + address
        method = "DELETE"
        payload={}

    response = requests.request(method, final_url, headers=headers, data=payload)
    print(response.text)


def config_address(action):
    global token
    if action == 'Create' or action == 'c':
        with open(csv_file, newline='') as csvfile:
            csv_reader = csv.reader(csvfile, delimiter=',')
            next(csv_reader) # skip first line
            for row in csv_reader:
                send_request(row, action)
    elif action == 'Delete' or action == 'd':
        address_lists = get_address_id()
        for each_address in address_lists['data']:
            if each_address['name'] != "Palo Alto Networks Sinkhole":
                print(each_address['id'])
                send_request(each_address['id'], action)


def config_tags(action):
    global token
    print(token)
    # if action == 'Create' or action == 'c':
    #     with open(tags_csv_file, newline='') as csvfile:
    #         csv_reader = csv.reader(csvfile, delimiter=',')
    #         next(csv_reader) # skip first line
                

def test_token(token):
    for i in range(20):
        token = validate_token(token)
        print(token)
        time.sleep(95)

def main():
    action = input("Enter Action Type(Create[c] | Delete[d]): ")
    if action == 'Create' or action == 'c':
        print(tabulate(prisma_topics, headers=["No.", "Topic Detail"], tablefmt="pretty"))
        topic_create = input("Please select number topic to create: ")
    global token
    token = login()
    global login_timestamp 
    login_timestamp = datetime.datetime.utcnow()
    # print("Token: {0}".format(token["access_token"]))
    
    if topic_create == 1:
        config_address(action)
    elif topic_create == 2:
        config_tags(action)

if __name__ == "__main__":
    main()