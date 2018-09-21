import requests
import json
from requests_ntlm import HttpNtlmAuth
import getpass
from easygui import passwordbox
import socket

# sock = socket.socket()
# host = socket.gethostname()
# port = 8000
#
# sock.bind((host,port))
# sock.listen(10)
#

# def createTFSBug(title, repro_steps, priority, severity = "3 - Medium"):
def createTFSBug(**kwargs):
  # summary, priority, serverity, worktype
  session = requests.session()
  if "title" in kwargs:title = kwargs['title']
  else:title = "Default Title"

  if "repro_steps" in kwargs:repro_steps = kwargs['repro_steps']
  else:repro_steps = "Default Repro Steps"

  if "priority" in kwargs:priority = kwargs['priority']
  else:priority = '1'

  if "severity" in kwargs:severity = kwargs['severity']
  else:severity = "3 - Medium"

  if "worktype" in kwargs:worktype = kwargs['worktype']
  else:worktype = "Maintenance/Support"

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
  url = "http://tfs.cbre.com:8080/tfs/CBRE01/DevOps-Demo/_apis/wit/workitems/$Bug?api-version=2.2"
  http_headers = {"Content-Type": "application/json-patch+json"}
  data_dump = json.dumps(data)
  # domain = input("TFS domain : ")
  # userName = input("TFS username : ")
  # password = input("TFS password : ")
  # password = passwordbox('Password: ')

  response = session.patch(url=url,data=data_dump,headers=http_headers,auth=HttpNtlmAuth('US\\gdeo','Oct2017#'))
  # print(domain+"\\"+userName+','+password)
  # auth = domain+'\\'+userName,password
  # response = session.patch(url=url,data=data_dump,headers=http_headers,auth=HttpNtlmAuth(domain,password))

  print("Response code = ",response)

  response_text = response.json()
  print(response_text)
  defect_ID = str(response_text['id'])
  # defect_summary = str(response_text['System.Title'])
  print(defect_ID)
  assert "200" in str(response), "FAIL"
  return defect_ID, response_text

if __name__=='__main__':
  createTFSBug()