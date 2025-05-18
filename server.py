from fastapi import FastAPI, File, UploadFile, Query
from fastapi.responses import JSONResponse
from extraction import process_document_sample
from fastapi.middleware.cors import CORSMiddleware


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
                    lender: str = Query(...):
    
    if file.content_type != "application/pdf":
        return JSONResponse(status_code=400, content={"error": "File must be a PDF."})
    
    # Read the file content
    file_content = await file.read()


    try:
        result = process_document_sample(
            image_content=file_content,
            lender
        )

        return JSONResponse(status_code=200, content={"message": "success", "document_type": document_type, "result": result})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    
