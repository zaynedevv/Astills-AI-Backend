from typing import Optional

from google.api_core.client_options import ClientOptions
from google.cloud import documentai  # type: ignore
from google.oauth2 import service_account
from enum import Enum
import os
import json
from decouple import config



class DocumentType(Enum):
    ANNUAL_FACILITY_FEE = "annual_facility_fee"
    APPLICATION_FEE = "application_fee"
    APPLICATION_NUMBER = "application_number"





def process_document_sample(
    project_id: str,
    location: str,
    processor_id: str,
    image_content: bytes,
    mime_type: str,
    field_mask: Optional[str] = None,
    processor_version_id: Optional[str] = None,
) -> None:


    creds = config('CREDENTIALS_JSON')
    credentials = service_account.Credentials.from_service_account_info(creds)

    client = documentai.DocumentProcessorServiceClient(
        credentials=credentials,
        client_options=ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")
    )
    
    if processor_version_id:
        # The full resource name of the processor version, e.g.:
        # `projects/{project_id}/locations/{location}/processors/{processor_id}/processorVersions/{processor_version_id}`
        name = client.processor_version_path(
            project_id, location, processor_id, processor_version_id
        )
    else:
        # The full resource name of the processor, e.g.:
        # `projects/{project_id}/locations/{location}/processors/{processor_id}`
        name = client.processor_path(project_id, location, processor_id)


    # Load binary data
    raw_document = documentai.RawDocument(content=image_content, mime_type=mime_type)

  

    # Configure the process request
    request = documentai.ProcessRequest(
        name=name,
        raw_document=raw_document,
        field_mask=field_mask,

    )

    result = client.process_document(request=request)

    # For a full list of `Document` object attributes, reference this page:
    # https://cloud.google.com/document-ai/docs/reference/rest/v1/Document
    document = result.document

    # Read the text recognition output from the processor
    print("The document contains the following text:")
    extracted_labels = {}
    for entity in document.entities:
        entity_text = entity.mention_text
        extracted_labels[entity.type_] = entity_text
    
    return extracted_labels
        

        
       
