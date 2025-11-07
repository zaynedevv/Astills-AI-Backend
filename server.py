from fastapi import FastAPI, File, UploadFile, Query, Body
from fastapi.responses import JSONResponse
from extraction import process_document_sample
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from populateTemplate import populateFile, getTemplateStucture
from constants import DOCMOSIS_DIRECTORIES
from fastapi.responses import StreamingResponse

from helpers import getBorrowerChecklist, structureJson, getTemplates, get_templates_async, generate_all_pdfs, populate_file_async

import io
import zipfile
import os


origins = ["*"]

app = FastAPI()



app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # List of allowed origins, or ["*"] for all
    allow_credentials=True,
    allow_methods=["*"],              # Allow all HTTP methods
    allow_headers=["*"],              # Allow all headers
)



'''
/documents/parse
@description This endpoint is used to parse a document using Google Document AI.
@params file is the file to be parsed
@params document_type is the type of document to be parsed
@params starting_page is the page number to start parsing from
@params ending_page is the page number to end parsing at
@returns JSON response with the parsed document

'''

@app.post("/documents/parse")
async def parse_doc(file: UploadFile = File(...), 
                    document_type: str = Query(...),
                    lender: str = Query(...)):
    
    if file.content_type != "application/pdf":
        return JSONResponse(status_code=400, content={"error": "File must be a PDF."})
    
    # Read the file content
    file_content = await file.read()

    try:
        result = process_document_sample(
            image_content=file_content,
            lender=lender
        )

        return JSONResponse(status_code=200, content={"message": "success", "document_type": document_type, "result": result})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    

"""
POST /documents/populate

Populates document templates based on provided selectors and matter information.

- Query parameters: lender, matter_type, transaction_type, state, loan_type
- Body: matter_info (dictionary with relevant data)

Automatically fills template structures and calls the Docmosis API to generate populated documents.

Returns: Populated files.
"""


