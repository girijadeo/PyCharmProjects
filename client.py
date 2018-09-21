import socket
import json
import requests

def Main():
    host = 'localhost'
    port = 8000

    s = socket.socket()
    s.connect((host, port))

    # message = "Hi"
    # while message.lower()!='exit':
    #     message=input("->")
    #     s.send(message)
    # defect_ID = s.recv(1024)
    # defect_summary = s.recv(1024)
    data = {"title": "test_1127",
            "repro_steps":"----repro steps from client 1127---",
            "priority":"2",
            "project_name_in_TFS":"DevOps-Demo"}
    # s.send(json.loads(data))
    data_dump = json.dumps(data)

    # s.send(data_dump)
    # title = data['title']
    s.send(data_dump.encode())
    response_text = s.recv(10*1024)
    # print("Receieved from server - Defect ID : "+str(defect_ID.decode()) )
    print("Receieved from server - Defect summary : " ,response_text.decode())
    # print("Defect summary - "+str(defect_summary))
        # message = input("->")

    s.close()


                    #
                    # url = "http://localhost:8000"
                    # http_headers = {"Content-Type": "application/json"}
                    # session = requests.session()
                    # response = session.post(url=url, data=data_dump, headers=http_headers)
                    #
                    # print("Response code = ", response)
                    #
                    # response_text = response.json()
                    # print(response_text)
                    # defect_ID = str(response_text['id'])
                    # # defect_summary = str(response_text['System.Title'])
                    # print(defect_ID)
                    # assert "200" in str(response), "FAIL"
                    # return defect_ID, response_text

if __name__=='__main__':
    Main()