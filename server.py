from fastapi import FastAPI, File, UploadFile, Query, Body
from fastapi.responses import JSONResponse
from extraction import process_document_sample
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from populateTemplate import populateFile
from fastapi.responses import StreamingResponse
import io
import zipfile


origins = ["*"]

app = FastAPI()



app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # List of allowed origins, or ["*"] for all
    allow_credentials=True,
    allow_methods=["*"],              # Allow all HTTP methods
    allow_headers=["*"],              # Allow all headers
)


class MatterInfo(BaseModel):
    directors: Optional[dict] = None
    company_borrower: Optional[dict] = None
    guarantor_1: Optional[dict] = None
    property_details: Optional[dict] = None
    fees: Optional[dict] = None
    loanDetails: Optional[dict] = None



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
    


templateStructures = {
    'Borrowers-Checklist': {
        "PROPDET1MORTGAGORS": "value1",
        "INSURANCEAMOUNT": "value2",
        "LOANSPECIALCONDITIONS": "value4",
        "Guarantor2Fullname": "value5"
    },
    'BC/Purchase/Standard': {
        'Company Guarantee Warranty (ShareHolders)': { 
            "GUARANTOR1FULLNAME": "value1",
            "GUARANTOR1ACN": "value2",
            "GUARANTOR1ADDRESSLINE1": "value3",
            "GUARANTOR1SUBURB": "value4",
            "GUARANTOR1STATE": "value5",
            "GUARANTOR1POSTCODE": "value6",
            "Bordetallnames": "value7",
            "BORDET1ACN": "value8",
            "BORDET1TRUSTNAME": "value9",
            "GUARANTOR1TRUSTNAME": "value10",
            "directors": [
            {
            "GUARANTORNAME": "value11"
            },
            {
            "GUARANTORNAME": "value12"
            },
            {
            "GUARANTORNAME": "value13"
            }
            ]
        },
        'Company Guarantee Warranty': {
            "GUARANTOR1FULLNAME": "value1",
            "GUARANTOR1ACN": "value2",
            "Bordetallnames": "value3",
            "BORDET1ACN": "value4",
            "BORDET1TRUSTNAME": "value5",
            "GUARANTOR1TRUSTNAME": "value6",
            "Guarantor2Fullname": "value7"
        },
        'Direct Debit Authority': {
            "LOANNUMBER": "value1",
            "Bordetallnames": "value2",
            "BORDET1ACN": "value3",
            "Guarantor2Fullname": "value4"
        },
        'Disbursement Direction Authority Purchase': {
            "Bordetallnames": "value1",
            "Propdetallsecadd": "value2",
            "ApplicationNumber": "value3",
            "LOANNUMBER": "value4",
            "Guarantor2Fullname": "value5",
            "guarantor_3_name": None,
            "Guarantor3Fullname": "value7",
            "PROPDETALLSECADD": "value8",
            "ADVANCEAMOUNT": "value9",
            "valuation_fee": "value10",
            "search_fee": "value11",
            "property_state": "value12",
            "NSW": "value13",
            "VIC": "value14",
            "QLD": "value15",
            "SA": "value16",
            "WA": "value17",
            "ACT": "value18",
            "TAS": "value19",
            "NT": "value20"
        },
        'Guarantee & Indemnity June 23': {
            "Bordetallnames": "value1",
            "BORDET1ACN": "value2",
            "BORDET1TRUSTNAME": "value3",
            "ApplicationNumber": "value4",
            "LOANNUMBER": "value5",
            "BORDET1FULLNAMESAL": "value6",
            "BORDET1ADDRESSLINE1": "value7",
            "BORDET1SUBURB": "value8",
            "BORDET1STATE": "value9",
            "BORDET1POSTCODE": "value10",
            "BORDET1EMAILADDRESS": "value11",
            "Guarantor2Fullname": "value12",
            "GUARANTOR2ADDRESSLINE1": "value13",
            "Guarantor2Suburb": "value14",
            "GUARANTOR2STATE": "value15",
            "GUARANTOR2POSTCODE": "value16",
            "GUARANTOR2EMAILADDRESS": "value17",
            "bordet1trustdate": "value18",
            "GUARANTOR1TRUSTNAME": "value19",
            "GUARANTOR1TRUSTDATE": "value20",
            "GUARANTOR1FULLNAME": "value21",
            "PROPDETALLSECADD": "value22",
            "directors": [
            {
            "GUARANTORFULLNAME": "value23"
            },
            {
            "GUARANTORFULLNAME": "value24"
            },
            {
            "GUARANTORFULLNAME": "value25"
            }
            ]
        },
        'Guarantee Indemnity Bare Trustee June 23': {
            "Bordetallnames": "value1",
            "BORDET1ACN": "value2",
            "BORDET1TRUSTNAME": "value3",
            "ApplicationNumber": "value4",
            "LOANNUMBER": "value5",
            "BORDET1FULLNAMESAL": "value6",
            "BORDET1ADDRESSLINE1": "value7",
            "BORDET1SUBURB": "value8",
            "BORDET1STATE": "value9",
            "BORDET1POSTCODE": "value10",
            "BORDET1EMAILADDRESS": "value11",
            "GUARANTOR1FULLNAME": "value12",
            "GUARANTOR1ACN": "value13",
            "GUARANTOR1ADDRESSLINE1": "value14",
            "GUARANTOR1SUBURB": "value15",
            "GUARANTOR1STATE": "value16",
            "GUARANTOR1POSTCODE": "value17",
            "GUARANTOR1EMAILADDRESS": "value18",
            "bordet1trustdate": "value19",
            "GUARANTOR1TRUSTNAME": "value20",
            "GUARANTOR1TRUSTDATE": "value21",
            "PROPDETALLSECADD": "value22"
        },
        'Guarantor Legal Advice Warranty': {
            "Bordetallnames": "value1",
            "BORDET1ACN": "value2",
            "BORDET1TRUSTNAME": "value3",
            "MATTERNUMBER": "value4",
            "Guarantor2Fullname": "value5"
        },
        'Guarantor Legal Advice': {
            "Bordetallnames": "value1",
            "BORDET1ACN": "value2",
            "BORDET1TRUSTNAME": "value3",
            "MATTERNUMBER": "value4",
            "Guarantor2Fullname": "value5",
            "Guarantor3Fullname": "value6"
        },
        
        'National Mortgage Form NSW': {
            "MATTERNUMBER": "value1",
            "PROPDET1TITREF": "value2",
            "Guarantor1Fullname": "value3",
            "Guarantor1ACN": "value4",
            "Guarantor2Fullname": "value5"
        },
        'National Mortgage Form QLD': {
            "MATTERNUMBER": "value1",
            "PROPDET1TITREF": "value2",
            "PROPDET1LOTDESC": "value3",
            "Guarantor1Fullname": "value4",
            "Guarantor1ACN": "value5",
            "Guarantor2Fullname": "value6"
        },
        'National Mortgage Form SA': {
            "MATTERNUMBER": "value1",
            "PROPDET1TITREF": "value2",
            "Guarantor1Fullname": "value3",
            "Guarantor1ACN": "value4",
            "BORDET1ADDRESSLINE1": "value5",
            "BORDET1SUBURB": "value6",
            "BORDET1STATE": "value7",
            "BORDET1POSTCODE": "value8",
            "Guarantor2Fullname": "value9"
        },
        'National Mortgage Form VIC': {
            "MATTERNUMBER": "value1",
            "PROPDET1TITREF": "value2",
            "Guarantor1Fullname": "value3",
            "Guarantor1ACN": "value4",
            "Guarantor2Fullname": "value5"
        },
        'Privacy Consent Form BC July 26 2024': {
            "Bordetallnames": "value1",
            "BORDET1ACN": "value2",
            "BORDET1TRUSTNAME": "value3",
            "Guarantor2Fullname": "value4"
        },
        'Warranties Fund Mortgaged Property June 23': {
            "Bordetallnames": "value1",
            "BORDET1ACN": "value2",
            "BORDET1TRUSTNAME": "value3",
            "PROPDETALLSECADD": "value4",
            "Guarantor2Fullname": "value5",
            "Guarantor2Addressline1": "value6",
            "Guarantor2Suburb": "value7",
            "Guarantor2State": "value8",
            "Guarantor2Postcode": "value9",
            "GUARANTOR1FULLNAME": "value10",
            "GUARANTOR1ACN": "value11",
            "GUARANTOR1TRUSTNAME": "value12"
        },
        '1. Credit Guide': {

        },
        '2. Loan Agreement - Terms and Conditions': {

        },
        '3. Mortgage Common Provisions': {},
        '4. Guarantee Information Statement': {},
        'SMSF Financing Agreement': {
            "Bordetallnames": "value1",
            "BORDET1ACN": "value2",
            "BORDET1TRUSTNAME": "value3",
            "directors": [
            {
            "GUARANTOR_FULLNAME": "value4"
            },
            {
            "GUARANTOR_FULLNAME": "value5"
            },
            {
            "GUARANTOR_FULLNAME": "value6"
            }
            ],
            "GUARANTOR1FULLNAME": "value7",
            "GUARANTOR1ACN": "value8",
            "ApplicationNumber": "value9",
            "LOANNUMBER": "value10",
            "BORDET1FULLNAME": "value11",
            "BORDET1ADDRESSLINE1": "value12",
            "BORDET1SUBURB": "value13",
            "BORDET1STATE": "value14",
            "BORDET1POSTCODE": "value15",
            "BORDET1EMAILADDRESS": "value16",
            "bordet1trustdate": "value17",
            "GUARANTOR1ADDRESSLINE1": "value18",
            "GUARANTOR1SUBURB": "value19",
            "GUARANTOR1STATE": "value20",
            "GUARANTOR1POSTCODE": "value21",
            "GUARANTOR1TRUSTNAME": "value22",
            "GUARANTOR1TRUSTDATE": "value23",
            "property_state": "value24",
            "ACT": "value25",
            "NSW": "value26",
            "NT": "value27",
            "QLD": "value28",
            "SA": "value29",
            "VIC": "value30",
            "TAS": "value31",
            "WA": "value32",
            "guarantor_2_name": "value33",
            "Guarantor2Addressline1": "value34",
            "Guarantor2Suburb": "value35",
            "Guarantor2State": "value36",
            "Guarantor2Postcode": "value37",
            "guarantor_3_name": None,
            "Guarantor3Addressline1": "value39",
            "Guarantor3Suburb": "value40",
            "Guarantor3State": "value41",
            "Guarantor3Postcode": "value42",
            "PROPDET1MORTGAGORS": "value43",
            "Guarantor2Fullname": "value44",
            "Guarantor3Fullname": "value45",
            "guarantor_4_name": "value46",
            "Guarantor4Fullname": "value47",
            "guarantor_5_name": "value48",
            "Guarantor5Fullname": "value49",
            "guarantor_6_name": "value50",
            "Guarantor6Fullname": "value51"
        },
        'Mortgage Side Agreement': { 
            "Bordetallnames": "value1",
            "BORDET1ACN": "value2",
            "BORDET1TRUSTNAME": "value3",
            "GUARANTOR1FULLNAME": "value4",
            "GUARANTOR1ACN": "value5",
            "GUARANTOR1TRUSTNAME": "value6",
            "ApplicationNumber": "value7",
            "LOANNUMBER": "value8",
            "PROPDET1MORTGAGORS": "value9",
            "GUARANTOR1ADDRESSLINE1": "value10",
            "GUARANTOR1SUBURB": "value11",
            "GUARANTOR1STATE": "value12",
            "GUARANTOR1POSTCODE": "value13",
            "GUARANTOR1EMAILADDRESS": "value14",
            "BORDET1FULLNAME": "value15",
            "BORDET1ADDRESSLINE1": "value16",
            "BORDET1SUBURB": "value17",
            "BORDET1POSTCODE": "value18",
            "BORDET1STATE": "value19",
            "BORDET1EMAILADDRESS": "value20",
            "bordet1trustdate": "value21",
            "PROPDETALLSECADD": "value22",
            "property_state": "value23",
            "ACT": "value24",
            "NSW": "value25",
            "NT": "value26",
            "QLD": "value27",
            "SA": "value28",
            "VIC": "value29",
            "TAS": "value30",
            "WA": "value31",
            "guarantor_2_name": "value32",
            "Guarantor2Addressline1": "value33",
            "Guarantor2Suburb": "value34",
            "Guarantor2State": "value35",
            "Guarantor2Postcode": "value36",
            "guarantor_3_name": None,
            "Guarantor3Addressline1": "value38",
            "Guarantor3Suburb": "value39",
            "Guarantor3State": "value40",
            "Guarantor3Postcode": "value41"
        }
    },
    'BC/Purchase/LoanAgreement': {
        'Loan Agreement Offer IO': {
            "Bordetallnames": "value1",
            "BORDET1ACN": "value2",
            "bordet1trustname": "value3",
            "PROPDETALLSECADD": "value4",
            "LoanNumber": "value5",
            "LOANPRODUCTTYPE": "value6",
            "ADVANCEAMOUNT": "value7",
            "IOInterestRate": "value8",
            "standardinterestrate": "value9",
            "IOTerm": "value10",
            "RepaymentAmount": "value11",
            "IORepayments": "value12",
            "PIRepayments": "value13",
            "app_fee": "value14",
            "lender_protection_fee": "value15",
            "ValFee": "value16",
            "documentation_fee": "value17",
            "MtgRegFee": "value18",
            "facilityterm": "value19",
            "BORDET1FULLNAMESAL": "value20",
            "BORDET1ADDRESSLINE1": "value21",
            "BORDET1SUBURB": "value22",
            "BORDET1STATE": "value23",
            "BORDET1postcode": "value24",
            "BORDET1EMAILADDRESS": "value25",
            "PROPDET1MORTGAGORS": "value26",
            "GUARANTOR1ADDRESSLINE1": "value27",
            "GUARANTOR1SUBURB": "value28",
            "GUARANTOR1STATE": "value29",
            "GUARANTOR1POSTCODE": "value30",
            "LOANPURPOSE": "value31",
            "LVR": "value32",
            "GUARANTOR2FULLNAME": "value33",
            "GUARANTOR3FULLNAME": "value34",
            "advanceamount": "value35",
            "LOANSPECIALCONDITIONS": "value36",
            "DefaultInterestRate": "value37",
            "guarantor_2_name": "value38",
            "Guarantor3Fullname": "value39",
            "Guarantor2Fullname": "value40"
    },
    'Loan Agreement Offer PI': {
            "Bordetallnames": "value1",
            "BORDET1ACN": "value2",
            "BORDET1TRUSTNAME": "value3",
            "PROPDETALLSECADD": "value4",
            "LOANNUMBER": "value5",
            "LOANPRODUCTTYPE": "value6",
            "ADVANCEAMOUNT": "value7",
            "IOInterestRate": "value8",
            "standardinterestrate": "value9",
            "IOTerm": "value10",
            "RepaymentAmount": "value11",
            "IORepayments": "value12",
            "PIRepayments": "value13",
            "app_fee": "value14",
            "lender_protection_fee": "value15",
            "ValFee": "value16",
            "documentation_fee": "value17",
            "MtgRegFee": "value18",
            "facilityterm": "value19",
            "BORDET1FULLNAMESAL": "value20",
            "BORDET1ADDRESSLINE1": "value21",
            "BORDET1SUBURB": "value22",
            "BORDET1STATE": "value23",
            "BORDET1POSTCODE": "value24",
            "BORDET1EMAILADDRESS": "value25",
            "PROPDET1MORTGAGORS": "value26",
            "GUARANTOR1ADDRESSLINE1": "value27",
            "GUARANTOR1SUBURB": "value28",
            "GUARANTOR1STATE": "value29",
            "GUARANTOR1POSTCODE": "value30",
            "LOANPURPOSE": "value31",
            "LVR": "value32",
            "Guarantor2Fullname": "value33",
            "Guarantor3Fullname": "value34",
            "LOANSPECIALCONDITIONS": "value35",
            "DefaultInterestRate": "value36",
            "guarantor_2_name": "value37",
            "guarantor_3_name": None
    }
    },
    'BC/Refi/Standard': {
        'Company Guarantee Warranty (ShareHolders)': { 
            "GUARANTOR1FULLNAME": "value1",
            "GUARANTOR1ACN": "value2",
            "GUARANTOR1ADDRESSLINE1": "value3",
            "GUARANTOR1SUBURB": "value4",
            "GUARANTOR1STATE": "value5",
            "GUARANTOR1POSTCODE": "value6",
            "Bordetallnames": "value7",
            "BORDET1ACN": "value8",
            "BORDET1TRUSTNAME": "value9",
            "GUARANTOR1TRUSTNAME": "value10",
            "directors": [
            {
            "GUARANTORNAME": "value11"
            },
            {
            "GUARANTORNAME": "value12"
            },
            {
            "GUARANTORNAME": "value13"
            }
            ]
        },
        'Company Guarantee Warranty': {
            "GUARANTOR1FULLNAME": "value1",
            "GUARANTOR1ACN": "value2",
            "Bordetallnames": "value3",
            "BORDET1ACN": "value4",
            "BORDET1TRUSTNAME": "value5",
            "GUARANTOR1TRUSTNAME": "value6",
            "Guarantor2Fullname": "value7"
        },
        'Direct Debit Authority': {
            "LOANNUMBER": "value1",
            "Bordetallnames": "value2",
            "BORDET1ACN": "value3",
            "Guarantor2Fullname": "value4"
        },
        'Disbursement Direction Authority Refi': {
            "Bordetallnames": "value1",
            "Propdetallsecadd": "value2",
            "ApplicationNumber": "value3",
            "LOANNUMBER": "value4",
            "Guarantor2Fullname": "value5",
            "guarantor_3_name": None,
            "Guarantor3Fullname": "value7",
            "PROPDETALLSECADD": "value8",
            "ADVANCEAMOUNT": "value9",
            "valuation_fee": "value10",
            "search_fee": "value11",
            "property_state": "value12",
            "NSW": "value13",
            "VIC": "value14",
            "QLD": "value15",
            "SA": "value16",
            "WA": "value17",
            "ACT": "value18",
            "TAS": "value19",
            "NT": "value20"
        },
        'Guarantee & Indemnity June 23': {
            "Bordetallnames": "value1",
            "BORDET1ACN": "value2",
            "BORDET1TRUSTNAME": "value3",
            "ApplicationNumber": "value4",
            "LOANNUMBER": "value5",
            "BORDET1FULLNAMESAL": "value6",
            "BORDET1ADDRESSLINE1": "value7",
            "BORDET1SUBURB": "value8",
            "BORDET1STATE": "value9",
            "BORDET1POSTCODE": "value10",
            "BORDET1EMAILADDRESS": "value11",
            "Guarantor2Fullname": "value12",
            "GUARANTOR2ADDRESSLINE1": "value13",
            "Guarantor2Suburb": "value14",
            "GUARANTOR2STATE": "value15",
            "GUARANTOR2POSTCODE": "value16",
            "GUARANTOR2EMAILADDRESS": "value17",
            "bordet1trustdate": "value18",
            "GUARANTOR1TRUSTNAME": "value19",
            "GUARANTOR1TRUSTDATE": "value20",
            "GUARANTOR1FULLNAME": "value21",
            "PROPDETALLSECADD": "value22",
            "directors": [
            {
            "GUARANTORFULLNAME": "value23"
            },
            {
            "GUARANTORFULLNAME": "value24"
            },
            {
            "GUARANTORFULLNAME": "value25"
            }
            ]
        },
        'Guarantee Indemnity Bare Trustee June 23': {
            "Bordetallnames": "value1",
            "BORDET1ACN": "value2",
            "BORDET1TRUSTNAME": "value3",
            "ApplicationNumber": "value4",
            "LOANNUMBER": "value5",
            "BORDET1FULLNAMESAL": "value6",
            "BORDET1ADDRESSLINE1": "value7",
            "BORDET1SUBURB": "value8",
            "BORDET1STATE": "value9",
            "BORDET1POSTCODE": "value10",
            "BORDET1EMAILADDRESS": "value11",
            "GUARANTOR1FULLNAME": "value12",
            "GUARANTOR1ACN": "value13",
            "GUARANTOR1ADDRESSLINE1": "value14",
            "GUARANTOR1SUBURB": "value15",
            "GUARANTOR1STATE": "value16",
            "GUARANTOR1POSTCODE": "value17",
            "GUARANTOR1EMAILADDRESS": "value18",
            "bordet1trustdate": "value19",
            "GUARANTOR1TRUSTNAME": "value20",
            "GUARANTOR1TRUSTDATE": "value21",
            "PROPDETALLSECADD": "value22"
        },
        'Guarantor Legal Advice Warranty': {
            "Bordetallnames": "value1",
            "BORDET1ACN": "value2",
            "BORDET1TRUSTNAME": "value3",
            "MATTERNUMBER": "value4",
            "Guarantor2Fullname": "value5"
        },
        'Guarantor Legal Advice': {
            "Bordetallnames": "value1",
            "BORDET1ACN": "value2",
            "BORDET1TRUSTNAME": "value3",
            "MATTERNUMBER": "value4",
            "Guarantor2Fullname": "value5",
            "Guarantor3Fullname": "value6"
        },
        
        'National Mortgage Form NSW': {
            "MATTERNUMBER": "value1",
            "PROPDET1TITREF": "value2",
            "Guarantor1Fullname": "value3",
            "Guarantor1ACN": "value4",
            "Guarantor2Fullname": "value5"
        },
        'National Mortgage Form QLD': {
            "MATTERNUMBER": "value1",
            "PROPDET1TITREF": "value2",
            "PROPDET1LOTDESC": "value3",
            "Guarantor1Fullname": "value4",
            "Guarantor1ACN": "value5",
            "Guarantor2Fullname": "value6"
        },
        'National Mortgage Form SA': {
            "MATTERNUMBER": "value1",
            "PROPDET1TITREF": "value2",
            "Guarantor1Fullname": "value3",
            "Guarantor1ACN": "value4",
            "BORDET1ADDRESSLINE1": "value5",
            "BORDET1SUBURB": "value6",
            "BORDET1STATE": "value7",
            "BORDET1POSTCODE": "value8",
            "Guarantor2Fullname": "value9"
        },
        'National Mortgage Form VIC': {
            "MATTERNUMBER": "value1",
            "PROPDET1TITREF": "value2",
            "Guarantor1Fullname": "value3",
            "Guarantor1ACN": "value4",
            "Guarantor2Fullname": "value5"
        },
        'Privacy Consent Form BC July 26 2024': {
            "Bordetallnames": "value1",
            "BORDET1ACN": "value2",
            "BORDET1TRUSTNAME": "value3",
            "Guarantor2Fullname": "value4"
        },
        'Warranties Fund Mortgaged Property June 23': {
            "Bordetallnames": "value1",
            "BORDET1ACN": "value2",
            "BORDET1TRUSTNAME": "value3",
            "PROPDETALLSECADD": "value4",
            "Guarantor2Fullname": "value5",
            "Guarantor2Addressline1": "value6",
            "Guarantor2Suburb": "value7",
            "Guarantor2State": "value8",
            "Guarantor2Postcode": "value9",
            "GUARANTOR1FULLNAME": "value10",
            "GUARANTOR1ACN": "value11",
            "GUARANTOR1TRUSTNAME": "value12"
        },
        '1. Credit Guide': {

        },
        '2. Loan Agreement - Terms and Conditions': {

        },
        '3. Mortgage Common Provisions': {},
        '4. Guarantee Information Statement': {},
        'SMSF Financing Agreement': {
            "Bordetallnames": "value1",
            "BORDET1ACN": "value2",
            "BORDET1TRUSTNAME": "value3",
            "directors": [
            {
            "GUARANTOR_FULLNAME": "value4"
            },
            {
            "GUARANTOR_FULLNAME": "value5"
            },
            {
            "GUARANTOR_FULLNAME": "value6"
            }
            ],
            "GUARANTOR1FULLNAME": "value7",
            "GUARANTOR1ACN": "value8",
            "ApplicationNumber": "value9",
            "LOANNUMBER": "value10",
            "BORDET1FULLNAME": "value11",
            "BORDET1ADDRESSLINE1": "value12",
            "BORDET1SUBURB": "value13",
            "BORDET1STATE": "value14",
            "BORDET1POSTCODE": "value15",
            "BORDET1EMAILADDRESS": "value16",
            "bordet1trustdate": "value17",
            "GUARANTOR1ADDRESSLINE1": "value18",
            "GUARANTOR1SUBURB": "value19",
            "GUARANTOR1STATE": "value20",
            "GUARANTOR1POSTCODE": "value21",
            "GUARANTOR1TRUSTNAME": "value22",
            "GUARANTOR1TRUSTDATE": "value23",
            "property_state": "value24",
            "ACT": "value25",
            "NSW": "value26",
            "NT": "value27",
            "QLD": "value28",
            "SA": "value29",
            "VIC": "value30",
            "TAS": "value31",
            "WA": "value32",
            "guarantor_2_name": "value33",
            "Guarantor2Addressline1": "value34",
            "Guarantor2Suburb": "value35",
            "Guarantor2State": "value36",
            "Guarantor2Postcode": "value37",
            "guarantor_3_name": None,
            "Guarantor3Addressline1": "value39",
            "Guarantor3Suburb": "value40",
            "Guarantor3State": "value41",
            "Guarantor3Postcode": "value42",
            "PROPDET1MORTGAGORS": "value43",
            "Guarantor2Fullname": "value44",
            "Guarantor3Fullname": "value45",
            "guarantor_4_name": "value46",
            "Guarantor4Fullname": "value47",
            "guarantor_5_name": "value48",
            "Guarantor5Fullname": "value49",
            "guarantor_6_name": "value50",
            "Guarantor6Fullname": "value51"
        },
        'Mortgage Side Agreement': { 
            "Bordetallnames": "value1",
            "BORDET1ACN": "value2",
            "BORDET1TRUSTNAME": "value3",
            "GUARANTOR1FULLNAME": "value4",
            "GUARANTOR1ACN": "value5",
            "GUARANTOR1TRUSTNAME": "value6",
            "ApplicationNumber": "value7",
            "LOANNUMBER": "value8",
            "PROPDET1MORTGAGORS": "value9",
            "GUARANTOR1ADDRESSLINE1": "value10",
            "GUARANTOR1SUBURB": "value11",
            "GUARANTOR1STATE": "value12",
            "GUARANTOR1POSTCODE": "value13",
            "GUARANTOR1EMAILADDRESS": "value14",
            "BORDET1FULLNAME": "value15",
            "BORDET1ADDRESSLINE1": "value16",
            "BORDET1SUBURB": "value17",
            "BORDET1POSTCODE": "value18",
            "BORDET1STATE": "value19",
            "BORDET1EMAILADDRESS": "value20",
            "bordet1trustdate": "value21",
            "PROPDETALLSECADD": "value22",
            "property_state": "value23",
            "ACT": "value24",
            "NSW": "value25",
            "NT": "value26",
            "QLD": "value27",
            "SA": "value28",
            "VIC": "value29",
            "TAS": "value30",
            "WA": "value31",
            "guarantor_2_name": "value32",
            "Guarantor2Addressline1": "value33",
            "Guarantor2Suburb": "value34",
            "Guarantor2State": "value35",
            "Guarantor2Postcode": "value36",
            "guarantor_3_name": None,
            "Guarantor3Addressline1": "value38",
            "Guarantor3Suburb": "value39",
            "Guarantor3State": "value40",
            "Guarantor3Postcode": "value41"
        }
    },
    'BC/Refi/LoanAgreement': {
        'Loan Agreement Offer IO': {
            "Bordetallnames": "value1",
            "BORDET1ACN": "value2",
            "bordet1trustname": "value3",
            "PROPDETALLSECADD": "value4",
            "LoanNumber": "value5",
            "LOANPRODUCTTYPE": "value6",
            "ADVANCEAMOUNT": "value7",
            "IOInterestRate": "value8",
            "standardinterestrate": "value9",
            "IOTerm": "value10",
            "RepaymentAmount": "value11",
            "IORepayments": "value12",
            "PIRepayments": "value13",
            "app_fee": "value14",
            "lender_protection_fee": "value15",
            "ValFee": "value16",
            "documentation_fee": "value17",
            "MtgRegFee": "value18",
            "facilityterm": "value19",
            "BORDET1FULLNAMESAL": "value20",
            "BORDET1ADDRESSLINE1": "value21",
            "BORDET1SUBURB": "value22",
            "BORDET1STATE": "value23",
            "BORDET1postcode": "value24",
            "BORDET1EMAILADDRESS": "value25",
            "PROPDET1MORTGAGORS": "value26",
            "GUARANTOR1ADDRESSLINE1": "value27",
            "GUARANTOR1SUBURB": "value28",
            "GUARANTOR1STATE": "value29",
            "GUARANTOR1POSTCODE": "value30",
            "LOANPURPOSE": "value31",
            "LVR": "value32",
            "GUARANTOR2FULLNAME": "value33",
            "GUARANTOR3FULLNAME": "value34",
            "advanceamount": "value35",
            "LOANSPECIALCONDITIONS": "value36",
            "DefaultInterestRate": "value37",
            "guarantor_2_name": "value38",
            "Guarantor3Fullname": "value39",
            "Guarantor2Fullname": "value40"
    },
    'Loan Agreement Offer PI': {
            "Bordetallnames": "value1",
            "BORDET1ACN": "value2",
            "BORDET1TRUSTNAME": "value3",
            "PROPDETALLSECADD": "value4",
            "LOANNUMBER": "value5",
            "LOANPRODUCTTYPE": "value6",
            "ADVANCEAMOUNT": "value7",
            "IOInterestRate": "value8",
            "standardinterestrate": "value9",
            "IOTerm": "value10",
            "RepaymentAmount": "value11",
            "IORepayments": "value12",
            "PIRepayments": "value13",
            "app_fee": "value14",
            "lender_protection_fee": "value15",
            "ValFee": "value16",
            "documentation_fee": "value17",
            "MtgRegFee": "value18",
            "facilityterm": "value19",
            "BORDET1FULLNAMESAL": "value20",
            "BORDET1ADDRESSLINE1": "value21",
            "BORDET1SUBURB": "value22",
            "BORDET1STATE": "value23",
            "BORDET1POSTCODE": "value24",
            "BORDET1EMAILADDRESS": "value25",
            "PROPDET1MORTGAGORS": "value26",
            "GUARANTOR1ADDRESSLINE1": "value27",
            "GUARANTOR1SUBURB": "value28",
            "GUARANTOR1STATE": "value29",
            "GUARANTOR1POSTCODE": "value30",
            "LOANPURPOSE": "value31",
            "LVR": "value32",
            "Guarantor2Fullname": "value33",
            "Guarantor3Fullname": "value34",
            "LOANSPECIALCONDITIONS": "value35",
            "DefaultInterestRate": "value36",
            "guarantor_2_name": "value37",
            "guarantor_3_name": None
    }
    }
}

