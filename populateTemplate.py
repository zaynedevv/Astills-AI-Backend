

import requests

def populateFile(templatePath, data, outputName):

    json = {
    "outputName": outputName,
    "templateName": templatePath,
    "data": data,
    "outputFormat": "pdf;docx",
    "accessKey": "YWU4Mjk4NDMtNmExNy00NzUwLWJjMDQtOTNmYTQyNzY5MGM5Ojk4NjkwNjIzNjQ"
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
        'accessKey': 'NTkxZjQ3ZjktODc4MC00MTBhLWIyZjktMzlkYmM0ZTIwZTAxOjU1MDIxMTY0Nw'
    }
    files=[

    ]
    headers = {}

    response = requests.request("POST", url, headers=headers, data=payload, files=files)

    return response.json()


