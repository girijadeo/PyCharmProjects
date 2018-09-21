import socket
# import CreateBug
import requests
import json
from requests_ntlm import HttpNtlmAuth
import base64


def createTFSBug(project_name_in_TFS, **kwargs):
    session = requests.session()
    if "title" in kwargs:
        title = kwargs['title']
    else:
        title = "Default Title"

    if "repro_steps" in kwargs:
        repro_steps = kwargs['repro_steps']
    else:
        repro_steps = "Default Repro Steps"

    if "priority" in kwargs:
        priority = kwargs['priority']
    else:
        priority = '1'

    if "severity" in kwargs:
        severity = kwargs['severity']
    else:
        severity = "3 - Medium"

    if "worktype" in kwargs:
        worktype = kwargs['worktype']
    else:
        worktype = "Maintenance/Support"

    data = [

        {
            "op": "add",
            "path": "/fields/System.Title",
            "value": title
        },
        {
            "op": "add",
            "path": "/fields/Microsoft.VSTS.TCM.ReproSteps",
            "value": repro_steps
        },
        {
            "op": "add",
            "path": "/fields/Microsoft.VSTS.Common.Priority",
            "value": priority
        },
        {
            "op": "add",
            "path": "/fields/Microsoft.VSTS.Common.Severity",
            "value": severity
        },
        {
            "op": "add",
            "path": "/fields/CBRE.WorkType",
            "value": worktype
        }
    ]

    project_name_in_TFS = project_name_in_TFS
    url = "http://tfs.cbre.com:8080/tfs/CBRE01/"+project_name_in_TFS+"/_apis/wit/workitems/$Bug?api-version=1.0"

    http_headers = {"Content-Type": "application/json-patch+json"}
    data_dump = json.dumps(data)

    decoded_password = base64.decodebytes(b'T2N0MjAxNyM=')
    decoded_password_string = decoded_password.decode('utf-8')

    response = session.patch(url=url, data=data_dump, headers=http_headers,
                             auth=HttpNtlmAuth('US\\gdeo', decoded_password_string))

    print("Response code = ", response)

    response_text = response.json()
    print(response_text)
    defect_ID = str(response_text['id'])
    print(defect_ID)
    assert "200" in str(response), "FAIL"
    return defect_ID, response_text


def Main():
    host = 'localhost'
    port = 8000

    s = socket.socket()
    s.bind((host,port))
    s.listen(1)
    print("serving at port", host, port)
    conn, addr = s.accept()
    print("Connection received from :" +str(addr))
    # while True:
    data_from_client = conn.recv(1024)
    data_json = json.loads(data_from_client.decode("utf-8"))
    title = data_json['title']
    repro_steps = data_json['repro_steps']
    priority = data_json['priority']
    project_name_in_TFS = data_json['project_name_in_TFS']
    defect_ID, response_text = createTFSBug(project_name_in_TFS=project_name_in_TFS,title=title,repro_steps=repro_steps,priority=priority)
    jsonResponse = json.dumps(response_text)
    conn.send(jsonResponse.encode('utf-8'))
    # conn.close()

if __name__=='__main__':
    Main()