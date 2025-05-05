from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO

def extract_pdf_pages(pdf_bytes: bytes, start_page: int, end_page: int) -> bytes:
    # Initialize PdfReader and PdfWriter
    reader = PdfReader(BytesIO(pdf_bytes))
    writer = PdfWriter()

    # Check for valid page range
    if start_page < 1 or end_page > len(reader.pages):
        raise ValueError("Invalid page range")

    # Extract pages and add them to PdfWriter
    for i in range(start_page - 1, end_page):  # PyPDF2 uses 0-based indexing
        writer.add_page(reader.pages[i])

    # Write the extracted pages to a BytesIO object
    output_pdf = BytesIO()
    writer.write(output_pdf)
    output_pdf.seek(0)  # Go to the beginning of the BytesIO stream

    # Return the bytes of the extracted pages
    return output_pdf.read()