from fastapi import FastAPI, File, UploadFile, Query, Body
from fastapi.responses import JSONResponse
from extraction import process_document_sample
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from populateTemplate import populateFile, getTemplateStucture
from constants import DOCMOSIS_DIRECTORIES
from fastapi.responses import StreamingResponse
from docxtpl import DocxTemplate
from io import BytesIO
import zipfile



from helpers import getBorrowerChecklist, structureJson, getTemplates, get_templates_async, generate_all_pdfs, populate_file_async, upload_convert_delete

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
    if "Commercial" in transaction_type:
        directoryIndex = matter_type + '/' + transaction_type + '/'
    
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

    #Matter files completed here
    
    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, "w") as zipf:

        # ---- MAIN TEMPLATE FILES ----
        for file in matterFiles:
            if not file:
                continue
            fileName = file.split('/')[-1]
            print("Processing File: " + fileName)

            doc_temp = DocxTemplate(file)
            doc_temp.render(matter_info)

            file_buffer = BytesIO()
            doc_temp.save(file_buffer)
            file_buffer.seek(0)
            docx_bytes = file_buffer.read()
            # Add DOCX to ZIP
            zipf.writestr(f"docx/{fileName}", docx_bytes)

            # Add PDF to ZIP (same name, different folder)
            upload_convert_delete(fileName, docx_bytes, zipf)
         

            print("merged DOCX and converted PDF")

        # ---- INDIVIDUAL LEGAL ADVICE: BC Purchase ----
        if lender == "BC" and 'Purchase' in transaction_type:
            template_path = "SMSF/Purchase/BC/17. Individual Legal Advice Certificate.docx"
            for director in matter_info["directors"]:
                context = matter_info.copy()
                context.update(director)

                doc_temp = DocxTemplate(template_path)
                doc_temp.render(context)

                filename = (
                    template_path.split('/')[-1][:-5]
                    + f" - {director['GUARANTORNAME']}.docx"
                )

                file_buffer = BytesIO()
                doc_temp.save(file_buffer)
                file_buffer.seek(0)
                docx_bytes = file_buffer.read()

                upload_convert_delete(filename, docx_bytes, zipf)
                zipf.writestr(f"docx/{filename}", file_buffer.read())

        # ---- GUARANTOR LEGAL ADVICE WARRANTY: BC Refi ----
        if lender == "BC" and "Refi" in transaction_type:
            template_path = "SMSF/Refi/BC/12. Guarantor Legal Advice Warranty.docx"
            for director in matter_info["directors"]:
                context = matter_info.copy()
                context.update(director)

                doc_temp = DocxTemplate(template_path)
                doc_temp.render(context)

                filename = (
                    template_path.split('/')[-1][:-5]
                    + f" - {director['GUARANTORNAME']}.docx"
                )

                file_buffer = BytesIO()
                doc_temp.save(file_buffer)
                file_buffer.seek(0)

                docx_bytes = file_buffer.read()

                upload_convert_delete(filename, docx_bytes, zipf)
                zipf.writestr(f"docx/{filename}", file_buffer.read())

        # ---- SOURCE PURCHASE (not NSW) ----
        if lender == "Source" and transaction_type == "Purchase" and matter_info["property_state"] != "NSW":
            template_path = "SMSF/Purchase/Source/12. Solicitors Certificate Guarantor.docx"
            for director in matter_info["directors"]:
                context = matter_info.copy()
                context.update(director)

                doc_temp = DocxTemplate(template_path)
                doc_temp.render(context)

                filename = (
                    template_path.split('/')[-1][:-5]
                    + f" - {director['GUARANTORNAME']}.docx"
                )

                file_buffer = BytesIO()
                doc_temp.save(file_buffer)
                file_buffer.seek(0)

                docx_bytes = file_buffer.read()

                upload_convert_delete(filename, docx_bytes, zipf)
                zipf.writestr(f"docx/{filename}", file_buffer.read())

        # ---- SOURCE PURCHASE (NSW) ----
        if lender == "Source" and transaction_type == "Purchase" and matter_info["property_state"] == "NSW":
            template_path = "SMSF/Purchase/Source/12. Legal Advice Declaration - NSW.docx"
            for director in matter_info["directors"]:
                context = matter_info.copy()
                context.update(director)

                doc_temp = DocxTemplate(template_path)
                doc_temp.render(context)

                filename = (
                    template_path.split('/')[-1][:-5]
                    + f" - {director['GUARANTORNAME']}.docx"
                )

                file_buffer = BytesIO()
                doc_temp.save(file_buffer)
                file_buffer.seek(0)

                docx_bytes = file_buffer.read()

                upload_convert_delete(filename, docx_bytes, zipf)
                zipf.writestr(f"docx/{filename}", file_buffer.read())

    # FINAL ZIP RESPONSE
    zip_buffer.seek(0)

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": "attachment; filename=merged_documents.zip"
        },
    )


    

        
    # # zip_buffer = io.BytesIO()
    # # with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
    # #     for filename, content in files:
    # #         zipf.writestr(filename, content)

    # # zip_buffer.seek(0)
    # # return StreamingResponse(
    # #     zip_buffer,
    # #     media_type="application/zip",
    # #     headers={"Content-Disposition": "attachment; filename=documents.zip"}
    # # )
    # zip_buffer = io.BytesIO()
    
    # with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as final_zip:
    #     for outer_filename, outer_content in files:
    #         inner_zip_bytes = io.BytesIO(outer_content)
    
    #         try:
    #             with zipfile.ZipFile(inner_zip_bytes, "r") as inner_zip:
    #                 for inner_name in inner_zip.namelist():
    #                     if inner_name.endswith("/"):
    #                         continue  # skip directories
    
    #                     # Extract base filename (ignore any folder paths inside zip)
    #                     base_inner_name = os.path.basename(inner_name)
    
    #                     # Make sure it has a clean extension (no .zip.docx, etc.)
    #                     base_inner_name = os.path.splitext(base_inner_name)[0]
    
    #                     if inner_name.lower().endswith(".pdf"):
    #                         final_zip.writestr(
    #                             f"pdfs/{base_inner_name}.pdf",
    #                             inner_zip.read(inner_name)
    #                         )
    #                     elif inner_name.lower().endswith(".docx"):
    #                         final_zip.writestr(
    #                             f"docs/{base_inner_name}.docx",
    #                             inner_zip.read(inner_name)
    #                         )
    #                     # else: skip non-docx/pdf files entirely
    
    #         except zipfile.BadZipFile:
    #             # Skip invalid zip files gracefully
    #             pass
    
    # zip_buffer.seek(0)
    # return StreamingResponse(
    #     zip_buffer,
    #     media_type="application/zip",
    #     headers={"Content-Disposition": "attachment; filename=documents.zip"}
    # )
        
