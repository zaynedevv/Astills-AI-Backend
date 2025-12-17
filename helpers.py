from populateTemplate import getTemplateStucture
import aiohttp
import asyncio
import httpx
from typing import List, Dict, Any
from docx2pdf import convert
import zipfile
import tempfile

import subprocess
import os
from pathlib import Path


def convert_docx_bytes_to_pdf(docx_bytes: bytes) -> bytes:
    """
    Convert DOCX bytes to PDF bytes using LibreOffice headless.
    """
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        docx_path = Path(tmpdir) / "temp.docx"
        pdf_path = Path(tmpdir) / "temp.pdf"

        # Write DOCX bytes to temp file
        with open(docx_path, "wb") as f:
            f.write(docx_bytes)

        # Convert to PDF
        subprocess.run([
            "soffice",
            "--headless",
            "--convert-to", "pdf",
            "--outdir", str(tmpdir),
            str(docx_path)
        ], check=True)

        # Read PDF bytes
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()

    return pdf_bytes


DOCMOSIS_API_URL = "https://au1.dws4.docmosis.com/api/getSampleData"
ACCESS_KEY = "MjlmMWJhYzItNTZiZS00MzM2LWIyNGQtNGMwMGQ1NGE3OTU1OjQ4NjcyOTEwNQ"

def getBorrowerChecklist(state, transaction_type, directories):
    if state in ['WA', 'TAS', 'NT']:
        checklist = directories.get('Borrowers-Checklist', {}).get('Wetsign')
        if checklist:
            return checklist
        else:
            return None
        
    elif state == 'NSW' and (transaction_type == "Purchase" or transaction_type == "Purchase-Commercial"):
        return directories['Borrowers-Checklist']['NSW']
    else:
        return directories['Borrowers-Checklist']['Non-Wetsign-NSW']
    





def structureJson(matter_info, jsonTemplates):
    for directory in jsonTemplates:
        template = jsonTemplates[directory]
        for key in template:
            if key in matter_info:
                value = matter_info[key]
                if value and value != 0:
                    template[key] = value
                elif not value and value == 0:
                    template[key] = 0
                else:
                    template[key] = None
            else:
                template[key] = None

    return jsonTemplates


def getTemplates(matterFiles):
    jsonTemplates = {}
    for file in matterFiles:
        templateStructure = getTemplateStucture(file);
        if (not templateStructure): continue
        template = templateStructure["templateSampleData"]
        jsonTemplates[file] = template
    return jsonTemplates





async def fetch_template(session: aiohttp.ClientSession, template_name: str) -> Dict[str, Any]:
    """
    Fetch a single template's sample data asynchronously.
    """
    payload = {
        'templateName': template_name,
        'accessKey': ACCESS_KEY
    }

    async with session.post(DOCMOSIS_API_URL, data=payload) as resp:
        resp.raise_for_status()
        data = await resp.json()
        return {template_name: data.get("templateSampleData")}

async def get_templates_async(matter_files: List[str], concurrency: int = 10) -> Dict[str, Any]:
    """
    Fetch multiple templates asynchronously with optional concurrency control.
    """
    semaphore = asyncio.Semaphore(concurrency)
    results: Dict[str, Any] = {}

    async with aiohttp.ClientSession() as session:

        async def fetch_with_semaphore(file: str):
            async with semaphore:
                try:
                    template_data = await fetch_template(session, file)
                    if template_data[file] is not None:
                        results.update(template_data)
                except Exception as e:
                    print(f"Error fetching {file}: {e}")

        tasks = [fetch_with_semaphore(file) for file in matter_files]
        await asyncio.gather(*tasks)

    return results

async def populate_file_async(template_path: str, data: dict, output_name: str) -> bytes:
    json_payload = {
        "outputName": output_name,
        "templateName": template_path,
        "data": data,
        "outputFormat": "pdf;docx",
        "accessKey": "MjlmMWJhYzItNTZiZS00MzM2LWIyNGQtNGMwMGQ1NGE3OTU1OjQ4NjcyOTEwNQ"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post("https://au1.dws4.docmosis.com/api/render", json=json_payload)
        # response.raise_for_status()  # will raise error if status != 200
        if (response.status_code != 200):
            print(response.content)
        return response.content

    

async def generate_all_pdfs(data: dict) -> list[tuple[str, bytes]]:
    tasks = []
    for path, template in data.items():
        file_name = path.split("/")[-1]
        if file_name[-4:].lower() == ".pdf":
            file_name = file_name[:-4] 
        elif file_name[-5:].lower() == ".docx":
            file_name = file_name[:-5] 
        tasks.append(populate_file_async(path, template, file_name))
    
    results = await asyncio.gather(*tasks)
    # Combine file names with content
    return [(path.split("/")[-1] + ".zip", content) for path, content in zip(data.keys(), results)]











