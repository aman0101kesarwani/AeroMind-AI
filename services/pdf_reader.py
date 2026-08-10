import fitz        # provided by PyMuPDF
from pathlib import Path        #Path is used for handling file paths in a clean and platform-independent way.

def extract_pdf_from_pdf(pdf_path : Path):
    """
    Extract text from a PDF page by page.
    """

    document = fitz.open(pdf_path)

    pages=[]

    for page_number, page in enumerate(document):

        page.append({
            "page" : page_number + 1,
            "text" : page.get_text()
        })

    document.close()

    return pages






# extract text from pdf
def extract_text_from_pdf(pdf_path: Path):
    """
    Extract text from a PDF page by page.
    """

    document = fitz.open(pdf_path)

    pages = []

    for page_number, page in enumerate(document):
        pages.append({
            "page": page_number + 1,
            "text": page.get_text()
        })

    document.close()

    return pages



























"""
pdf_path : which is the location of the PDF.
"""

"""
the function return :
[
    {
        "page": 1,
        "text": "Introduction to Aircraft..."
    },
    {
        "page": 2,
        "text": "Engine Maintenance..."
    },
    {
        "page": 3,
        "text": "Safety Procedures..."
    }
]


notice :we keep the page number.
"""