docmosisDirectories = {
    'Company Guarantee Warranty': 'SMSF/Purchase/BC/Company Guarantee Warranty.docx',
    'Company Guarantee Warranty (ShareHolders)': 'SMSF/Purchase/BC/Company Guarantee Warranty (ShareHolders).docx',
    'Direct Debit Authority': 'SMSF/Purchase/BC/Direct Debit Authority.docx',
    'Disbursement Direction Authority Purchase': 'SMSF/Purchase/BC/Disbursement Direction Authority Purchase.docx',
    'Guarantee & Indemnity June 23': 'SMSF/Purchase/BC/Guarantee & Indemnity June 23.docx',
    'Guarantee Indemnity Bare Trustee June 23': 'SMSF/Purchase/BC/Guarantee Indemnity Bare Trustee June 23.docx',
    'Guarantor Legal Advice Warranty': 'SMSF/Purchase/BC/Guarantor Legal Advice Warranty.docx',
    'Guarantor Legal Advice': 'SMSF/Purchase/BC/Guarantor Legal Advice.docx',
    'Privacy Consent Form BC July 26 2024': 'SMSF/Purchase/BC/Privacy Consent Form BC July 26 2024.docx',
    'Warranties Fund Mortgaged Property June 23': 'SMSF/Purchase/BC/Warranties Fund Mortgaged Property June 23.docx',
    '0. Borrowers Checklist SMSF Purchase Wet sign Mortgage': 'SMSF/Purchase/BC/WetSign/0. Borrowers Checklist SMSF Purchase Wet sign Mortgage.docx',
    '0. Borrowers Checklist SMSF NSW Purchase': 'SMSF/Purchase/BC/NSW/0. Borrowers Checklist SMSF NSW Purchase.docx',
    '0. Borrowers Checklist SMSF Purchase Hybrid': 'SMSF/Purchase/BC/0. Borrowers Checklist SMSF Purchase Hybrid.docx',
    'National Mortgage Form NSW': 'SMSF/Purchase/BC/National Mortgage Form NSW.docx',
    'National Mortgage Form QLD': 'SMSF/Purchase/BC/National Mortgage Form QLD.docx',
    'National Mortgage Form SA': 'SMSF/Purchase/BC/National Mortgage Form SA.docx',
    'National Mortgage Form VIC': 'SMSF/Purchase/BC/National Mortgage Form VIC.docx',
    'Loan Agreement Offer IO': 'SMSF/Purchase/BC/Loan Agreement Offer IO.docx',
    'Loan Agreement Offer PI': 'SMSF/Purchase/BC/Loan Agreement Offer PI.docx',
    '1. Credit Guide': 'SMSF/Purchase/BC/1. Credit Guide.docx',
    '2. Loan Agreement - Terms and Conditions': 'SMSF/Purchase/BC/2. Loan Agreement - Terms and Conditions.docx',
    '3. Mortgage Common Provisions': 'SMSF/Purchase/BC/3. Mortgage Common Provisions.docx',
    '4. Guarantee Information Statement': 'SMSF/Purchase/BC/4. Guarantee Information Statement.docx',
    'SMSF Financing Agreement': 'SMSF/Purchase/BC/SMSF Financing Agreement.docx',
    'Mortgage Side Agreement': 'SMSF/Purchase/BC/Mortgage Side Agreement.docx',
    '0. Borrowers Checklist SMSF Refi (no ILA)': 'SMSF/Refi/BC/0. Borrowers Checklist SMSF Refi (no ILA).docx',
    '0. Borrowers Checklist SMSF Refi Hybrid (wet sign mortgage)': 'SMSF/Refi/BC/WetSign/0. Borrowers Checklist SMSF Refi Hybrid (wet sign mortgage).docx',
    'Disbursement Direction Authority Refi': 'SMSF/Refi/BC/Disbursement Direction Authority Refi.docx'
}


