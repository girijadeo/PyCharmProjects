# from socket import socket
from json import JSONDecodeError

import requests
import json
from requests_ntlm import HttpNtlmAuth
import socket
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime


#Load the json file for data
with open('config.json') as json_data:
    jsonData = json.load(json_data)

#TFS credentials from the json file
TFS_username = jsonData['TFS_username']
TFS_password = jsonData['TFS_password']
TFS_prod_URL = jsonData['tfs_prod']
TFS_test_URL = jsonData['tfs_test']

session = requests.session()
# print(str(datetime.now()))

# This function is used to integrate the defect service with the metrics service
def postToMetricService(env,action, application_id,automation_tool_id):
    if env =="prod":
        url="https://devopsmetricsservice.azurewebsites.net/api/metrics/submit"
    else:
        url = "https://stg-devopsmetricsservice.azurewebsites.net/api/metrics/submit"

    if action=="create":
        AutomationProcessId=jsonData["AutomationProcessId_create"]
    elif action=="update":
        AutomationProcessId=jsonData["AutomationProcessId_update"]
    else:
        AutomationProcessId = jsonData["AutomationProcessId_search"]

    http_headers = {"Content-Type": "application/json"}
    data = {
	"ApplicationId": application_id,
	"AutomationProcessId": AutomationProcessId,
	"AutomationToolId": automation_tool_id,
	"Description": "Testing the automated defect service integration with metrics service",
	"Version": "4.0",
	"Cycle": "Automatic Defect management service",
	"StartDateTime": str(datetime.now()),
	"EndDateTime": str(datetime.now())

    }
    data_dump = json.dumps(data)

    response = session.post(url=url, data=data_dump, headers=http_headers)

    response_text = response.text
    print (response_text)
    return response_text

# This function is used to send the HTTP response code and text to the client
def sendHTTPresponse(status_code,reason,response_text,conn):
    response_proto = 'HTTP/1.1'.encode()
    response_status = str(status_code).encode()
    response_status_text = reason.encode()
    encoded_response_text = str(response_text).encode()

    conn.send(b'%s %s %s %s\r\n\r\n' % (response_proto, response_status,
                                        response_status_text, encoded_response_text))
    conn.send((reason+" - "+response_text).encode())

def createLogFile(logger_name,fileName):
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(logger_name)

    # create a file handler
    handler = TimedRotatingFileHandler(filename=fileName+'.log', when='midnight', interval=1, backupCount=5)
    # handler.suffix = "%Y%m%d"
    logger.addHandler(handler)
    handler.setLevel(logging.INFO)
    # handler.setLevel(logging.DEBUG)

    # create a logging format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    return logger

logger_response = createLogFile("logger_response","APIresponse")
logger_request = createLogFile("logger_request","APIrequestJSON")

# ***************This function is used for creating a new bug in TFS*********************
def createTFSBug(tfs_env,project_name_in_TFS,title, repro_steps,application_id_for_metrics_service,automation_tool_id, **kwargs):

    try:
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

        tfs_env = tfs_env

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

        if tfs_env=="prod":
            url = TFS_prod_URL+project_name_in_TFS+"/_apis/wit/workitems/$Bug?api-version=1.0"

            # url = "http://tfs.cbre.com:8080/tfs/CBRE01/"+project_name_in_TFS+"/_apis/wit/workitems/$Bug?api-version=1.0"
        else:
            url = TFS_test_URL+project_name_in_TFS+"/_apis/wit/workitems/$Bug?api-version=1.0"

        http_headers = {"Content-Type": "application/json-patch+json"}
        data_dump = json.dumps(data)


        response = session.patch(url=url, data=data_dump, headers=http_headers,
                                 auth=HttpNtlmAuth(TFS_username, TFS_password))



        response_text = response.json()
        response_text_metrics_service=postToMetricService(tfs_env, "create", application_id_for_metrics_service,automation_tool_id)
        logger_response.info("Response text = " + str(response_text)+
                             "****response_text_metrics_service= "+response_text_metrics_service)
    except ConnectionRefusedError:
        print("ConnectionRefusedError : No connection could be made because the target machine actively refused it")
        response="ConnectionRefusedError"
        response_text="ConnectionRefusedError : No connection could be made because the target machine actively refused it"
        # sendHTTPresponse("400",response,response_text,conn)
        logger_response.info("ConnectionRefusedError : No connection could be made because the target machine actively refused it")

    return response, response_text

