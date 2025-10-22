

import requests

def populateFile(templatePath, data, outputName):

    json = {
    "outputName": outputName,
    "templateName": templatePath,
    "data": data,
    "outputFormat": "pdf;docx",
    "accessKey": "MjE1MWNhZDQtZmQ5YS00MTNjLWE4ODMtZjNiZmVhNDVkODkyOjY4NTM2MTc0OTk"
    }

    headers = {'content-type': 'application/json'}

    response = requests.post('https://au1.dws4.docmosis.com/api/render', headers = headers, json=json)
    if response.status_code != 200:
        print(response.content)
    return response.content


def getTemplateStucture(path):

    url = "https://au1.dws4.docmosis.com/api/getSampleData"

    payload = {
        'templateName': path,
        'accessKey': 'MjE1MWNhZDQtZmQ5YS00MTNjLWE4ODMtZjNiZmVhNDVkODkyOjY4NTM2MTc0OTk'
    }
    files=[

    ]
    headers = {}

    response = requests.request("POST", url, headers=headers, data=payload, files=files)

    return response.json()