fileDirectory = {
    'SMSF/Purchase/BC/' : {
        'Borrowers-Checklist': {
            'Wetsign': '0. Borrowers Checklist SMSF Purchase Wet sign Mortgage',
            'NSW': '0. Borrowers Checklist SMSF NSW Purchase',
            'Non-Wetsign-NSW': '0. Borrowers Checklist SMSF Purchase Hybrid',
        },
        'Standard': [
            'Company Guarantee Warranty',
            'Company Guarantee Warranty (ShareHolders)',
            'Direct Debit Authority',
            'Disbursement Direction Authority Purchase',
            'Guarantee & Indemnity June 23',
            'Guarantee Indemnity Bare Trustee June 23',
            'Guarantor Legal Advice Warranty',
            'Guarantor Legal Advice',
            'Privacy Consent Form BC July 26 2024',
            'Warranties Fund Mortgaged Property June 23',
            '1. Credit Guide',
            '2. Loan Agreement - Terms and Conditions',
            '3. Mortgage Common Provisions',
            '4. Guarantee Information Statement',
            'SMSF Financing Agreement',
            'Mortgage Side Agreement'
        ],
        'Loan-Agreement': {
            'IO': 'Loan Agreement Offer IO',
            'PI': 'Loan Agreement Offer PI'
        },
        'NSW-Specific': [
            'National Mortgage Form NSW'
        ],
        'QLD-Specific': [
            'National Mortgage Form QLD'
        ],
        'SA-Specific': [
            'National Mortgage Form SA'
        ],
        'VIC-Specific': [
            'National Mortgage Form VIC'
        ]
        
    },
    'SMSF/Refi/BC/': {
      'Borrowers-Checklist': {
            'Wetsign': '0. Borrowers Checklist SMSF Refi Hybrid (wet sign mortgage)',
            'Non-Wetsign-NSW': '0. Borrowers Checklist SMSF Refi (no ILA)',
        },
        'Standard': [
            'Company Guarantee Warranty',
            'Company Guarantee Warranty (ShareHolders)',
            'Direct Debit Authority',
            'Disbursement Direction Authority Refi',
            'Guarantee & Indemnity June 23',
            'Guarantee Indemnity Bare Trustee June 23',
            'Guarantor Legal Advice Warranty',
            'Guarantor Legal Advice',
            'Privacy Consent Form BC July 26 2024',
            'Warranties Fund Mortgaged Property June 23',
            '1. Credit Guide',
            '2. Loan Agreement - Terms and Conditions',
            '3. Mortgage Common Provisions',
            '4. Guarantee Information Statement',
            'SMSF Financing Agreement',
            'Mortgage Side Agreement'
        ],
        'Loan-Agreement': {
            'IO': 'Loan Agreement Offer IO',
            'PI': 'Loan Agreement Offer PI'
        },
        'NSW-Specific': [
            'National Mortgage Form NSW'
        ],
        'QLD-Specific': [
            'National Mortgage Form QLD'
        ],
        'SA-Specific': [
            'National Mortgage Form SA'
        ],
        'VIC-Specific': [
            'National Mortgage Form VIC'
        ]
    },
    'SMSF/Purchase/Source/': [

    ],
    'SMSF/Refi/Source/': [

    ]
}