# **************************This function is used for searching an existing bug in TFS, using the project name and defect title**********************************
def searchBug(tfs_env,project_name_in_tfs, defect_title_to_search,
              application_id_for_metrics_service, automation_tool_id):
    session = requests.session()
    data = {"query": "Select [System.Id] From WorkItems "
                      "Where [System.WorkItemType] = 'Bug' "
                      "AND [System.TeamProject] = '"+project_name_in_tfs+"'"
                      "AND [System.Title] = '"+defect_title_to_search+"'"
                      "AND [State] <> 'Closed' "
                      "AND [State] <> 'Removed' "
                      "order by [Microsoft.VSTS.Common.Priority] asc, [System.CreatedDate] desc"}

    if tfs_env=="prod":
        url = TFS_prod_URL+"_apis/wit/wiql?api-version=1.0"
    else:
        url = TFS_test_URL+"_apis/wit/wiql?api-version=1.0"

    http_headers = {"Content-Type": "application/json"}
    data_dump = json.dumps(data)

    response = session.post(url=url, data=data_dump, headers=http_headers,
                             auth=HttpNtlmAuth(TFS_username, TFS_password))

    response_text = response.json()
    response_text_metrics_service = postToMetricService(tfs_env, action="search",
                                                        application_id=application_id_for_metrics_service,
                                                        automation_tool_id=automation_tool_id)
    logger_response.info("Response text = " + str(response_text) +
                         "****response_text_metrics_service= "
                         + response_text_metrics_service)
    return response, response_text

# ***************************This function is used to update the fields of an existing bug******************************
# NOTE : Currently only title, defect status and repro_steps can be udpated, provision to update other fields will be added in future

def updateBug(tfs_env,id,attribute_to_update,updated_title,updated_repro_steps,defectStatus_to_update,application_id_for_metrics_service,automation_tool_id):

    data =[]

    if attribute_to_update=='title':
        data = [

            # title,

            {
                "op": "add",
                "path": "/fields/System.Title",
                "value": updated_title
            }
            ]

    elif attribute_to_update == 'repro_steps':
        data = [
            {
                "op": "add",
                "path": "/fields/Microsoft.VSTS.TCM.ReproSteps",
                "value": updated_repro_steps
            }
            ]
    elif attribute_to_update == 'defect_status':
        data = [
            {
                "op": "add",
                "path": "/fields/State",
                "value": defectStatus_to_update
            }
            ]

    if tfs_env=="prod":
        url = TFS_prod_URL+"_apis/wit/workItems/"+id+"?api-version=1.0"
    else:
        url = TFS_test_URL+"_apis/wit/workItems/"+id+"?api-version=1.0"

    http_headers = {"Content-Type": "application/json-patch+json"}
    data_dump = json.dumps(data)
    response = session.patch(url=url, data=data_dump, headers=http_headers,
                             auth=HttpNtlmAuth(TFS_username, TFS_password))
    response_text = response.json()
    response_text_metrics_service=postToMetricService(tfs_env,action="search",application_id=application_id_for_metrics_service,
                        automation_tool_id=automation_tool_id)
    logger_response.info("Response text = " + str(response_text)+
    "****response_text_metrics_service= " + response_text_metrics_service)
    return response, response_text

