
import requests
from requests_ntlm import HttpNtlmAuth
import json
import base64



TFS_username = 'TND\\TND_VSTO_build_test'
TFS_password = '&a3WAZQjVTfh5_hY'

def searchTFSBugWithID():


    # tpc = TfsTeamProjectCollection.Uri("http://server:8080/tfs/DefaultCollection"))
    # workItemStore = tpc.GetService(typeof(WorkItemStore))
    #
    # queryResults = workItemStore.Query("Select [State], [Title] "
    # "From WorkItems " +
    # "Where [Work Item Type] = 'Bug' " +
    # "Order By [State] Asc, [Changed Date] Desc")
    #
    # queryRoot = workItemStore.Projects[0].QueryHierarchy
    #
    # folder = (QueryFolder)queryRoot["Shared Queries"]
    #
    # query = (QueryDefinition)folder["Active Bugs"]
    # queryResults = workItemStore.Query(query.QueryText);
    #
    session = requests.session()
    decoded_password=base64.decodebytes(b'T2N0MjAxNyM=')
    decoded_password_string=decoded_password.decode('utf-8')

    # url = "http://tfs.cbre.com:8080/tfs/CBRE01/DevOps-Demo/_apis/wit/workitems?ids=216300&api-version=2.2"



    # This one works*************

    # 1. Search 1 ID
    # url = "http://tfs.cbre.com:8080/tfs/CBRE01/_apis/wit/workitems/219992?api-version=1.0"

    # 2. Search multiple IDs
    # url = "http://tfs.cbre.com:8080/tfs/CBRE01/_apis/wit/workitems?ids=219991,219992&api-version=1.0"

    # 3. Search by date
    # url = "http://tfs.cbre.com:8080/tfs/CBRE01/_apis/wit/workitems?ids=219991,219992&fields=System.Id,System.Title,System.WorkItemType,Microsoft.VSTS.Scheduling.RemainingWork&asOf=2017-12-13&api-version=1.0"

    # 4. Search by fields
    url = "http://tfs.cbre.com:8080/tfs/CBRE01/_apis/wit/workitems?ids=219991&fields=System.Title&api-version=1.0"

    # ************************************




    # http_headers = {"Content-Type": "application/json-patch+json"}
    # url = "http://tfs.cbre.com:8080/tfs/CBRE01/DevOps-Demo/_workitems?ids=209857&fields=System.Title&api-version=2.2"
    headers = {"User-Agent": "Request"}

    # Gives 404 Page not found error
    # url = "http://tfs.cbre.com:8080/tfs/CBRE01/DevOps-Demo/_apis/wit/workitems/209857?&api-version=2.2"


    response = session.get(url=url,headers=headers,auth=HttpNtlmAuth(TFS_username,TFS_password))

    print("Response code = ",response)

    response_text = response.text
    # json_text = json.dumps(response_text)
    # json_loads = json.loads(json_text)
    # print("JSON = ",json_loads)
    print(response_text)
    # defect_ID = str(response_text['id'])
    # print(defect_ID)
    assert "200" in str(response), "FAIL"
    # return defect_ID, response_text

if __name__=='__main__':
    searchTFSBugWithID()