@app.post('/documents/populate')
async def populate(
    lender: str = Query(...),
    matter_type: str = Query(...),
    transaction_type: str = Query(...),
    state: str = Query(...),
    loan_type: str = Query(...),
    matter_info: dict = Body(...),  # MatterInfo is the Pydantic model
):
    baseURL = matter_type + '/' + transaction_type + '/' + lender + '/'
    baseFiles = fileDirectory[baseURL]
    matterFiles = []

    #Borrower Checklist Logic:
    Wetsign = state == 'WA' or state == 'TAS' or state == 'NT'
    isNSWMatter = state == 'NSW'
    if (Wetsign):
        borrowersChecklist = baseFiles['Borrowers-Checklist']['Wetsign']
    elif (isNSWMatter and transaction_type == "Purchase"):
        borrowersChecklist = baseFiles['Borrowers-Checklist']['NSW']
    else:
        borrowersChecklist = baseFiles['Borrowers-Checklist']['Non-Wetsign-NSW']

    matterFiles.append(borrowersChecklist)

    loanAgreement = baseFiles['Loan-Agreement'][loan_type]

    matterFiles.append(loanAgreement)

    stateSpecificFiles = baseFiles.get(f'{state}-Specific', {})

    if (stateSpecificFiles):
        matterFiles.extend(stateSpecificFiles)


    matterFiles.extend(baseFiles.get('Standard', []))

    jsonTemplates = {}

    standardDir = f'{lender}/{transaction_type}/Standard'
    loanAgreementDir = f'{lender}/{transaction_type}/LoanAgreement'
    BorrowersChecklistDir = f'Borrowers-Checklist'

    #Get Standard JSON Templates
    for key in templateStructures[standardDir]:
        if key in matterFiles:
            newDict = templateStructures[standardDir][key].copy()
            for key2 in templateStructures[standardDir][key]:
                data = matter_info['matter_info'].get(key2, '')
                if (data is not None):
                    newDict[key2] = data
            jsonTemplates[key] = newDict

    #Format Loan Agreements
    print(matterFiles)
    for key in templateStructures[loanAgreementDir]:
          if key in matterFiles:
            newDict = templateStructures[loanAgreementDir][key].copy()
            for key2 in templateStructures[loanAgreementDir][key]:

                data = matter_info['matter_info'].get(key2, '')
                print('loan agreement ' + key2)
                if (data is not None):
                    newDict[key2] = data
            jsonTemplates[key] = newDict

    #Format Borrowers Checklist
    newDict = templateStructures[BorrowersChecklistDir].copy()
    for key2 in templateStructures[BorrowersChecklistDir]:
        data = matter_info['matter_info'].get(key2, '')
        if (data is not None):
            newDict[key2] = data
    jsonTemplates[borrowersChecklist] = newDict


    files = []

    for key in jsonTemplates:
        data = jsonTemplates[key]
        path = docmosisDirectories[key]
        print(path)
        print(data)

        pdf_bytes = populateFile(path, data, f"{key}.pdf")
        print(type(pdf_bytes))
        files.append((f"{key}.pdf", pdf_bytes))

        
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for filename, content in files:
            zipf.writestr(filename, content)

    zip_buffer.seek(0)
    return StreamingResponse(zip_buffer, media_type="application/zip", headers={
        "Content-Disposition": "attachment; filename=documents.zip"
    })




    


    # Return the response wrapped in JSONResponse
    