def Main():

    # try:
    host = jsonData['hostIP']
    port = jsonData['hostPort']

    s = socket.socket()
    s.bind((host,port))
    s.listen(10)

    print("Serving at : ", host, port)
    # # except ConnectionRefusedError:
    #     print("ConnectionRefusedError : No connection could be made because the target machine actively refused it")
    #     response = "ConnectionRefusedError"
    #     response_text = "ConnectionRefusedError : No connection could be made because the target machine actively refused it"
    #     logger_response.info("ConnectionRefusedError : No connection could be made because the target machine actively refused it")



    while True:             #********Setting an infinite loop, so that the server is forever on, unless explicitly stopped

        # try:
        conn, addr = s.accept()
        print("Connection received from :" +str(addr))
        logger_request.info("Connection received from :" +str(addr))
        logger_response.info("Connection received from :" +str(addr))
        data_from_client = conn.recv(1024)
        print(data_from_client)
        logger_request.info("raw request from client = "+str(data_from_client.decode("utf-8")))
        # if not data_from_client: continue
        decoded_data_from_client = data_from_client.decode("utf-8")

        json_part_of_decoded_data_from_client = (decoded_data_from_client.split('\r\n\r\n'))[1]
        data_json_string = json_part_of_decoded_data_from_client.strip()
        try:
            data_json = json.loads(data_json_string)
            logger_request.info("Request JSON = " +str(data_json))
        except ValueError:
            print("JSON decode error. Invalid JSON")
            sendHTTPresponse("401","ValueError","JSON decode error. Invalid JSON",conn)
            logger_request.info("Raw request = " + str(data_from_client.decode("utf-8")))
            logger_request.info("Raw request JSON = " + data_json_string)
            logger_request.info("Raw request = " + str(data_from_client.decode("utf-8")))
            logger_response.info("JSON decode error. Invalid JSON")
            conn.close()
            continue

        # ***********Check for the required action - create/search/update***********************************************
        try:
            application_id_for_metrics_service = data_json["application_id"]
        except:
            # print("KeyError - Data missing. Mandatory field 'application_id' is missing")
            # conn.send("KeyError - Data missing. Mandatory field 'application_id' is missing".encode())
            sendHTTPresponse("400", "KeyError", "Data missing. Mandatory field 'application_id' is missing", conn)
            conn.close()
            continue


        automation_tool_id = jsonData["automation_tool_id"]
        # 1. CREATE
        if data_json['action'] == 'create':

            try:
                title = data_json['title']
                repro_steps = data_json['repro_steps']
                project_name_in_TFS = data_json['project_name_in_TFS']

                # ********Setting defaults values for the optional parameters
                if "tfs_env" in data_json:
                    tfs_env = data_json["tfs_env"]
                else:
                    tfs_env="test"

                if 'priority'in data_json:
                    priority = data_json['priority']
                else:
                    priority='1'

                if 'SystemInfo'in data_json:
                    SystemInfo = data_json['SystemInfo']
                else:
                    SystemInfo=""

                if "severity" in data_json:
                    severity = data_json['severity']
                else:
                    severity = "3 - Medium"

                if "history" in data_json:
                    history = data_json['history']
                else:
                    history = ""

                # *********Calling the createTFSBug() function to create a new bug
                response_code, response_text = createTFSBug(tfs_env=tfs_env,project_name_in_TFS=project_name_in_TFS,title=title,repro_steps=repro_steps,application_id_for_metrics_service=application_id_for_metrics_service,
                                                            automation_tool_id=automation_tool_id,
                                                            priority=priority,severity=severity,SystemInfo=SystemInfo,history=history)

            except KeyError:
                # conn.send("KeyError - Data invalid or missing".encode())
                logger_request.info("Request JSON = " + str(data_json))
                logger_response.info("KeyError - Data invalid or missing")
                sendHTTPresponse("400", "KeyError", "Data invalid or missing", conn)
                # print("KeyError - Data invalid or missing")
                conn.close()
                continue
        # ________________________________________________________________________

        # 2. SEARCH
        elif data_json['action']=='search':
            try:
                if "tfs_env" in data_json:
                    tfs_env = data_json["tfs_env"]
                else:
                    tfs_env="test"
                project_name_in_tfs=data_json['project_name_in_TFS']
                defect_title_to_search= data_json['defect_title_to_search']

                response_code,response_text= searchBug(tfs_env, project_name_in_tfs,defect_title_to_search,
                                                       application_id_for_metrics_service=application_id_for_metrics_service,
                                                       automation_tool_id=automation_tool_id,
                                                       )
            except KeyError:
                print("KeyError - Data invalid or missing")
                # conn.send("KeyError - Data invalid or missing".encode())
                sendHTTPresponse("400","KeyError","Data invalid or missing",conn)
                conn.close()
                continue
        # __________________________________________________________________________

        # 3. UDPATE
        elif data_json['action']=='update':

            try:

                title = 'default'
                repro_steps = 'default'
                defectStatus_to_update = 'default'

                attribute_to_update = data_json['attribute_to_update']

                if "tfs_env" in data_json:
                    tfs_env = data_json["tfs_env"]
                else:
                    tfs_env="test"

                if attribute_to_update=='title':
                    title = data_json['title']

                elif attribute_to_update == 'repro_steps':
                    repro_steps = data_json['repro_steps']


                elif attribute_to_update == 'defect_status':
                    defectStatus_to_update = data_json['defectStatus_to_update']

                else:
                    print("KeyError - Value for 'attribute_to_update' is invalid. "
                              "It can only be title OR repro_steps OR defect_status")
                    sendHTTPresponse("400","KeyError","Value for 'attribute_to_update' is invalid."
                                                      "It can only be title OR repro_steps OR defect_status",conn)
                    # conn.send("KeyError - Value for 'attribute_to_update' is invalid. "
                    #           "It can only be title OR repro_steps OR defect_status".encode())
                    conn.close()
                    continue

                id=data_json['id']
                response_code,response_text = updateBug(tfs_env=tfs_env,id=id,attribute_to_update = attribute_to_update,updated_title=title,updated_repro_steps=repro_steps,defectStatus_to_update=defectStatus_to_update,
                                                        application_id_for_metrics_service=application_id_for_metrics_service,
                                                        automation_tool_id=automation_tool_id)

            except KeyError:
                print("KeyError - Data invalid or missing")
                sendHTTPresponse("400", "KeyError", "Data invalid or missing", conn)
                # conn.send("KeyError - Data invalid or missing".encode())
                conn.close()
                continue
        # ____________________________________________________________________________
        else:
            # raise KeyError
            print("KeyError - Data invalid. The value of 'action' is incorrect")
            sendHTTPresponse("400", "KeyError", "Data invalid. The value of 'action' is incorrect", conn)
            # conn.send("KeyError - Data invalid. The value of 'action' is incorrect. Action can only be 'create','search' or 'update'".encode())
            conn.close()
            continue

        print("Response code = ", response_code)
        print(response_text)
        jsonResponse = json.dumps(response_text)
        status_code = response_code.status_code
        reason = response_code.reason

        # ********Sending the response code to the client*************************************************

        response_proto = 'HTTP/1.1'.encode()
        response_status = str(status_code).encode()
        response_status_text = reason.encode()
        encoded_response_text=str(response_text).encode()

        conn.send(b'%s %s %s %s\r\n\r\n'%(response_proto, response_status,
                                    response_status_text,encoded_response_text))
        # sendLogFile(s)

        # *********Sending the response body(which is in json format) to the client************************
        conn.send(jsonResponse.encode())
        conn.close()

if __name__=='__main__':
    Main()