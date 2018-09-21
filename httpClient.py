import httplib2
import sys
import requests
import json

# get http server ip
http_server = 'http://localhost:8000'
# create a connection
conn = httplib2.HTTPConnectionWithTimeout(http_server)

values = {
    'name': 'Thomas Anderson',
    'location': 'unknown'
}


    # request command to server
response = requests.post(url="http://localhost:8000", data=values)
print(response)
print(response.text)

# get response from server
# rsp = conn.getresponse()

# print server response and data
# print(rsp.status, rsp.reason)
# data_received = rsp.read()
# print(data_received)

conn.close()