@app.post('/documents/populate')
async def populate(
    lender: str = Query(...),
    matter_type: str = Query(...),
    transaction_type: str = Query(...),
    state: str = Query(...),
    loan_type: str = Query(...),
    matter_info: dict = Body(...),  # MatterInfo is the Pydantic model
):
    
    

    # print(str(matter_info))

    matter_info = matter_info['matter_info']
    
    #Get Directories Associated with Matter Type
    directoryIndex = matter_type + '/' + transaction_type + '/' + lender + '/'
    matterDirectories = DOCMOSIS_DIRECTORIES.get(directoryIndex)

    if not matterDirectories: return JSONResponse(status_code=404, content={"error": "Cannot Find Document Directory"})

    matterFiles = []

    #Borrower Checklist Logic
    borrowerDirectory = getBorrowerChecklist(state, transaction_type, matterDirectories)

    matterFiles.append(borrowerDirectory)

    loanAgreement = matterDirectories['Loan-Agreement'][loan_type]

    matterFiles.append(loanAgreement)

    stateSpecificFiles = matterDirectories.get(f'{state}-Specific', None)

    if (stateSpecificFiles):
        matterFiles.extend(stateSpecificFiles)


    matterFiles.extend(matterDirectories.get('Standard', []))

    # templates = getTemplates(matterFiles)
    templates = await get_templates_async(matterFiles, concurrency=93)
    
    data = structureJson(matter_info, templates)

    print(data)

    files = await generate_all_pdfs(data)

    #Individual Legal Advice Certificate Logic
    if lender == "BC" and transaction_type == "Purchase":
        ILAName = "SMSF/Purchase/BC/17. Individual Legal Advice Certificate.docx"
        template = await get_templates_async([ILAName])
        print(template);
    
        for director in matter_info["directors"]:
            ILAData = {}
            for key in template[ILAName]:
                if data.get(key):  # safer than data[key]
                    ILAData[key] = data[key]
                else:
                    ILAData[key] = director.get(key)
            print(ILAData)
    
            file = await populate_file_async(
                ILAName,
                ILAData,
                f'17. Individual Legal Advice Certificate - {director["GUARANTORNAME"]}'
            )
            files.append((f'17. Individual Legal Advice Certificate - {director["GUARANTORNAME"]}.zip', file))


    #Guarantor Legal Advice Warranty
    if lender == "BC" and transaction_type == "Refi":
        ILAName = "SMSF/Refi/BC/12. Guarantor Legal Advice Warranty.docx"
        template = await get_templates_async([ILAName])
        print(template);
    
        for director in matter_info["directors"]:
            ILAData = {}
            for key in template[ILAName]:
                if data.get(key):  # safer than data[key]
                    ILAData[key] = data[key]
                else:
                    ILAData[key] = director.get(key)
            print(ILAData)
    
            file = await populate_file_async(
                ILAName,
                ILAData,
                f'12. Guarantor Legal Advice Warranty - {director["GUARANTORNAME"]}'
            )
            files.append((f'12. Guarantor Legal Advice Warranty - {director["GUARANTORNAME"]}.zip', file))

    if lender == "Source" and transaction_type == "Purchase" and matter_info["property_state"] != "NSW":
        ILAName = "SMSF/Purchase/Source/12. Solicitors Certificate Guarantor.docx"
        template = await get_templates_async([ILAName])
        print(template);
    
        for director in matter_info["directors"]:
            ILAData = {}
            for key in template[ILAName]:
                if data.get(key):  # safer than data[key]
                    ILAData[key] = data[key]
                else:
                    ILAData[key] = director.get(key)
            print(ILAData)
    
            file = await populate_file_async(
                ILAName,
                ILAData,
                f'12. Solicitors Certificate Guarantor - {director["GUARANTORNAME"]}'
            )
            files.append((f'12. Solicitors Certificate Guarantor - {director["GUARANTORNAME"]}.zip', file))

    if lender == "Source" and transaction_type == "Purchase" and matter_info["property_state"] == "NSW":
        ILAName = "SMSF/Purchase/Source/12. Legal Advice Declaration - NSW.docx"
        template = await get_templates_async([ILAName])
        print(template);
    
        for director in matter_info["directors"]:
            ILAData = {}
            for key in template[ILAName]:
                if data.get(key):  # safer than data[key]
                    ILAData[key] = data[key]
                else:
                    ILAData[key] = director.get(key)
            print(ILAData)
    
            file = await populate_file_async(
                ILAName,
                ILAData,
                f'12. Legal Advice Declaration - NSW - {director["GUARANTORNAME"]}'
            )
            files.append((f'12. Legal Advice Declaration - NSW - {director["GUARANTORNAME"]}.zip', file))


    

        
    # zip_buffer = io.BytesIO()
    # with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
    #     for filename, content in files:
    #         zipf.writestr(filename, content)

    # zip_buffer.seek(0)
    # return StreamingResponse(
    #     zip_buffer,
    #     media_type="application/zip",
    #     headers={"Content-Disposition": "attachment; filename=documents.zip"}
    # )
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as final_zip:
        for outer_filename, outer_content in files:
            outer_name = os.path.splitext(outer_filename)[0]  # remove .zip extension
            inner_zip_bytes = io.BytesIO(outer_content)

            try:
                with zipfile.ZipFile(inner_zip_bytes, "r") as inner_zip:
                    for inner_name in inner_zip.namelist():
                        if inner_name.endswith("/"):
                            continue  # skip directories

                        base_inner_name = os.path.basename(inner_name)

                        if inner_name.lower().endswith(".pdf"):
                            final_zip.writestr(
                                f"pdfs/{outer_name}/{base_inner_name}",
                                inner_zip.read(inner_name)
                            )
                        elif inner_name.lower().endswith(".docx"):
                            final_zip.writestr(
                                f"docs/{outer_name}/{base_inner_name}",
                                inner_zip.read(inner_name)
                            )
                        else:
                            final_zip.writestr(
                                f"others/{outer_name}/{base_inner_name}",
                                inner_zip.read(inner_name)
                            )
            except zipfile.BadZipFile:
                # If not a valid zip, skip
                pass

    zip_buffer.seek(0)
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=documents.zip"}
    )
        
