import ssl
import os
from websocket import create_connection
import json
from pathlib import Path

def idCounter(self):
    self.id +=1 
    return self.id

class QlikEngine():
    #Initialize websocket
    def __init__(self,host,cert_path,user_directory,user_id):
        self.host = host
        self.cert_path = cert_path
        self.user_directory = user_directory
        self.user_id = user_id
        self.id = 0
        socketUrl = f"wss://{self.host}:4747/app/"
        cert = {
                "cert_reqs":ssl.CERT_NONE,
                'ca_certs':os.path.join(self.cert_path,'root.pem'),
                'certfile':os.path.join(self.cert_path,'client.pem'),
                'keyfile':os.path.join(self.cert_path,'client_key.pem')
        }

        requestHeader = {
                'X-Qlik-User':f'UserDirectory={self.user_directory};'
                              f'UserId={self.user_id}'
        }

        try:
            self.ws = create_connection(socketUrl, sslopt = cert, header = requestHeader)
            self.result = self.ws.recv()
            result = json.loads(self.result)
            self.sessionState = result.get("params").get("qSessionState")
            if  self.sessionState == 'SESSION_CREATED':
                self.sessionCreated = True
            else:
                self.sessionCreated = False
        except Exception as e:
            self.result = json.dumps({
                "params": {"qSessionState":"error"}
            })
            self.sessionCreated = False 
            print("error while websocket opening")
            print(e)


    def getDocList(self):
        self.ws.send(json.dumps({
            "id": idCounter(self),
	        "handle": -1,
            "method": "GetDocList",
            "params": [],
            "outKey": -1
        }))

        result = self.ws.recv()

        data = json.loads(result)
        documentsList = data["result"]

        documents = []

        for doc in documentsList.get("qDocList"):
            documentMeta = doc.get("qMeta")
            if documentMeta.get("published"):
                stream = documentMeta.get("stream").get("name")
                streamId = documentMeta.get("stream").get("id")
                isPublished = True
            else:
                stream = "None"
                streamId = "None"
                isPublished = False

            document = {
                "docId": doc.get("qDocId"),
                "docName": doc.get("qDocName"),
                "isPublished": isPublished,
                "qvfSize": doc.get("qFileSize"),
                "createdDate":documentMeta.get("createdDate"),
                "modifiedDate":documentMeta.get("modifiedDate"),
                "lastReloadTime":documentMeta.get("qLastReloadTime"),
                "publishTime":documentMeta.get("publishTime"),
                "stream":stream,
                "streamId":streamId
            }    
            documents.append(document)

        return documents

    def openDoc(self, docId):
        self.ws.send(json.dumps({
            "method": "OpenDoc",
	        "handle": -1,
	        "params": [
                docId
	        ],
	        "outKey": -1,
            "id": idCounter(self)
        }))

        result = self.ws.recv()
        data = json.loads(result)

        return data

    def applyBookmark(self,handle,bookmarkId):
        self.ws.send(json.dumps(
            {
                "id":idCounter(self),
	            "handle": handle,
	            "method": "ApplyBookmark",
	            "params": {
		            "qId": bookmarkId
	            }
            }
        ))

        result = self.ws.recv()
        data = json.loads(result)

        return data

    def getSheetsObject(self,handle): 
        self.ws.send(json.dumps({
            "method": "CreateSessionObject",
            "handle": handle,
            "id":idCounter(self),
            "params": [
                {
                    "qInfo": {
                        "qType": "SheetList"
                    },
                    "qAppObjectListDef": {
                        "qType": "sheet",
                        "qData": {
                            "title": "/qMetaDef/title",
                            "description": "/qMetaDef/description",
                            "thumbnail": "/thumbnail",
                            "cells": "/cells",
                            "rank": "/rank",
                            "columns": "/columns",
                            "rows": "/rows"
                        }
                    }
                }
            ],
            "outKey": -1
        }))

        result = self.ws.recv()
        sheetObjects = json.loads(result)
        sheetsHandle = sheetObjects['result']['qReturn']['qHandle']

        self.ws.send(json.dumps(
            {
            "id":idCounter(self),
            "method": "GetLayout",
	        "handle": sheetsHandle,
	        "params": [],
	        "outKey": -1
            }
        ))

        result = self.ws.recv()
        data = json.loads(result)

        return data


    def getLayout(self,handle):
        self.ws.send(json.dumps(
            {
            "id":idCounter(self),
            "method": "GetLayout",
	        "handle": handle,
	        "params": [],
	        "outKey": -1
            }
        ))

        result = self.ws.recv()
        data = json.loads(result)

        return data



    def getObject(self,handle,objectId):
        self.ws.send(json.dumps(
            {
                "id":idCounter(self),
                "handle": handle,
                "method": "GetObject",
                "params": {
                    "qId": objectId
                }
            }
        ))

        result = self.ws.recv()
        data = json.loads(result)

        return data

    def exportData(self,handle,exportFormat):
        self.ws.send(json.dumps(
            {
                "id":idCounter(self),
                "jsonrpc": "2.0",
                "method": "ExportData",
                "handle": handle,
                "params": [ exportFormat ],
                "outKey": -1
            }
        ))

        result = self.ws.recv()
        data = json.loads(result)

        return data

    def sendRequest(self,request):
        self.ws.send(json.dumps(request))

        result = self.ws.recv()
        data = json.loads(result)

        return data

    def showVariables(self, handle, showreserve = False, showConfig = False):
        variableListRequest = {
                                "method": "CreateSessionObject",
                                "handle": handle,
                                "params": [
                                    {
                                        "qInfo": {
                                        "qType": "VariableList"
                                    },
                                        "qVariableListDef": {
                                            "qType": "variable",
                                            "qShowReserved": showreserve,
                                            "qShowConfig": showConfig,
                                            "qData": {
                                                "tags": "/tags"
                                            }
                                        }
                                    }
                                ],
                                "outKey": -1,
                                "id": idCounter(self)
                            }

        self.ws.send(json.dumps(variableListRequest))
        result = self.ws.recv()
        variableList = json.loads(result)
        listHandle = variableList['result']['qReturn']['qHandle']

        getLayoutRequest =  {
                                "method": "GetLayout",
                                "handle": listHandle,
                                "params": [],
                                "outKey": -1,
                                "id": idCounter(self)
                            }

        self.ws.send(json.dumps(getLayoutRequest))
        result = self.ws.recv()
        variables = json.loads(result)
        variables = variables['result']['qLayout']['qVariableList']['qItems']

        print ("{:<15} {:<18} {:<40} {:<30} {:<20}".format('isScriptCreated','qIncludeInBookmark','id','name','definition'))
        for variable in variables:
            self.ws.send(json.dumps(
                {
                    "handle": handle,
                    "id":idCounter(self),
                    "method": "GetVariableByName",
                    "params": {
		                "qName": variable['qName']
	                }
                }
            ))

            result = self.ws.recv()
            data = json.loads(result)
            variableHandle = data['result']['qReturn']['qHandle']
            self.ws.send(json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "GetProperties",
                    "handle": variableHandle,
                    "id":idCounter(self),
                    "params": [],
                    "outKey": -1,
                    "return_empty": True,
                    "delta": False
                }
            ))
            result = self.ws.recv()
            data = json.loads(result)
            variableParams = data['result']
            
            if(variableParams['qProp']['qIncludeInBookmark']):
                qIncludeInBookmark = 'true'
            else:
                qIncludeInBookmark = 'false'

            if "qIsScriptCreated" in variable:
                isScriptCreated = 'true'
            else: 
                isScriptCreated = 'false'

            if "qDefinition" in variable:
                definition = variable['qDefinition']
            else:
                definition =  'without definition'
            
            print ("{:<15} {:<18} {:<40} {:<30} {:<20}".format(isScriptCreated,qIncludeInBookmark, variable['qInfo']['qId'],variable['qName'],definition))

        return variables



    def includeVariableInBookmark(self,handle,include=True,variable="ALL"):
        def setVariableParams(self,handle,variableName,include):
            self.ws.send(json.dumps(
                {
                    "handle": handle,
                    "id":idCounter(self),
                    "method": "GetVariableByName",
                    "params": {
		                "qName": variableName
	                }
                }
            ))

            result = self.ws.recv()
            data = json.loads(result)
            variableHandle = data['result']['qReturn']['qHandle']
            
            self.ws.send(json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "GetProperties",
                    "handle": variableHandle,
                    "id":idCounter(self),
                    "params": [],
                    "outKey": -1,
                    "return_empty": True,
                    "delta": False
                }
            ))

            result = self.ws.recv()
            data = json.loads(result)
            variableParams = data['result']
            variableParams['qProp']['qIncludeInBookmark'] = include

            request = json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "SetProperties",
                    "handle": variableHandle,
                    "params": variableParams,
                    "outKey": -1,
                    "id":idCounter(self)
                }
            )

            self.ws.send(request)

            result = self.ws.recv()
            data = json.loads(result)

            return data

        if variable != "ALL":
            final =  setVariableParams(self,handle,variable,include)
            return final
        else:
            variableListRequest = {
                                "method": "CreateSessionObject",
                                "handle": handle,
                                "params": [
                                    {
                                        "qInfo": {
                                        "qType": "VariableList"
                                    },
                                        "qVariableListDef": {
                                            "qType": "variable",
                                            "qShowReserved": False,
                                            "qShowConfig": False,
                                            "qData": {
                                                "tags": "/tags"
                                            }
                                        }
                                    }
                                ],
                                "outKey": -1,
                                "id": idCounter(self)
                            }

            self.ws.send(json.dumps(variableListRequest))
            result = self.ws.recv()
            variableList = json.loads(result)
            listHandle = variableList['result']['qReturn']['qHandle']
            
            getLayoutRequest =  {
                                    "method": "GetLayout",
                                    "handle": listHandle,
                                    "params": [],
                                    "outKey": -1,
                                    "id": idCounter(self)
                                }

            self.ws.send(json.dumps(getLayoutRequest))
            result = self.ws.recv()
            variables = json.loads(result)
            variables = variables['result']['qLayout']['qVariableList']['qItems']

            for variable in variables:
                setVariableParams(self,handle,variable['qName'],include)
            print('finished')
            return 'finished'


    def exportApp(self,dir, onlyPublished=True, streamId='ALL',appId="ALL",createFolderStructure = False, idInNaming = True):
        def request(docId,file):
            exportApp = {
                "handle": -1,
                "method": "ExportApp",
                "params": {
                    "qTargetPath": file,
                    "qSrcAppId": doc["docId"],
                    "qIds": [
                       
                    ],
                    "qNoData": False
                }
            }
            self.ws.send(json.dumps(exportApp))
            result = self.ws.recv()
            status = json.loads(result)
            status = status['result']['qSuccess']
            if status:
                printStatus = 'Success'
            else:
                printStatus = 'Failed'
            print(f'{doc["docName"]} {printStatus}')
            return status

        docList = self.getDocList()
        successCount = 0
        failedCount = 0
        if appId == "ALL":
            for doc in docList:
                if createFolderStructure:
                    if idInNaming:
                        filePath = f'{doc["stream"]} ({doc["streamId"]})'
                    else:
                        filePath = doc["stream"]
                    exportdir= os.path.join(dir,filePath)
                    if not os.path.isdir(exportdir):
                         Path(exportdir).mkdir(parents=True, exist_ok=True)
                else:
                    exportdir = dir

                if idInNaming:
                    fileName = f'{doc["docName"]} ({doc["docId"]}).qvf'
                else:
                    fileName = f'{doc["docName"]}.qvf' 
                file = os.path.join(exportdir,fileName)
                if (onlyPublished == True and doc["isPublished"] == True) or onlyPublished == False:
                    if streamId == 'ALL' or streamId == doc["streamId"]:
                        status = request(doc["docId"],file)
                
                        if status:
                            successCount += 1
                        else:
                            failedCount += 1
        else:
             for doc in docList:
                 if appId == doc["docId"]:
                    if idInNaming:
                        fileName = f'{doc["docName"]} ({doc["docId"]}).qvf'
                    else:
                        fileName = f'{doc["docName"]}.qvf'
                    file = os.path.join(dir,fileName)
                    status = request(doc["docId"],file)
                    if status:
                        successCount += 1
                    else:
                        failedCount += 1
           
        print(f'Export finished with {successCount} success and {failedCount} failed')

    #Object destroyer
    def __del__(self):
        if self.sessionCreated:
            self.ws.close()
