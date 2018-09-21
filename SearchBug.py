import requests
import json
from requests_ntlm import HttpNtlmAuth
import base64

TFS_username = 'TND\\TND_VSTO_build_test'
TFS_password = '&a3WAZQjVTfh5_hY'

def searchBug(project_name_in_tfs, defect_title_to_search):
    session = requests.session()
    data = {"query": "Select [System.Id] From WorkItems "
                      "Where [System.WorkItemType] = 'Bug' "
                      "AND [System.TeamProject] = '"+project_name_in_tfs+"'"
                      "AND [System.Title] = '"+defect_title_to_search+"'"
                      "AND [State] <> 'Closed' "
                      "AND [State] <> 'Removed' "
                      "order by [Microsoft.VSTS.Common.Priority] asc, [System.CreatedDate] desc"}
    url = "http://tfs.cbre.com:8080/tfs/CBRE01/_apis/wit/wiql?api-version=1.0"

    http_headers = {"Content-Type": "application/json"}
    data_dump = json.dumps(data)

    response = session.post(url=url, data=data_dump, headers=http_headers,
                             auth=HttpNtlmAuth(TFS_username, TFS_password))

    print("Response code = ", response)

    response_text = response.json()
    print(response_text)
    assert "200" in str(response), "FAIL"


if __name__ == '__main__':
    searchBug("DevOps-Demo","Some Bug")