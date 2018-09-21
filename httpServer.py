import http.server
import socketserver
import CreateBug

# def createTFSBug(project_name_in_TFS, **kwargs):
#     session = requests.session()
#     if "title" in kwargs:
#         title = kwargs['title']
#     else:
#         title = "Default Title"
#
#     if "repro_steps" in kwargs:
#         repro_steps = kwargs['repro_steps']
#     else:
#         repro_steps = "Default Repro Steps"
#
#     if "priority" in kwargs:
#         priority = kwargs['priority']
#     else:
#         priority = '1'
#
#     if "severity" in kwargs:
#         severity = kwargs['severity']
#     else:
#         severity = "3 - Medium"
#
#     if "worktype" in kwargs:
#         worktype = kwargs['worktype']
#     else:
#         worktype = "Maintenance/Support"
#
#     data = [
#
#         {
#             "op": "add",
#             "path": "/fields/System.Title",
#             "value": title
#         },
#         {
#             "op": "add",
#             "path": "/fields/Microsoft.VSTS.TCM.ReproSteps",
#             "value": repro_steps
#         },
#         {
#             "op": "add",
#             "path": "/fields/Microsoft.VSTS.Common.Priority",
#             "value": priority
#         },
#         {
#             "op": "add",
#             "path": "/fields/Microsoft.VSTS.Common.Severity",
#             "value": severity
#         },
#         {
#             "op": "add",
#             "path": "/fields/CBRE.WorkType",
#             "value": worktype
#         }
#     ]
#
#     project_name_in_TFS = project_name_in_TFS
#     url = "http://tfs.cbre.com:8080/tfs/CBRE01/"+project_name_in_TFS+"/_apis/wit/workitems/$Bug?api-version=2.2"
#
#     http_headers = {"Content-Type": "application/json-patch+json"}
#     data_dump = json.dumps(data)
#
#     decoded_password = base64.decodebytes(b'T2N0MjAxNyM=')
#     decoded_password_string = decoded_password.decode('utf-8')
#
#     response = session.patch(url=url, data=data_dump, headers=http_headers,
#                              auth=HttpNtlmAuth('US\\gdeo', decoded_password_string))
#
#     print("Response code = ", response)
#
#     response_text = response.json()
#     print(response_text)
#     defect_ID = str(response_text['id'])
#     print(defect_ID)
#     assert "200" in str(response), "FAIL"
#     return defect_ID, response_text

PORT = 33334
HOST = "127.0.0.1"

Handler = http.server.SimpleHTTPRequestHandler

httpd = socketserver.TCPServer((HOST, PORT),Handler)

print ("serving at port", HOST, PORT)

httpd.serve_forever()


