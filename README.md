# qEngineApi

### Библиотека для подключения к engine api qlik sense
Ссылка проекта на [pypi]
### Установка
```sh
pip install qEngineApi
```
### Используемые библиотеки
- ##### ssl
- ##### os
- ##### websocket
- ##### json
### Как работать с библиотекой

##### подключение библиотеки  
```python
from qEngineApi import QlikEngine
```
##### создание подключения.
```python
engineConnect = QlikEngine(host = "HOST" ,cert_path =  "path:/to/dir", user_directory = "DIRECTORY", user_id = "USER")
```
в параметрах подключения необходимо указать:
- **host** -  адрес вашего сервера, где развернут qlik.
- **cert_path** - абсолютный путь до папки с сертификатами. Как выгрузить сертификаты, можно почитать [тут]. После экспорта появится три файла: root.pem, client.pem, client_key.pem. Все они должны лежать по указанному пути, сохраняя оригинальные именования.
- **user_directory** - директория вашего пользователя (домент учетной записи)
- **user_id** - ваш пользователь.  

**!!!Важно -на пользователя под которым вы подключаетесь распространяются все ограничения, как на доступ к документам/действиям, так и на доступ к данным внутри приложений в случае если включена section access. То есть доступ в engine api будет полностью соответствовать доступу в hub указанного пользователя. Указать можно любого пользователя под которым вы хотите работать.**

после создания подключения можно проверить статус подключения в параметре **engineConnect.sessionCreated**, Все последующие действия рекомендуется выполнять только если он **true**. После окончания работы с engine api необходимо закрыть соединение вызвав **del engineConnect**
```python
sessionCreated = engineConnect.sessionCreated
if sessionCreated:
    //ваш код
    ...
    del engineConnect #убиваем сессию после того как завершили все действия
```
##### Описание методов 
##### getDocList(self) - возвращает список документов доступных пользователю
```python
documents = engineConnect.getDocList()
print(json.dumps(documents))
```
##### openDoc(self, docId) - открывает подключение к конкретному приложению
```python
doc = engineConnect.openDoc('2ec2ed23-a62f-4c9d-b501-1b3a5fac192c')
docHandle = doc['result']['qReturn']['qHandle']
print(json.dumps(doc))
```
в качестве аргумента необходимо передать id приложения qlik sense. Найти его можно либо в ссылке, открыв его в хабе, либо посмотреть в qmc, либо воспользоваться методов getDocList().
**!!!Для дальнейшей работы с открытым документом, необходимо запомнить handle этого вызова**

##### applyBookmark(self,handle,bookmarkId) - применяет указанную закладку к документу.
```python
bookmark = engineConnect.applyBookmark(docHandle,'c37ff895-d611-44b8-95b3-d6ddaa35f9a9')
print(json.dumps(bookmark))
```
в качестве аргумента необходимо передать handle, который вернулся в методе открытия документа И id закладки.

##### getObject(self,handle,objectId) - обратиться к конкретному объекту в приложении.
```python
object = engineConnect.getObject(docHandle,'PegSyT')
objectHandle = object['result']['qReturn']['qHandle']
```
В качестве аргумента необходимо передать handle, который вернулся в методе открытия документа и id объекта.
**!!!Для дальнейшей работы с объектом необходимо запомнить handle, вернувшийся в ответе.**

##### exportData(self,handle,exportFormat) - метод для экспорта данных объекта, вернет json содержащий ссылку на скачивание файла.
```python
export = engineConnect.exportData(objectHandle,'OOXML')
downloadUrl = 'http://'+ host  + export['result']['qUrl']
print(downloadUrl)
```
В качестве аргументов необходимо указать handle, который вернулся в методе обращения к объекту и формат экспорта.
Подробнее о форматах можно почитать в [справке qlik]

##### getSheetsObject(self,handle,exportFormat) - вернет массив всех листов приложения со всеми их объектами.
```python
sheetsObject= engineConnect.getSheetsObject(docHandle)
sheets = sheetsObject['result']['qLayout']['qAppObjectList']['qItems']
for sheet in sheets:
     sheetObjects = sheet['qData']['cells']
      for object in sheetObjects:
         print(object)
```
В качестве аргумента необходимо передать handle, который вернулся в методе обращения к документу.

##### sendRequest(self,request) - произвольный запрос к engine api. Вернет json с ответом.
```python
request = {
    "handle": docHandle,
	"method": "ApplyBookmark",
	"params": {
	        "qId": "c37ff895-d611-44b8-95b3-d6ddaa35f9a9"
	}
}

result = engineConnect.sendRequest(request)
print(json.dumps(result))
```

В качестве аргумента можно передать любой произвольный запрос.
**Поэкспериментировать с запросами к engine api можно в [dev-hub->engine api explorer]. Попасть в него можно через hub->троеточие в верхнем правом углу страницы-> Dev-hub**

[//]: #
[тут]: <https://help.qlik.com/en-US/sense-admin/August2022/Subsystems/DeployAdministerQSE/Content/Sense_DeployAdminister/QSEoW/Administer_QSEoW/Managing_QSEoW/export-certificates.htm>
[pypi]: <https://pypi.org/project/qEngineApi/>
[справке qlik]: <https://help.qlik.com/en-US/sense-developer/August2022/Subsystems/EngineJSONAPI/Content/service-genericobject-exportdata.htm>
[dev-hub->engine api explorer]: <https://help.qlik.com/en-US/sense-developer/May2022/Subsystems/Dev-Hub/Content/Sense_Dev-Hub/EngineApiExplorer/engine-api-explorer.htm>
