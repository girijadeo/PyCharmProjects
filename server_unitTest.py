import requests
import json
from requests_ntlm import HttpNtlmAuth
import socket
import unittest

# Load the json file for data
with open('config.json') as json_data:
    jsonData = json.load(json_data)

# TFS credentials from the json file
TFS_username = jsonData['TFS_username']
TFS_password = jsonData['TFS_password']

session = requests.session()


class DefectFilingService(unittest.TestCase):

    def setUp(self):
        pass


    # ***************This function is used for creating a new bug in TFS*********************
    def createTFSBug(project_name_in_TFS, title, repro_steps, **kwargs):

        # Setting defaults values for the optional parameters
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

        if "SystemInfo" in kwargs:
            SystemInfo = kwargs['SystemInfo']
        else:
            SystemInfo = ""

        if "history" in kwargs:
            history = kwargs['history']
        else:
            history = ""

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
            },
            {
                "op": "add",
                "path": "/fields/Microsoft.VSTS.TCM.SystemInfo",
                "value": SystemInfo
            },
            {
                "op": "add",
                "path": "/fields/System.History",
                "value": history
            }
        ]

        url = "http://tfs.cbre.com:8080/tfs/CBRE01/" + project_name_in_TFS + "/_apis/wit/workitems/$Bug?api-version=1.0"

        http_headers = {"Content-Type": "application/json-patch+json"}
        data_dump = json.dumps(data)

        response = session.patch(url=url, data=data_dump, headers=http_headers,
                                 auth=HttpNtlmAuth(TFS_username, TFS_password))

        # print("Response code = ", response)

        response_text = response.json()
        # print(response_text)
        defect_ID = str(response_text['id'])
        print(defect_ID)
        assert "200" in str(response), "FAIL"
        return response, response_text

    # **************************This function is used for searching an existing bug in TFS**********************************
    def searchBug(searchby, **kwargs):

        url = ""

        # 1. Search a single ID
        if (searchby == "id"):
            url = "http://tfs.cbre.com:8080/tfs/CBRE01/_apis/wit/workitems/" + kwargs['id'] + "?api-version=1.0"

        # 2. Search multiple IDs
        elif (searchby == "ids"):
            url = "http://tfs.cbre.com:8080/tfs/CBRE01/_apis/wit/workitems?ids=" + kwargs['ids'] + "&api-version=1.0"

        # 3. Search by date
        elif (searchby == "date"):
            url = "http://tfs.cbre.com:8080/tfs/CBRE01/_apis/wit/workitems?ids=" + kwargs[
                'ids'] + "&fields=System.Id,System.Title,System.WorkItemType,Microsoft.VSTS.Scheduling.RemainingWork&asOf=" + \
                  kwargs['date'] + "&api-version=1.0"

        headers = {"User-Agent": "Request"}
        response = session.get(url=url, headers=headers, auth=HttpNtlmAuth(TFS_username, TFS_password))
        response_text = response.text
        assert "200" in str(response), "FAIL"
        return response, response_text

    # ***************************This function is used to update the fields of an existing bug******************************
    # NOTE : Currently only title and repro_steps can be udpated, provision to update other fields will be added in future

    def updateBug(id, updated_title, updated_repro_steps):
        data = [

            {
                "op": "add",
                "path": "/fields/System.Title",
                "value": updated_title
            },
            {
                "op": "add",
                "path": "/fields/Microsoft.VSTS.TCM.ReproSteps",
                "value": updated_repro_steps
            }
        ]

        url = "http://tfs.cbre.com:8080/tfs/CBRE01/_apis/wit/workItems/" + id + "?api-version=1.0"
        http_headers = {"Content-Type": "application/json-patch+json"}
        data_dump = json.dumps(data)
        response = session.patch(url=url, data=data_dump, headers=http_headers,
                                 auth=HttpNtlmAuth(TFS_username, TFS_password))
        response_text = response.json()
        assert "200" in str(response), "FAIL"
        return response, response_text

    def test_Main(self):

        # Declaring variables
        id = ""
        ids = ""
        date = ''

        # ****Enter the host IP here:
        host = 'localhost'
        port = 8000

        s = socket.socket()
        s.bind((host, port))
        s.listen(10)

        print("Serving at : ", host, port)

        while True:  # ********Setting an infinite loop, so that the server is forever on, unless explicitly stopped
            conn, addr = s.accept()
            print("Connection received from :" + str(addr))
            data_from_client = conn.recv(1024)
            # if not data_from_client: continue
            decoded_data_from_client = data_from_client.decode("utf-8")

            json_part_of_decoded_data_from_client = (decoded_data_from_client.split('\r\n\r\n'))[1]
            data_json_string = json_part_of_decoded_data_from_client.strip()

            data_json = json.loads(data_json_string)

            # ***********Check for the required action - create/search/update***********************************************

            # 1. CREATE
            if data_json['action'] == 'create':
                title = data_json['title']
                repro_steps = data_json['repro_steps']
                # priority = data_json['priority']
                project_name_in_TFS = data_json['project_name_in_TFS']

                # ********Setting defaults values for the optional parameters
                if 'priority' in data_json:
                    priority = data_json['priority']
                else:
                    priority = '1'

                if 'SystemInfo' in data_json:
                    SystemInfo = data_json['SystemInfo']
                else:
                    SystemInfo = ""

                if "severity" in data_json:
                    severity = data_json['severity']
                else:
                    severity = "3 - Medium"

                if "history" in data_json:
                    history = data_json['history']
                else:
                    history = ""

                # *********Calling the createTFSBug() function to create a new bug
                response_code, response_text = DefectFilingService.createTFSBug(project_name_in_TFS=project_name_in_TFS, title=title,
                                                            repro_steps=repro_steps, priority=priority,
                                                            severity=severity, SystemInfo=SystemInfo, history=history)
            # ________________________________________________________________________

            # 2. SEARCH
            elif data_json['action'] == 'search':
                searchby = data_json['searchby']
                if searchby == 'id':
                    id = data_json['id']
                elif searchby == 'ids':
                    ids = data_json['ids']
                elif searchby == 'date':
                    date = data_json['date']
                    ids = data_json['ids']

                response_code, response_text = DefectFilingService.searchBug(searchby=searchby, id=id, ids=ids, date=date)
            # __________________________________________________________________________

            # 3. UDPATE
            elif data_json['action'] == 'update':
                title = data_json['title']
                repro_steps = data_json['repro_steps']
                id = data_json['id']
                response_code, response_text = DefectFilingService.updateBug(id=id, updated_title=title, updated_repro_steps=repro_steps)
            # ____________________________________________________________________________


            print("Response code = ", response_code)
            print(response_text)
            jsonResponse = json.dumps(response_text)
            status_code = response_code.status_code
            reason = response_code.reason

            # ********Sending the response code to the client*************************************************
            response_proto = 'HTTP/1.1'.encode()
            response_status = str(status_code).encode()
            response_status_text = reason.encode()

            conn.send(b'%s %s %s\r\n\r\n' % (response_proto, response_status,
                                             response_status_text))

            # *********Sending the response body(which is in json format) to the client************************
            conn.send(jsonResponse.encode())

            conn.close()


if __name__ == '__main__':
    unittest.main()