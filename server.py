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
        "Guarantor2Fullname": "value5",
          "directors": [
         
        ],
        "PROPDET1MORTGAGORS": "value4",
        "INSURANCEAMOUNT": "value5",
        "LOANSPECIALCONDITIONS": "value6"
    },
    'BC/Purchase/Standard': {
        '13. Company Guarantee Warranty (ShareHolders)': { 
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
        '12. Company Guarantee Warranty': {
            "GUARANTOR1FULLNAME": "value1",
            "GUARANTOR1ACN": "value2",
            "Bordetallnames": "value3",
            "BORDET1ACN": "value4",
            "BORDET1TRUSTNAME": "value5",
            "GUARANTOR1TRUSTNAME": "value6",
            "Guarantor2Fullname": "value7"
        },
        '16. Direct Debit Authority': {
            "LOANNUMBER": "value1",
            "Bordetallnames": "value2",
            "BORDET1ACN": "value3",
            "Guarantor2Fullname": "value4"
        },
        '15. Disbursement Direction Authority Purchase': {
                                                    "Bordetallnames": "value1",
                                                    "Propdetallsecadd": "value2",
                                                    "ApplicationNumber": "value3",
                                                    "LOANNUMBER": "value4",
                                                    "Guarantor2Fullname": "value5",
                                                    "guarantor_3_name": "value6",
                                                    "Guarantor3Fullname": "value7",
                                                    "PROPDETALLSECADD": "value8",
                                                    "ADVANCEAMOUNT": "value9",
                                                    "app_fee": "value10",
                                                    "valuation_fee": "value11",
                                                    "settlement_fee": "value12",
                                                    "lender_protection_fee": "value13",
                                                    "annual_package_fee": "value14",
                                                    "documentation_fee": "value15",
                                                    "trust_deed_review_fee": "value16",
                                                    "sundry_fee": "value17",
                                                    "search_fee": "value18",
                                                    "property_state": "value19",
                                                    "NSW": "NSW",
                                                    "VIC": "VIC",
                                                    "QLD": "QLD",
                                                    "SA": "SA",
                                                    "WA": "WA",
                                                    "ACT": "ACT",
                                                    "TAS": "TAS",
                                                    "NT": "NT"
                                                    },
        '11. Guarantee & Indemnity June 23': {
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
        '10. Guarantee Indemnity Bare Trustee June 23': {
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
        '12. Guarantor Legal Advice Warranty': {
            "Bordetallnames": "value1",
            "BORDET1ACN": "value2",
            "BORDET1TRUSTNAME": "value3",
            "MATTERNUMBER": "value4",
            "Guarantor2Fullname": "value5"
        },
        '7. Guarantor Legal Advice': {
            "Bordetallnames": "value1",
            "BORDET1ACN": "value2",
            "BORDET1TRUSTNAME": "value3",
            "MATTERNUMBER": "value4",
            "Guarantor2Fullname": "value5",
            "Guarantor3Fullname": "value6"
        },
        
        '6. National Mortgage Form NSW': {
                                    "MATTERNUMBER": "value1",
                                    "PROPDET1TITREF": "value2",
                                    "PROPDET1LOTDESC": "value3",
                                    "Guarantor1Fullname": "value4",
                                    "Guarantor1ACN": "value5",
                                    "Guarantor2Fullname": "value6"
                                    },
        '6. National Mortgage Form QLD': {
                                    "MATTERNUMBER": "value1",
                                    "PROPDET1TITREF": "value2",
                                    "PROPDET1LOTDESC": "value3",
                                    "Guarantor1Fullname": "value4",
                                    "Guarantor1ACN": "value5",
                                    "Guarantor2Fullname": "value6"
                                    },
        '6. National Mortgage Form SA': {
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
        '6. National Mortgage Form VIC': {
                                    "MATTERNUMBER": "value1",
                                    "PROPDET1TITREF": "value2",
                                    "Guarantor1Fullname": "value3",
                                    "Guarantor1ACN": "value4",
                                    "Guarantor2Fullname": "value5"
                                    },
        '7. Privacy Consent Form BC July 26 2024': {
            "Bordetallnames": "value1",
            "BORDET1ACN": "value2",
            "BORDET1TRUSTNAME": "value3",
            "Guarantor2Fullname": "value4"
        },
        '14. Warranties Fund Mortgaged Property June 23': {
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
        '9. SMSF Financing Agreement': {
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
            "guarantor_4_name": None,
            "Guarantor4Fullname": "value47",
            "guarantor_5_name": None,
            "Guarantor5Fullname": "value49",
            "guarantor_6_name": None,
            "Guarantor6Fullname": "value51"
        },
        '8. Mortgage Side Agreement': { 
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
        '5. Loan Agreement Offer IO': {
                        "Bordetallnames": "value1",
                        "BORDET1ACN": "value2",
                        "bordet1trustname": "value3",
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
                        "annual_facility_fee": "value16",
                        "ValFee": "value17",
                        "settlement_fee": "value18",
                        "documentation_fee": "value19",
                        "trust_deed_review_fee": "value20",
                        "bank_cheque_fee": "value21",
                        "MtgRegFee": "value22",
                        "facilityterm": "value23",
                        "BORDET1FULLNAMESAL": "value24",
                        "BORDET1ADDRESSLINE1": "value25",
                        "BORDET1SUBURB": "value26",
                        "BORDET1STATE": "value27",
                        "BORDET1postcode": "value28",
                        "BORDET1EMAILADDRESS": "value29",
                        "PROPDET1MORTGAGORS": "value30",
                        "GUARANTOR1ADDRESSLINE1": "value31",
                        "GUARANTOR1SUBURB": "value32",
                        "GUARANTOR1STATE": "value33",
                        "GUARANTOR1POSTCODE": "value34",
                        "LOANPURPOSE": "value35",
                        "LVR": "value36",
                        "GUARANTOR2FULLNAME": "value37",
                        "GUARANTOR3FULLNAME": "value38",
                        "advanceamount": "value39",
                        "LOANSPECIALCONDITIONS": "value40",
                        "DefaultInterestRate": "value41",
                        "BORDET1FULLNAME": "value42",
                        "BORDET1TRUSTNAME": "value43",
                        "guarantor_2_name": "value44",
                        "guarantor_3_name": None,
                        "LoanPurpose": "value40"
                        },
    '5. Loan Agreement Offer PI': {
                            "BORDET1FULLNAMESAL": "value1",
                            "BORDET1ACN": "value2",
                            "bordet1trustname": "value3",
                            "BORDET1ADDRESSLINE1": "value4",
                            "BORDET1SUBURB": "value5",
                            "BORDET1STATE": "value6",
                            "BORDET1postcode": "value7",
                            "BORDET1EMAILADDRESS": "value8",
                            "PROPDETALLSECADD": "value9",
                            "LoanNumber": "value10",
                            "LOANPRODUCTTYPE": "value11",
                            "ADVANCEAMOUNT": "value12",
                            "standardinterestrate": "value13",
                            "RepaymentAmount": "value14",
                            "PIRepayments": "value15",
                            "app_fee": "value16",
                            "ValFee": "value17",
                            "lender_protection_fee": "value18",
                            "annual_facility_fee": "value19",
                            "settlement_fee": "value20",
                            "documentation_fee": "value21",
                            "trust_deed_review_fee": "value22",
                            "bank_cheque_fee": "value23",
                            "MtgRegFee": "value24",
                            "facilityterm": "value25",
                            "GUARANTOR1FULLNAME": "value26",
                            "GUARANTOR1ACN": "value27",
                            "GUARANTOR1ADDRESSLINE1": "value28",
                            "GUARANTOR1SUBURB": "value29",
                            "GUARANTOR1STATE": "value30",
                            "GUARANTOR1POSTCODE": "value31",
                            "LVR": "value32",
                            "GUARANTOR2FULLNAME": "value33",
                            "GUARANTOR3FULLNAME": "value34",
                            "advanceamount": "value35",
                            "LOANSPECIALCONDITIONS": "value36",
                            "DefaultInterestRate": "value37",
                            "BORDET1FULLNAME": "value38",
                            "BORDET1TRUSTNAME": "value39",
                            "guarantor_2_name": "value40",
                            "guarantor_3_name": None,
                            "LoanPurpose": "value40"
                            },
    },
    'BC/Refi/Standard': {
        '13. Company Guarantee Warranty (ShareHolders)': { 
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
        '12. Company Guarantee Warranty': {
            "GUARANTOR1FULLNAME": "value1",
            "GUARANTOR1ACN": "value2",
            "Bordetallnames": "value3",
            "BORDET1ACN": "value4",
            "BORDET1TRUSTNAME": "value5",
            "GUARANTOR1TRUSTNAME": "value6",
            "Guarantor2Fullname": "value7"
        },
        '16. Direct Debit Authority': {
            "LOANNUMBER": "value1",
            "Bordetallnames": "value2",
            "BORDET1ACN": "value3",
            "Guarantor2Fullname": "value4"
        },
        '15. Disbursement Direction Authority Refi': {
                                            "Bordetallnames": "value1",
                                            "Propdetallsecadd": "value2",
                                            "ApplicationNumber": "value3",
                                            "LOANNUMBER": "value4",
                                            "Guarantor2Fullname": "value5",
                                            "guarantor_3_name": None,
                                            "Guarantor3Fullname": "value7",
                                            "PROPDETALLSECADD": "value8",
                                            "ADVANCEAMOUNT": "value9",
                                            "app_fee": "value10",
                                            "valuation_fee": "value11",
                                            "settlement_fee": "value12",
                                            "lender_protection_fee": "value13",
                                            "documentation_fee": "value14",
                                            "trust_deed_review_fee": "value15",
                                            "sundry_fee": "value16",
                                            "search_fee": "value17",
                                            "property_state": "value18",
                                            "NSW": "value19",
                                            "VIC": "value20",
                                            "QLD": "value21",
                                            "SA": "value22",
                                            "WA": "value23",
                                            "ACT": "value24",
                                            "TAS": "value25",
                                            "NT": "value26"
                                            },
        '11. Guarantee & Indemnity June 23': {
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
        '10. Guarantee Indemnity Bare Trustee June 23': {
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
        '12. Guarantor Legal Advice Warranty': {
            "Bordetallnames": "value1",
            "BORDET1ACN": "value2",
            "BORDET1TRUSTNAME": "value3",
            "MATTERNUMBER": "value4",
            "Guarantor2Fullname": "value5"
        },
        '7. Guarantor Legal Advice': {
            "Bordetallnames": "value1",
            "BORDET1ACN": "value2",
            "BORDET1TRUSTNAME": "value3",
            "MATTERNUMBER": "value4",
            "Guarantor2Fullname": "value5",
            "Guarantor3Fullname": "value6"
        },
        
        '6. National Mortgage Form NSW': {
                                    "MATTERNUMBER": "value1",
                                    "PROPDET1TITREF": "value2",
                                    "Guarantor1Fullname": "value3",
                                    "Guarantor1ACN": "value4",
                                    "Guarantor2Fullname": "value5"
                                    },
        '6. National Mortgage Form QLD': {
                                        "MATTERNUMBER": "value1",
                                        "PROPDET1TITREF": "value2",
                                        "PROPDET1LOTDESC": "value3",
                                        "Guarantor1Fullname": "value4",
                                        "Guarantor1ACN": "value5",
                                        "Guarantor2Fullname": "value6"
                                        },
        '6. National Mortgage Form SA': {
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
        '6. National Mortgage Form VIC': {
                                    "MATTERNUMBER": "value1",
                                    "PROPDET1TITREF": "value2",
                                    "Guarantor1Fullname": "value3",
                                    "Guarantor1ACN": "value4",
                                    "Guarantor2Fullname": "value5"
                                    },
        '7. Privacy Consent Form BC July 26 2024': {
            "Bordetallnames": "value1",
            "BORDET1ACN": "value2",
            "BORDET1TRUSTNAME": "value3",
            "Guarantor2Fullname": "value4"
        },
        '15. Warranties Fund Mortgaged Property June 23': {
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
        '9. SMSF Financing Agreement': {
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
            "guarantor_4_name": None,
            "Guarantor4Fullname": "value47",
            "guarantor_5_name": None,
            "Guarantor5Fullname": "value49",
            "guarantor_6_name": None,
            "Guarantor6Fullname": "value51"
        },
        '8. Mortgage Side Agreement': { 
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
        '5. Loan Agreement Offer IO': {
                                    "Bordetallnames": "value1",
                                    "BORDET1ACN": "value2",
                                    "bordet1trustname": "value3",
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
                                    "annual_facility_fee": "value16",
                                    "ValFee": "value17",
                                    "settlement_fee": "value18",
                                    "documentation_fee": "value19",
                                    "trust_deed_review_fee": "value20",
                                    "bank_cheque_fee": None,
                                    "MtgRegFee": "value22",
                                    "facilityterm": "value23",
                                    "BORDET1FULLNAMESAL": "value24",
                                    "BORDET1ADDRESSLINE1": "value25",
                                    "BORDET1SUBURB": "value26",
                                    "BORDET1STATE": "value27",
                                    "BORDET1postcode": "value28",
                                    "BORDET1EMAILADDRESS": "value29",
                                    "PROPDET1MORTGAGORS": "value30",
                                    "GUARANTOR1ADDRESSLINE1": "value31",
                                    "GUARANTOR1SUBURB": "value32",
                                    "GUARANTOR1STATE": "value33",
                                    "GUARANTOR1POSTCODE": "value34",
                                    "LOANPURPOSE": "value35",
                                    "LVR": "value36",
                                    "GUARANTOR2FULLNAME": "value37",
                                    "GUARANTOR3FULLNAME": "value38",
                                    "advanceamount": "value39",
                                    "LOANSPECIALCONDITIONS": "value40",
                                    "DefaultInterestRate": "value41",
                                    "BORDET1FULLNAME": "value42",
                                    "BORDET1TRUSTNAME": "value43",
                                    "guarantor_2_name": None,
                                    "guarantor_3_name": None,
                                    "LoanPurpose": "value40"
                                    },
    '5. Loan Agreement Offer PI': {
                                "BORDET1FULLNAMESAL": "value1",
                                "BORDET1ACN": "value2",
                                "bordet1trustname": "value3",
                                "BORDET1ADDRESSLINE1": "value4",
                                "BORDET1SUBURB": "value5",
                                "BORDET1STATE": "value6",
                                "BORDET1postcode": "value7",
                                "BORDET1EMAILADDRESS": "value8",
                                "PROPDETALLSECADD": "value9",
                                "LoanNumber": "value10",
                                "LOANPRODUCTTYPE": "value11",
                                "ADVANCEAMOUNT": "value12",
                                "standardinterestrate": "value13",
                                "RepaymentAmount": "value14",
                                "PIRepayments": "value15",
                                "app_fee": "value16",
                                "ValFee": "value17",
                                "lender_protection_fee": "value18",
                                "annual_facility_fee": "value19",
                                "settlement_fee": "value20",
                                "documentation_fee": "value21",
                                "trust_deed_review_fee": "value22",
                                "bank_cheque_fee": None,
                                "MtgRegFee": "value24",
                                "facilityterm": "value25",
                                "GUARANTOR1FULLNAME": "value26",
                                "GUARANTOR1ACN": "value27",
                                "GUARANTOR1ADDRESSLINE1": "value28",
                                "GUARANTOR1SUBURB": "value29",
                                "GUARANTOR1STATE": "value30",
                                "GUARANTOR1POSTCODE": "value31",
                                "LVR": "value32",
                                "GUARANTOR2FULLNAME": "value33",
                                "GUARANTOR3FULLNAME": "value34",
                                "advanceamount": "value35",
                                "LOANSPECIALCONDITIONS": "value36",
                                "DefaultInterestRate": "value37",
                                "BORDET1FULLNAME": "value38",
                                "BORDET1TRUSTNAME": "value39",
                                "guarantor_2_name": None,
                                "guarantor_3_name": None,
                                "LoanPurpose": "value40"
                                }
    },
    'Source/Purchase/Standard': {
        '11. Direct Debit Request': {
                                "BORDET1FULLNAMESAL": "value1",
                                "BORDET1ACN": "value2",
                                "bordet1trustname": "value3",
                                "BORDET1ADDRESSLINE1": "value4",
                                "BORDET1SUBURB": "value5",
                                "BORDET1STATE": "value6",
                                "BORDET1postcode": "value7",
                                "BORDET1EMAILADDRESS": "value8",
                                "LOANNumber": "value9",
                                "Guarantor2FULLNAME": "value10"
                                },
        '10. Disbursement Direction Authority Source': {
                                                "Propdetallsecadd": "value1",
                                                "Bordetallnames": "value2",
                                                "BORDET1ACN": "value3",
                                                "guarantor_2_name": "value4",
                                                "guarantor_3_name": None,
                                                "GUARANTOR1FULLNAME": "value6",
                                                "GUARANTOR1ACN": "value7",
                                                "directors": [
                                                ],
                                                "loannumber": "value11",
                                                "Lender": "value12",
                                                "lendercharges": [
                                                   
                                                ],
                                                "faocharges": [
                                                   
                                                ],
                                                "balanceavailableforsettlement": "value25",
                                                "advanceamount": "value26",
                                                "BORDET1FULLNAME": "value27"
                                                },
        '7. Guarantee SMSF Holding Trustee': {
                                            "Guarantor1FullName": "value1",
                                            "GUARANTOR1TRUSTNAME": "value2",
                                            "Guarantor1ACN": "value3",
                                            "GUARANTOR1ADDRESSLINE1": "value4",
                                            "GUARANTOR1SUBURB": "value5",
                                            "GUARANTOR1STATE": "value6",
                                            "GUARANTOR1POSTCODE": "value7",
                                            "BORDET1FULLNAMESAL": "value8",
                                            "bordet1trustname": "value9",
                                            "BORDET1ACN": "value10",
                                            "BORDET1ADDRESSLINE1": "value11",
                                            "BORDET1SUBURB": "value12",
                                            "BORDET1STATE": "value13",
                                            "BORDET1POSTCODE": "value14",
                                            "GUARANTOR1FULLNAME": "value15",
                                            "GUARANTOR1ACN": "value16",
                                            "Guarantor2FullName": "value17"
                                        },
        '5. National Mortgage Form ACT Source': {
                                            "MATTERNUMBER": "value1",
                                            "PROPDET1TITREF": "value2",
                                            "GUARANTOR1FULLNAME": "value3",
                                            "GUARANTOR1ACN": "value4",
                                            "GUARANTOR2FULLNAME": "value5"
                                            },
        '5. National Mortgage Form NSW Source': {
            "MATTERNUMBER": "value1",
            "PROPDET1TITREF": "value2",
            "GUARANTOR1FULLNAME": "value3",
            "Guarantor1ACN": "value4",
            "Guarantor2FullName": "value5"
            },
        '5. National Mortgage Form QLD Source': {
                                            "MATTERNUMBER": "value1",
                                            "PROPDET1TITREF": "value2",
                                            "PROPDET1LOTDESC": "value3",
                                            "GUARANTOR1FULLNAME": "value4",
                                            "GUARANTOR1ACN": "value5",
                                            "GUARANTOR2FULLNAME": "value6"
                                            },
        '5. National Mortgage Form SA Source': {
                                            "MATTERNUMBER": "value1",
                                            "PROPDET1TITREF": "value2",
                                            "GUARANTOR1FULLNAME": "value3",
                                            "GUARANTOR1ACN": "value4",
                                            "BORDET1ADDRESSLINE1": "value5",
                                            "BORDET1SUBURB": "value6",
                                            "BORDET1STATE": "value7",
                                            "BORDET1POSTCODE": "value8",
                                            "GUARANTOR2FULLNAME": "value9"
                                            },
        '5. National Mortgage Form VIC Source': {
                                            "MATTERNUMBER": "value1",
                                            "PROPDET1TITREF": "value2",
                                            "GUARANTOR1FULLNAME": "value3",
                                            "Guarantor1ACN": "value4",
                                            "GUARANTOR2FULLNAME": "value5",
                                            "GUAraNTOR1FULLNAME": "value6"
                                            },
        '6. Privacy Policy Collection Notice': {
                                            "Bordetallnames": "value1",
                                            "BORDET1ACN": "value2",
                                            "bordet1trustname": "value3",
                                            "Guarantor2FullName": "value4",
                                            "directors": [
                                                {
                                                "GUARANTORNAME": "value5"
                                                },
                                                {
                                                "GUARANTORNAME": "value6"
                                                },
                                                {
                                                "GUARANTORNAME": "value7"
                                                }
                                            ]
                                            },
        '9. Purchase Acknowledgement Legal Financial Advice': {
                                                            "Bordetallnames": "value1",
                                                            "BORDET1ACN": "value2",
                                                            "LOANNNUMBER": "value3",
                                                            "directors": [
                                                                {
                                                                "GUARANTORNAME": "value4"
                                                                },
                                                                {
                                                                "GUARANTORNAME": "value5"
                                                                },
                                                                {
                                                                "GUARANTORNAME": "value6"
                                                                }
                                                            ]
                                                            },
        '8. SMSF Member Guarantee':{
                                "directors": [
                                    {
                                    "GUARANTORNAME": "value1",
                                    "GUARANTORADDRESSLINE1": "value2",
                                    "GUARANTORSUBURB": "value3",
                                    "GUARANTORSTATE": "value4",
                                    "GUARANTORPOSTCODE": "value5"
                                    },
                                    {
                                    "GUARANTORNAME": "value6",
                                    "GUARANTORADDRESSLINE1": "value7",
                                    "GUARANTORSUBURB": "value8",
                                    "GUARANTORSTATE": "value9",
                                    "GUARANTORPOSTCODE": "value10"
                                    },
                                    {
                                    "GUARANTORNAME": "value11",
                                    "GUARANTORADDRESSLINE1": "value12",
                                    "GUARANTORSUBURB": "value13",
                                    "GUARANTORSTATE": "value14",
                                    "GUARANTORPOSTCODE": "value15"
                                    }
                                ],
                                "BORDET1FULLNAMESAL": "value16",
                                "bordet1trustname": "value17",
                                "BORDET1ACN": "value18",
                                "BORDET1ADDRESSLINE1": "value19",
                                "BORDET1SUBURB": "value20",
                                "BORDET1STATE": "value21",
                                "BORDET1POSTCODE": "value22",
                                "Guarantor1Fullname": "value23",
                                "GUARANTOR1TRUSTNAME": "value24",
                                "GUARANTOR1ACN": "value25",
                                "GUARANTOR1ADDRESSLINE1": "value26",
                                "GUARANTOR1SUBURB": "value27",
                                "GUARANTOR1STATE": "value28",
                                "GUARANTOR1POSTCODE": "value29",
                                "GUARANTOR2FULLNAME": "value30",
                                "guarantor_3_name": "value31",
                                "GUARANTOR3FULLNAME": "value32",
                                "guarantor_4_name": "value33",
                                "GUARANTOR4FULLNAME": "value34",
                                "guarantor_5_name": "value35",
                                "GUARANTOR5FULLNAME": "value36",
                                "guarantor_6_name": "value37",
                                "GUARANTOR6FULLNAME": "value38"
                                },
        '1. Credit Guide': {},
        '2. Loan General Terms': {},
        '3. Mortgage Common Provisions': {},
        '12. Legal Advice Declaration NSW Guarantor': {
            "plinitials": "value1",
            "matternumber": "value2",
            "Guarantor2FULLNAME": "value3",
            "GUARANTOR2ADDRESSLINE1": "value4",
            "GUARANTOR2SUBURB": "value5",
            "GUARANTOR2STATE": "value6",
            "GUARANTOR2POSTCODE": "value7",
            "BORDET1FULLNAMESAL": "value8",
            "BORDET1ACN": "value9",
            "bordet1trustname": "value10",
            "Propdetallsecadd": "value11"
            }

        
    },
    'Source/Purchase/LoanAgreement': {
        '4. Loan Agreement SMSF IO': {
                                "Bordetallnames": "value1",
                                "BORDET1ACN": "value2",
                                "BORDET1TRUSTNAME": "value3",
                                "BORDET1ADDRESSLINE1": "value4",
                                "BORDET1SUBURB": "value5",
                                "BORDET1STATE": "value6",
                                "BORDET1postcode": "value7",
                                "LOANNumber": "value8",
                                "ADVANCEAMOUNT": "value9",
                                "standardinterestrate": "value10",
                                "facilityterm": "value11",
                                "PIRepayments": "value12",
                                "IOTerm": "value13",
                                "RepaymentAmount": "value14",
                                "number_of_repayments": "value15",
                                "charges": [
                                    {
                                    "charge_name": "value16",
                                    "charge_amount": "value17"
                                    },
                                    {
                                    "charge_name": "value18",
                                    "charge_amount": "value19"
                                    },
                                    {
                                    "charge_name": "value20",
                                    "charge_amount": "value21"
                                    }
                                ],
                                "mortgage_registration_fee": "value22",
                                "security_duty": None,
                                "LMI_Fee": None,
                                "annual_facility_fee": "value25",
                                "monthly_facility_fee": None,
                                "LoanPurposeDetail": "value27",
                                "DefaultInterestRate": "value28",
                                "LOANSPECIALCONDITIONS": "value29",
                                "PROPDET1MORTGAGORS": "value30",
                                "PROPDETALLSECADD": "value31",
                                "PROPDET1TITREF": "value32",
                                "GUARANTOR1FULLNAME": "value33",
                                "GUARANTOR1ACN": "value34",
                                "Guarantor1Fullname": "value35",
                                "GUARANTOR1ADDRESSLINE1": "value36",
                                "GUARANTOR1SUBURB": "value37",
                                "GUARANTOR1STATE": "value38",
                                "GUARANTOR1POSTCODE": "value39",
                                "directors": [
                                    {
                                    "GUARANTORNAME": "value40",
                                    "GUARANTORADDRESSLINE1": "value41",
                                    "GUARANTORSUBURB": "value42",
                                    "GUARANTORSTATE": "value43",
                                    "GUARANTORPOSTCODE": "value44"
                                    },
                                    {
                                    "GUARANTORNAME": "value45",
                                    "GUARANTORADDRESSLINE1": "value46",
                                    "GUARANTORSUBURB": "value47",
                                    "GUARANTORSTATE": "value48",
                                    "GUARANTORPOSTCODE": "value49"
                                    },
                                    {
                                    "GUARANTORNAME": "value50",
                                    "GUARANTORADDRESSLINE1": "value51",
                                    "GUARANTORSUBURB": "value52",
                                    "GUARANTORSTATE": "value53",
                                    "GUARANTORPOSTCODE": "value54"
                                    }
                                ],
                                "BORDET1FULLNAMESAL": "value55",
                                "BORDET1TRUSTDATE": "value56",
                                "GUARANTOR1TRUSTNAME": "value57",
                                "GUARANTOR1TRUSTDATE": "value58",
                                "guarantor_2_name": "value59",
                                "guarantor_3_name": None
                                },
        '4. Loan Agreement SMSF PI': {
                                    "Bordetallnames": "value1",
                                    "BORDET1ACN": "value2",
                                    "BORDET1TRUSTNAME": "value3",
                                    "BORDET1ADDRESSLINE1": "value4",
                                    "BORDET1SUBURB": "value5",
                                    "BORDET1STATE": "value6",
                                    "BORDET1postcode": "value7",
                                    "LOANNumber": "value8",
                                    "ADVANCEAMOUNT": "value9",
                                    "standardinterestrate": "value10",
                                    "facilityterm": "value11",
                                    "PIRepayments": "value12",
                                    "RepaymentAmount": "value13",
                                    "number_of_repayments": "value14",
                                    "charges": [
                                        {
                                        "charge_name": "value15",
                                        "charge_amount": "value16"
                                        },
                                        {
                                        "charge_name": "value17",
                                        "charge_amount": "value18"
                                        },
                                        {
                                        "charge_name": "value19",
                                        "charge_amount": "value20"
                                        }
                                    ],
                                    "mortgage_registration_fee": "value21",
                                    "security_duty": "value22",
                                    "LMI_Fee": "value23",
                                    "annual_facility_fee": "value24",
                                    "monthly_facility_fee": "value25",
                                    "LoanPurposeDetail": "value26",
                                    "DefaultInterestRate": "value27",
                                    "LOANSPECIALCONDITIONS": "value28",
                                    "PROPDET1MORTGAGORS": "value29",
                                    "PROPDETALLSECADD": "value30",
                                    "PROPDET1TITREF": "value31",
                                    "GUARANTOR1FULLNAME": "value32",
                                    "GUARANTOR1ACN": "value33",
                                    "Guarantor1Fullname": "value34",
                                    "GUARANTOR1ADDRESSLINE1": "value35",
                                    "GUARANTOR1SUBURB": "value36",
                                    "GUARANTOR1STATE": "value37",
                                    "GUARANTOR1POSTCODE": "value38",
                                    "directors": [
                                        {
                                        "GUARANTORNAME": "value39",
                                        "GUARANTORADDRESSLINE1": "value40",
                                        "GUARANTORSUBURB": "value41",
                                        "GUARANTORSTATE": "value42",
                                        "GUARANTORPOSTCODE": "value43"
                                        },
                                        {
                                        "GUARANTORNAME": "value44",
                                        "GUARANTORADDRESSLINE1": "value45",
                                        "GUARANTORSUBURB": "value46",
                                        "GUARANTORSTATE": "value47",
                                        "GUARANTORPOSTCODE": "value48"
                                        },
                                        {
                                        "GUARANTORNAME": "value49",
                                        "GUARANTORADDRESSLINE1": "value50",
                                        "GUARANTORSUBURB": "value51",
                                        "GUARANTORSTATE": "value52",
                                        "GUARANTORPOSTCODE": "value53"
                                        }
                                    ],
                                    "BORDET1FULLNAMESAL": "value54",
                                    "BORDET1TRUSTDATE": "value55",
                                    "GUARANTOR1TRUSTNAME": "value56",
                                    "GUARANTOR1TRUSTDATE": "value57",
                                    "guarantor_2_name": "value58",
                                    "guarantor_3_name": "value59"
                                    },
    },
    "Source/Refi/Standard": {
        '11. Direct Debit Request': {
                                "BORDET1FULLNAMESAL": "value1",
                                "BORDET1ACN": "value2",
                                "bordet1trustname": "value3",
                                "BORDET1ADDRESSLINE1": "value4",
                                "BORDET1SUBURB": "value5",
                                "BORDET1STATE": "value6",
                                "BORDET1postcode": "value7",
                                "BORDET1EMAILADDRESS": "value8",
                                "LOANNumber": "value9",
                                "Guarantor2FULLNAME": "value10"
                                },
        '10. Disbursement Direction Authority Source': {
                                                "Propdetallsecadd": "value1",
                                                "Bordetallnames": "value2",
                                                "BORDET1ACN": "value3",
                                                "guarantor_2_name": "value4",
                                                "guarantor_3_name": None,
                                                "GUARANTOR1FULLNAME": "value6",
                                                "GUARANTOR1ACN": "value7",
                                                "directors": [
                                                ],
                                                "loannumber": "value11",
                                                "Lender": "value12",
                                                "lendercharges": [
                                                   
                                                ],
                                                "faocharges": [
                                                   
                                                ],
                                                "balanceavailableforsettlement": "value25",
                                                "advanceamount": "value26",
                                                "BORDET1FULLNAME": "value27"
                                                },
        '7. Guarantee SMSF Holding Trustee': {
                                            "Guarantor1Fullname": "value1",
                                            "GUARANTOR1TRUSTNAME": "value2",
                                            "Guarantor1ACN": "value3",
                                            "GUARANTOR1ADDRESSLINE1": "value4",
                                            "GUARANTOR1SUBURB": "value5",
                                            "GUARANTOR1STATE": "value6",
                                            "GUARANTOR1POSTCODE": "value7",
                                            "BORDET1FULLNAMESAL": "value8",
                                            "bordet1trustname": "value9",
                                            "BORDET1ACN": "value10",
                                            "BORDET1ADDRESSLINE1": "value11",
                                            "BORDET1SUBURB": "value12",
                                            "BORDET1STATE": "value13",
                                            "BORDET1POSTCODE": "value14",
                                            "GUARANTOR1FULLNAME": "value15",
                                            "GUARANTOR1ACN": "value16",
                                            "Guarantor2FullName": "value17"
                                        },
            '5. National Mortgage Form ACT Source':{
                                                "MATTERNUMBER": "value1",
                                                "PROPDET1TITREF": "value2",
                                                "GUARANTOR1FULLNAME": "value3",
                                                "GUARANTOR1ACN": "value4",
                                                "GUARANTOR2FULLNAME": "value5"
                                                },
        '5. National Mortgage Form NSW Source': {
                                            "MATTERNUMBER": "value1",
                                            "PROPDET1TITREF": "value2",
                                            "GUARANTOR1FULLNAME": "value3",
                                            "GUARANTOR1ACN": "value4",
                                            "GUARANTOR2FULLNAME": "value5"
                                            },
        '5. National Mortgage Form QLD Source': {
                                            "MATTERNUMBER": "value1",
                                            "PROPDET1TITREF": "value2",
                                            "PROPDET1LOTDESC": "value3",
                                            "GUARANTOR1FULLNAME": "value4",
                                            "GUARANTOR1ACN": "value5",
                                            "GUARANTOR2FULLNAME": "value6"
                                            },   
        '5. National Mortgage Form SA Source': {
                                            "MATTERNUMBER": "value1",
                                            "PROPDET1TITREF": "value2",
                                            "GUARANTOR1FULLNAME": "value3",
                                            "GUARANTOR1ACN": "value4",
                                            "BORDET1ADDRESSLINE1": "value5",
                                            "BORDET1SUBURB": "value6",
                                            "BORDET1STATE": "value7",
                                            "BORDET1POSTCODE": "value8",
                                            "GUARANTOR2FULLNAME": "value9"
                                            },
        '5. National Mortgage Form VIC Source': {
                                            "MATTERNUMBER": "value1",
                                            "PROPDET1TITREF": "value2",
                                            "GUARANTOR1FULLNAME": "value3",
                                            "Guarantor1ACN": "value4",
                                            "GUARANTOR2FULLNAME": "value5",
                                            "GUAraNTOR1FULLNAME": "value6"
                                            },
        '6. Privacy Policy Collection Notice': {
                                            "Bordetallnames": "value1",
                                            "BORDET1ACN": "value2",
                                            "bordet1trustname": "value3",
                                            "Guarantor2FullName": "value4",
                                            "directors": [
                                                {
                                                "GUARANTORNAME": "value5"
                                                },
                                                {
                                                "GUARANTORNAME": "value6"
                                                },
                                                {
                                                "GUARANTORNAME": "value7"
                                                }
                                            ]
                                            },
        '9. Purchase Acknowledgement Legal Financial Advice': {
                                                            "Bordetallnames": "value1",
                                                            "BORDET1ACN": "value2",
                                                            "LOANNNUMBER": "value3",
                                                            "directors": [
                                                                {
                                                                "GUARANTORNAME": "value4"
                                                                },
                                                                {
                                                                "GUARANTORNAME": "value5"
                                                                },
                                                                {
                                                                "GUARANTORNAME": "value6"
                                                                }
                                                            ]
                                                            },
        '8. SMSF Member Guarantee': {
                                "directors": [
                                    {
                                    "GuarantorFullName": "value1",
                                    "GUARANTORADDRESSLINE1": "value2",
                                    "GUARANTORSUBURB": "value3",
                                    "GUARANTORSTATE": "value4",
                                    "GUARANTORPOSTCODE": "value5"
                                    },
                                    {
                                    "GuarantorFullName": "value6",
                                    "GUARANTORADDRESSLINE1": "value7",
                                    "GUARANTORSUBURB": "value8",
                                    "GUARANTORSTATE": "value9",
                                    "GUARANTORPOSTCODE": "value10"
                                    },
                                    {
                                    "GuarantorFullName": "value11",
                                    "GUARANTORADDRESSLINE1": "value12",
                                    "GUARANTORSUBURB": "value13",
                                    "GUARANTORSTATE": "value14",
                                    "GUARANTORPOSTCODE": "value15"
                                    }
                                ],
                                "BORDET1FULLNAMESAL": "value16",
                                "bordet1trustname": "value17",
                                "BORDET1ACN": "value18",
                                "BORDET1ADDRESSLINE1": "value19",
                                "BORDET1SUBURB": "value20",
                                "BORDET1STATE": "value21",
                                "BORDET1POSTCODE": "value22",
                                "Guarantor1FullName": "value23",
                                "GUARANTOR1TRUSTNAME": "value24",
                                "Guarantor1ACN": "value25",
                                "GUARANTOR1ADDRESSLINE1": "value26",
                                "GUARANTOR1SUBURB": "value27",
                                "GUARANTOR1STATE": "value28",
                                "GUARANTOR1POSTCODE": "value29",
                                "GUARANTOR2FULLNAME": "value30",
                                "guarantor_3_name": None,
                                "GUARANTOR3FULLNAME": "value32",
                                "guarantor_4_name": None,
                                "GUARANTOR4FULLNAME": "value34",
                                "guarantor_5_name": None,
                                "GUARANTOR5FULLNAME": "value36"
                                },
        '1. Credit Guide': {},
        '2. Loan General Terms': {},
        '3. Mortgage Common Provisions': {},
        '12. Legal Advice Declaration NSW Guarantor': {
            "plinitials": "value1",
            "matternumber": "value2",
            "Guarantor2FULLNAME": "value3",
            "GUARANTOR2ADDRESSLINE1": "value4",
            "GUARANTOR2SUBURB": "value5",
            "GUARANTOR2STATE": "value6",
            "GUARANTOR2POSTCODE": "value7",
            "BORDET1FULLNAMESAL": "value8",
            "BORDET1ACN": "value9",
            "bordet1trustname": "value10",
            "Propdetallsecadd": "value11"
            }

    },
    "Source/Refi/LoanAgreement": {
                '4. Loan Agreement SMSF IO': {
                                        "Bordetallnames": "value1",
                                        "BORDET1ACN": "value2",
                                        "BORDET1TRUSTNAME": "value3",
                                        "BORDET1ADDRESSLINE1": "value4",
                                        "BORDET1SUBURB": "value5",
                                        "BORDET1STATE": "value6",
                                        "BORDET1postcode": "value7",
                                        "LOANNumber": "value8",
                                        "ADVANCEAMOUNT": "value9",
                                        "standardinterestrate": "value10",
                                        "facilityterm": "value11",
                                        "PIRepayments": "value12",
                                        "IOTerm": "value13",
                                        "RepaymentAmount": "value14",
                                        "number_of_repayments": "value15",
                                        "charges": [
                                            {
                                            "charge_name": "value16",
                                            "charge_amount": "value17"
                                            },
                                            {
                                            "charge_name": "value18",
                                            "charge_amount": "value19"
                                            },
                                            {
                                            "charge_name": "value20",
                                            "charge_amount": "value21"
                                            }
                                        ],
                                        "mortgage_registration_fee": "value22",
                                        "security_duty": None,
                                        "LMI_Fee": None,
                                        "annual_facility_fee": "value25",
                                        "monthly_facility_fee": None,
                                        "LoanPurposeDetail": "value27",
                                        "DefaultInterestRate": "value28",
                                        "LOANSPECIALCONDITIONS": "value29",
                                        "PROPDET1MORTGAGORS": "value30",
                                        "PROPDETALLSECADD": "value31",
                                        "PROPDET1TITREF": "value32",
                                        "GUARANTOR1FULLNAME": "value33",
                                        "GUARANTOR1ACN": "value34",
                                        "Guarantor1Fullname": "value35",
                                        "GUARANTOR1ADDRESSLINE1": "value36",
                                        "GUARANTOR1SUBURB": "value37",
                                        "GUARANTOR1STATE": "value38",
                                        "GUARANTOR1POSTCODE": "value39",
                                        "directors": [
                                            {
                                            "GUARANTORNAME": "value40",
                                            "GUARANTORADDRESSLINE1": "value41",
                                            "GUARANTORSUBURB": "value42",
                                            "GUARANTORSTATE": "value43",
                                            "GUARANTORPOSTCODE": "value44"
                                            },
                                            {
                                            "GUARANTORNAME": "value45",
                                            "GUARANTORADDRESSLINE1": "value46",
                                            "GUARANTORSUBURB": "value47",
                                            "GUARANTORSTATE": "value48",
                                            "GUARANTORPOSTCODE": "value49"
                                            },
                                            {
                                            "GUARANTORNAME": "value50",
                                            "GUARANTORADDRESSLINE1": "value51",
                                            "GUARANTORSUBURB": "value52",
                                            "GUARANTORSTATE": "value53",
                                            "GUARANTORPOSTCODE": "value54"
                                            }
                                        ],
                                        "BORDET1FULLNAMESAL": "value55",
                                        "BORDET1TRUSTDATE": "value56",
                                        "GUARANTOR1TRUSTNAME": "value57",
                                        "GUARANTOR1TRUSTDATE": "value58",
                                        "guarantor_2_name": "value59",
                                        "guarantor_3_name": None
                                        },
        '4. Loan Agreement SMSF PI': {
                                    "Bordetallnames": "value1",
                                    "BORDET1ACN": "value2",
                                    "BORDET1TRUSTNAME": "value3",
                                    "BORDET1ADDRESSLINE1": "value4",
                                    "BORDET1SUBURB": "value5",
                                    "BORDET1STATE": "value6",
                                    "BORDET1postcode": "value7",
                                    "LOANNumber": "value8",
                                    "ADVANCEAMOUNT": "value9",
                                    "standardinterestrate": "value10",
                                    "facilityterm": "value11",
                                    "PIRepayments": "value12",
                                    "RepaymentAmount": "value13",
                                    "number_of_repayments": "value14",
                                    "charges": [
                                        {
                                        "charge_name": "value15",
                                        "charge_amount": "value16"
                                        },
                                        {
                                        "charge_name": "value17",
                                        "charge_amount": "value18"
                                        },
                                        {
                                        "charge_name": "value19",
                                        "charge_amount": "value20"
                                        }
                                    ],
                                    "mortgage_registration_fee": "value21",
                                    "security_duty": None,
                                    "LMI_Fee": None,
                                    "annual_facility_fee": None,
                                    "monthly_facility_fee": None,
                                    "LoanPurposeDetail": "value26",
                                    "DefaultInterestRate": "value27",
                                    "LOANSPECIALCONDITIONS": "value28",
                                    "PROPDET1MORTGAGORS": "value29",
                                    "PROPDETALLSECADD": "value30",
                                    "PROPDET1TITREF": "value31",
                                    "GUARANTOR1FULLNAME": "value32",
                                    "GUARANTOR1ACN": "value33",
                                    "Guarantor1Fullname": "value34",
                                    "GUARANTOR1ADDRESSLINE1": "value35",
                                    "GUARANTOR1SUBURB": "value36",
                                    "GUARANTOR1STATE": "value37",
                                    "GUARANTOR1POSTCODE": "value38",
                                    "directors": [
                                        {
                                        "guarantor_name": "value39",
                                        "guarantor_address": "value40",
                                        "guarantor_suburb": "value41",
                                        "guarantor_state": "value42",
                                        "guarantor_postcode": "value43"
                                        },
                                        {
                                        "guarantor_name": "value44",
                                        "guarantor_address": "value45",
                                        "guarantor_suburb": "value46",
                                        "guarantor_state": "value47",
                                        "guarantor_postcode": "value48"
                                        },
                                        {
                                        "guarantor_name": "value49",
                                        "guarantor_address": "value50",
                                        "guarantor_suburb": "value51",
                                        "guarantor_state": "value52",
                                        "guarantor_postcode": "value53"
                                        }
                                    ],
                                    "BORDET1FULLNAMESAL": "value54",
                                    "BORDET1TRUSTDATE": "value55",
                                    "GUARANTOR1TRUSTNAME": "value56",
                                    "GUARANTOR1TRUSTDATE": "value57",
                                    "guarantor_2_name": "value58",
                                    "guarantor_3_name": None
                                    },
    }
}

docmosisDirectories = {
    '12. Company Guarantee Warranty': 'SMSF/Purchase/BC/12. Company Guarantee Warranty.docx',
    '13. Company Guarantee Warranty (ShareHolders)': 'SMSF/Purchase/BC/13. Company Guarantee Warranty (ShareHolders).docx',
    '16. Direct Debit Authority': 'SMSF/Purchase/BC/16. Direct Debit Authority.docx',
    '15. Disbursement Direction Authority Purchase': 'SMSF/Purchase/BC/15. Disbursement Direction Authority Purchase.docx',
    '11. Guarantee & Indemnity June 23': 'SMSF/Purchase/BC/11. Guarantee & Indemnity June 23.docx',
    '10. Guarantee Indemnity Bare Trustee June 23': 'SMSF/Purchase/BC/10. Guarantee Indemnity Bare Trustee June 23.docx',
    '12. Guarantor Legal Advice Warranty': 'SMSF/Purchase/BC/12. Guarantor Legal Advice Warranty.docx',
    '7. Guarantor Legal Advice': 'SMSF/Purchase/BC/7. Guarantor Legal Advice.docx',
    '7. Privacy Consent Form BC July 26 2024': 'SMSF/Purchase/BC/7. Privacy Consent Form BC July 26 2024.docx',
    '14. Warranties Fund Mortgaged Property June 23': 'SMSF/Purchase/BC/14. Warranties Fund Mortgaged Property June 23.docx',
    '0. Borrowers Checklist SMSF Purchase Wet sign Mortgage': 'SMSF/Purchase/BC/WetSign/0. Borrowers Checklist SMSF Purchase Wet sign Mortgage.docx',
    '0. Borrowers Checklist SMSF NSW Purchase': 'SMSF/Purchase/BC/NSW/0. Borrowers Checklist SMSF NSW Purchase.docx',
    '0. Borrowers Checklist SMSF Purchase Hybrid': 'SMSF/Purchase/BC/0. Borrowers Checklist SMSF Purchase Hybrid.docx',
    '6. National Mortgage Form NSW': 'SMSF/Purchase/BC/6. National Mortgage Form NSW.docx',
    '6. National Mortgage Form QLD': 'SMSF/Purchase/BC/6. National Mortgage Form QLD.docx',
    '6. National Mortgage Form SA': 'SMSF/Purchase/BC/6. National Mortgage Form SA.docx',
    '6. National Mortgage Form VIC': 'SMSF/Purchase/BC/6. National Mortgage Form VIC.docx',
    '5. Loan Agreement Offer IO': 'SMSF/Purchase/BC/5. Loan Agreement Offer IO.docx',
    '5. Loan Agreement Offer PI': 'SMSF/Purchase/BC/5. Loan Agreement Offer PI.docx',
    '1. Credit Guide': 'SMSF/Purchase/BC/1. Credit Guide.docx',
    '2. Loan Agreement - Terms and Conditions': 'SMSF/Purchase/BC/2. Loan Agreement - Terms and Conditions.docx',
    '3. Mortgage Common Provisions': 'SMSF/Purchase/BC/3. Mortgage Common Provisions.docx',
    '4. Guarantee Information Statement': 'SMSF/Purchase/BC/4. Guarantee Information Statement.docx',
    '9. SMSF Financing Agreement': 'SMSF/Purchase/BC/9. SMSF Financing Agreement.docx',
    '8. Mortgage Side Agreement': 'SMSF/Purchase/BC/8. Mortgage Side Agreement.docx',
    '0. Borrowers Checklist SMSF Refi (no ILA)': 'SMSF/Refi/BC/0. Borrowers Checklist SMSF Refi (no ILA).docx',
    '0. Borrowers Checklist SMSF Refi Hybrid (wet sign mortgage)': 'SMSF/Refi/BC/WetSign/0. Borrowers Checklist SMSF Refi Hybrid (wet sign mortgage).docx',
    '15. Disbursement Direction Authority Refi': 'SMSF/Refi/BC/16. Disbursement Direction Authority Refi.docx',
    '1. Credit Guide': 'SMSF/Purchase/Source/1. Credit Guide.docx',
    '2. Loan General Terms': 'SMSF/Purchase/Source/2. Loan General Terms.docx',
    '3. Mortgage Common Provisions': "SMSF/Purchase/Source/3. Mortgage Common Provisions.docx",
    '0. Borrowers Checklist SMSF Purchase': 'SMSF/Purchase/Source/0. Borrowers Checklist SMSF Purchase.docx',
    '11. Direct Debit Request': 'SMSF/Purchase/Source/11. Direct Debit Request.docx',
    '10. Disbursement Direction Authority Source': 'SMSF/Purchase/Source/10. Disbursement Direction Authority Source.docx',
    '7. Guarantee SMSF Holding Trustee': 'SMSF/Purchase/Source/7. Guarantee SMSF Holding Trustee.docx',
    '12. Legal Advice Declaration NSW Guarantor': 'SMSF/Purchase/Source/12. Legal Advice Declaration NSW Guarantor.docx',
    '4. Loan Agreement SMSF PI': 'SMSF/Purchase/Source/4. Loan Agreement SMSF PI.docx',
    '5. National Mortgage Form ACT Source': 'SMSF/Purchase/Source/5. National Mortgage Form ACT Source.docx',
    '5. National Mortgage Form NSW Source': 'SMSF/Purchase/Source/5. National Mortgage Form NSW Source.docx',
    '5. National Mortgage Form QLD Source': 'SMSF/Purchase/Source/5. National Mortgage Form QLD Source.docx',
    '5. National Mortgage Form SA Source': 'SMSF/Purchase/Source/5. National Mortgage Form SA Source.docx',
    '5. National Mortgage Form VIC Source': 'SMSF/Purchase/Source/5. National Mortgage Form VIC Source.docx',
    '4. Loan Agreement SMSF IO': 'SMSF/Purchase/Source/4. Loan Agreement SMSF IO.docx',
    '8. SMSF Member Guarantee': 'SMSF/Purchase/Source/8. SMSF Member Guarantee.docx',
    '12. Solicitors Certificate Guarantor': 'SMSF/Purchase/Source/12. Solicitors Certificate Guarantor.docx',
    '0. Borrowers Checklist SMSF Wetsign': 'SMSF/Purchase/Source/WetSign/0. Borrowers Checklist SMSF Wetsign.docx',
    '0. Borrowers Checklist SMSF NSW': 'SMSF/Purchase/Source/NSW/0. Borrowers Checklist SMSF NSW.docx',
    '6. Privacy Policy Collection Notice': 'SMSF/Purchase/Source/6. Privacy Policy Collection Notice.docx',
    '9. Purchase Acknowledgement Legal Financial Advice': 'SMSF/Purchase/Source/9. Purchase Acknowledgement Legal Financial Advice.docx',
    '0. Borrowers Checklist SMSF Refi Hybrid (wet sign mortgage)': "SMSF/Refi/Source/WetSign/0. Borrowers Checklist SMSF Refi Hybrid (wet sign mortgage).docx",
    '0. Borrowers Checklist SMSF Refi (no ILA)': 'SMSF/Refi/Source/0. Borrowers Checklist SMSF Refi (no ILA).docx'
}


fileDirectory = {
    'SMSF/Purchase/BC/' : {
        'Borrowers-Checklist': {
            'Wetsign': '0. Borrowers Checklist SMSF Purchase Wet sign Mortgage',
            'NSW': '0. Borrowers Checklist SMSF NSW Purchase',
            'Non-Wetsign-NSW': '0. Borrowers Checklist SMSF Purchase Hybrid',
        },
        'Standard': [
            '12. Company Guarantee Warranty',
            '13. Company Guarantee Warranty (ShareHolders)',
            '16. Direct Debit Authority',
            '15. Disbursement Direction Authority Purchase',
            '11. Guarantee & Indemnity June 23',
            '10. Guarantee Indemnity Bare Trustee June 23',
            '12. Guarantor Legal Advice Warranty',
            '7. Guarantor Legal Advice',
            '7. Privacy Consent Form BC July 26 2024',
            '14. Warranties Fund Mortgaged Property June 23',
            '1. Credit Guide',
            '2. Loan Agreement - Terms and Conditions',
            '3. Mortgage Common Provisions',
            '4. Guarantee Information Statement',
            '9. SMSF Financing Agreement',
            '8. Mortgage Side Agreement'
        ],
        'Loan-Agreement': {
            'IO': '5. Loan Agreement Offer IO',
            'PI': '5. Loan Agreement Offer PI'
        },
        'NSW-Specific': [
            '6. National Mortgage Form NSW'
        ],
        'QLD-Specific': [
            '6. National Mortgage Form QLD'
        ],
        'SA-Specific': [
            '6. National Mortgage Form SA'
        ],
        'VIC-Specific': [
            '6. National Mortgage Form VIC'
        ]
        
    },
    'SMSF/Refi/BC/': {
      'Borrowers-Checklist': {
            'Wetsign': '0. Borrowers Checklist SMSF Refi Hybrid (wet sign mortgage)',
            'Non-Wetsign-NSW': '0. Borrowers Checklist SMSF Refi (no ILA)',
        },
        'Standard': [
            '12. Company Guarantee Warranty',
            '13. Company Guarantee Warranty (ShareHolders)',
            '16. Direct Debit Authority',
            '15. Disbursement Direction Authority Refi',
            '11. Guarantee & Indemnity June 23',
            '10. Guarantee Indemnity Bare Trustee June 23',
            '12. Guarantor Legal Advice Warranty',
            '7. Guarantor Legal Advice',
            '7. Privacy Consent Form BC July 26 2024',
            '14. Warranties Fund Mortgaged Property June 23',
            '1. Credit Guide',
            '2. Loan Agreement - Terms and Conditions',
            '3. Mortgage Common Provisions',
            '4. Guarantee Information Statement',
            '9. SMSF Financing Agreement',
            '8. Mortgage Side Agreement'
        ],
        'Loan-Agreement': {
            'IO': '5. Loan Agreement Offer IO',
            'PI': '5. Loan Agreement Offer PI'
        },
        'NSW-Specific': [
            '6. National Mortgage Form NSW'
        ],
        'QLD-Specific': [
            '6. National Mortgage Form QLD'
        ],
        'SA-Specific': [
            '6. National Mortgage Form SA'
        ],
        'VIC-Specific': [
            '6. National Mortgage Form VIC'
        ]
    },
    'SMSF/Purchase/Source/': {
        'Borrowers-Checklist': {
            'Wetsign': '0. Borrowers Checklist SMSF Wetsign',
            'NSW': '0. Borrowers Checklist SMSF NSW',
            'Non-Wetsign-NSW': '0. Borrowers Checklist SMSF Purchase',
        },
        'Standard': [
            '1. Credit Guide',
            '2. Loan General Terms',
            '3. Mortgage Common Provisions',
            '11. Direct Debit Request',
            '10. Disbursement Direction Authority Source',
            '7. Guarantee SMSF Holding Trustee',
            '6. Privacy Policy Collection Notice',
            '9. Purchase Acknowledgement Legal Financial Advice',
            '8. SMSF Member Guarantee',
            '12. Solicitors Certificate Guarantor',
            
        ],
        'Loan-Agreement': {
            'IO': '4. Loan Agreement SMSF IO',
            'PI': '4. Loan Agreement SMSF PI'
        },
        'NSW-Specific': [
            '5. National Mortgage Form NSW Source',
            '12. Legal Advice Declaration NSW Guarantor',
        ],
        'QLD-Specific': [
            '5. National Mortgage Form QLD Source'
        ],
        'SA-Specific': [
            '5. National Mortgage Form SA Source'
        ],
        'VIC-Specific': [
            '5. National Mortgage Form VIC Source'
        ],
        'ACT-Specific': [
            '5. National Mortgage Form ACT Source'
        ]
    },
    'SMSF/Refi/Source/': {
        'Borrowers-Checklist': {
            'Wetsign': '0. Borrowers Checklist SMSF Refi Hybrid (wet sign mortgage)',
            'Non-Wetsign-NSW': '0. Borrowers Checklist SMSF Refi (no ILA)',
        },
        'Standard': [
            '1. Credit Guide',
            '2. Loan General Terms',
            '3. Mortgage Common Provisions',
            '11. Direct Debit Request',
            '10. Disbursement Direction Authority Source',
            '7. Guarantee SMSF Holding Trustee',
            '6. Privacy Policy Collection Notice',
            '9. Purchase Acknowledgement Legal Financial Advice',
            '8. SMSF Member Guarantee',
            '12. Solicitors Certificate Guarantor',
            
        ],
        'Loan-Agreement': {
            'IO': '4. Loan Agreement SMSF IO',
            'PI': '4. Loan Agreement SMSF PI'
        },
        'NSW-Specific': [
            '5. National Mortgage Form NSW Source',
            '12. Legal Advice Declaration NSW Guarantor',
        ],
        'QLD-Specific': [
            '5. National Mortgage Form QLD Source'
        ],
        'SA-Specific': [
            '5. National Mortgage Form SA Source'
        ],
        'VIC-Specific': [
            '5. National Mortgage Form VIC Source'
        ],
        'ACT-Specific': [
            '5. National Mortgage Form ACT Source'
        ]
    }
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

    print(str(matter_info))
    # print("test")
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
    for key in templateStructures[loanAgreementDir]:
          if key in matterFiles:
            newDict = templateStructures[loanAgreementDir][key].copy()
            for key2 in templateStructures[loanAgreementDir][key]:
                
                data = matter_info['matter_info'].get(key2, '')
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
   

        pdf_bytes = populateFile(path, data, f"{key}.zip")
        files.append((f"{key}.zip", pdf_bytes))

        
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for filename, content in files:
            zipf.writestr(filename, content)

    zip_buffer.seek(0)
    return StreamingResponse(zip_buffer, media_type="application/zip", headers={
        "Content-Disposition": "attachment; filename=documents.zip"
    })




    


    # Return the response wrapped in JSONResponse
    