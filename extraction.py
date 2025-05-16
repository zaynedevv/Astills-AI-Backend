from typing import Optional

from google.api_core.client_options import ClientOptions
from google.cloud import documentai  # type: ignore
from google.oauth2 import service_account
from enum import Enum
import requests
import time
import os


model_url = "https://zayne.cognitiveservices.azure.com/formrecognizer/documentModels/Finalv1:analyze?api-version=2023-07-31"


key = os.environ.get("AZURE_KEY")

headers = {
    "Ocp-Apim-Subscription-Key": key,
    "Content-Type": "application/pdf"
}


class DocumentType(Enum):
    ANNUAL_FACILITY_FEE = "annual_facility_fee"
    APPLICATION_FEE = "application_fee"
    APPLICATION_NUMBER = "application_number"





def process_document_sample(
    image_content: bytes,
) -> None:
    
    
    response = requests.post(model_url, headers=headers, data=image_content)

    # The response includes an operation-location for polling
    operation_url = response.headers["Operation-Location"]

    # Poll the result
    while True:
        result = requests.get(operation_url, headers={"Ocp-Apim-Subscription-Key": key})
        result_json = result.json()
        status = result_json["status"]
        if status in ["succeeded", "failed"]:
            break
        time.sleep(2)


    documents = result_json.get("analyzeResult", {}).get("documents", [])
    final_fields = {}

    for doc in documents:
        fields = doc.get("fields", {})
        for field_name, field_data in fields.items():
            value = (
                field_data.get("valueString") or
                field_data.get("valueNumber") or
                field_data.get("valueDate") or
                field_data.get("valueTime") or
                field_data.get("valueInteger") or
                field_data.get("valuePhoneNumber") or
                field_data.get("valueSelectionMark") or
                field_data.get("valueCountryRegion") or
                field_data.get("valueArray") or
                field_data.get("valueObject") or
                field_data.get("content")
            )
            final_fields[field_name] = value

    return final_fields


            
        
