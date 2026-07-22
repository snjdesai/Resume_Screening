
import os
import fitz  # PyMuPDF
import pdfplumber
from docx import Document  # Importing Document directly

class ResumeParser:
    def read_pdf(self, filepath):
        text = ""
        pdf = fitz.open(filepath)
        for page in pdf:
            text += page.get_text()
        pdf.close()
        return text

    def read_docx(self, filepath):
        # Fixed: Changed docx.Document to just Document based on your import line
        document = Document(filepath)
        text = ""
        for para in document.paragraphs:
            text += para.text + "\n"
        return text

    def read_text(self, filepath):
        if filepath.endswith(".pdf"):
            return self.read_pdf(filepath)
        elif filepath.endswith(".docx"):
            return self.read_docx(filepath)
        else:
            raise Exception("Unsupported File")

