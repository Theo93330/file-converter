import os
import pandas as pd
import pdfplumber
from PyPDF2 import PdfReader, PdfWriter
from docx import Document
from openpyxl import Workbook
import tempfile

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'xlsx', 'xls', 'csv', 'png', 'jpg', 'jpeg', 'txt'}

def _tmpfile(suffix=''):
    fd, path = tempfile.mkstemp(suffix=suffix)
    os.close(fd)
    return path

def process_file(path, action, paid=False):
    name = os.path.basename(path)
    base, ext = os.path.splitext(name)
    ext = ext.lower().lstrip('.')

    if action == 'extract_text':
        return extract_text_from_pdf(path)
    if action == 'pdf_to_docx' and ext == 'pdf':
        return pdf_to_docx(path)
    if action == 'csv_to_xlsx' and ext in ('csv',):
        return csv_to_xlsx(path)
    if action == 'clean_csv' and ext in ('csv', 'xlsx'):
        return clean_table(path)
    # default fallback: return text file
    return extract_text_generic(path)

def extract_text_from_pdf(path):
    out = _tmpfile(suffix='.txt')
    text_parts = []
    with pdfplumber.open(path) as pdf:
        for p in pdf.pages:
            text = p.extract_text()
            if text:
                text_parts.append(text)
    with open(out, 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(text_parts))
    return out, 'text/plain'

def extract_text_generic(path):
    _, ext = os.path.splitext(path)
    ext = ext.lower().lstrip('.')
    if ext == 'txt':
        return path, 'text/plain'
    if ext == 'csv':
        df = pd.read_csv(path)
        out = _tmpfile(suffix='.xlsx')
        df.to_excel(out, index=False)
        return out, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    # fallback
    return path, 'application/octet-stream'

def pdf_to_docx(path):
    out = _tmpfile(suffix='.docx')
    text, _ = extract_text_from_pdf(path)
    with open(text, 'r', encoding='utf-8') as f:
        content = f.read()
    doc = Document()
    for para in content.split('\n'):
        doc.add_paragraph(para)
    doc.save(out)
    return out, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'

def csv_to_xlsx(path):
    df = pd.read_csv(path)
    out = _tmpfile(suffix='.xlsx')
    df.to_excel(out, index=False)
    return out, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

def clean_table(path):
    _, ext = os.path.splitext(path)
    ext = ext.lower().lstrip('.')
    if ext == 'csv':
        df = pd.read_csv(path, dtype=str)
    else:
        df = pd.read_excel(path, dtype=str)
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    df = df.dropna(axis=1, how='all')
    df = df.dropna(axis=0, how='all')
    df = df.drop_duplicates()
    out = _tmpfile(suffix='.xlsx')
    df.to_excel(out, index=False)
    return out, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
