import pyodbc
# import tfserver
from tfs import TFSAPI
from tfs import TFSQuery

TFSServer = "tfs.cbre.com"
TFS_username = 'TND\\TND_VSTO_build_test'
TFS_password = '&a3WAZQjVTfh5_hY'


# database = ''
# # cnxn = pyodbc.connect(DRIVER='{ODBC Driver 13 for SQL Server}',SERVER=TFSServer, DATABASE=database,UID=TFS_username,PWD=TFS_password)
# # conn = pyodbc.connect('DRIVER={SQL Server};SERVER='+TFSServer+';DATABASE='+database+';UID='+TFS_username+';PWD='+ TFS_password)
# conn = pyodbc.connect('DRIVER={SQL Server};SERVER=USCDCPDBTFS02.US.CBRE.NET;DSN=MSSQL-PYTHON')
# cursor = conn.cursor()


# service = tfserver.TfsTeamProjectCollection(Uri("http://tfs.cbre.com:8080/tfs/CBRE01")).GetService<WorkItemStore>()
# client = TFSAPI("http://tfs.cbre.com:8080/tfs/CBRE01", user="US\\gdeo",password="Oct2017#")


# workitem = client.get_workitem(220327)

# query = TFSQuery(uri="http://tfs.cbre.com:8080/tfs/CBRE01")
# # query.get("title")
#
# query.column_names()


# Set path to ProjectName in project parameter
client = TFSAPI("http://tfs.cbre.com:8080/tfs/CBRE01",project="DevOps-Demo",user=TFS_username, password=TFS_password)

# Run custom query
### NOTE: Fields in SELECT really ignored, wiql return Work Items with all fields
query = "SELECT    " \
        "[System.Id],    " \
        "[System.WorkItemType],    " \
        "[System.Title],    " \
        "[System.ChangedDate]" \
        "FROM workitems" \
        "WHERE" \
        "    [System.WorkItemType] = 'Bug'" \
        "ORDER BY [System.ChangedDate]"

wiql = client.run_wiql(query)

# Get founded Work Item ids
ids = wiql.workitem_ids
print("Found WI with ids={}".format(",".join(ids)))

# Get RAW query data - python dict
raw = wiql.result

# Get all found workitems
workitems = wiql.workitems
print(workitems[0]['Title'])