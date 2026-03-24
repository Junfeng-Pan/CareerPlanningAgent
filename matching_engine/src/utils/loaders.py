import os
from pypdf import PdfReader
from docx import Document

def load_resume_text(file_path: str) -> str:
    """
    根据文件后缀名，提取 PDF 或 Word 文档中的纯文本。
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件未找到: {file_path}")

    if file_path.endswith('.pdf'):
        return _extract_from_pdf(file_path)
    elif file_path.endswith('.docx'):
        return _extract_from_docx(file_path)
    else:
        raise ValueError(f"不支持的文件格式: {file_path}. 仅支持 .pdf 和 .docx")

def _extract_from_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text.strip()

def _extract_from_docx(file_path: str) -> str:
    doc = Document(file_path)
    text = ""
    for para in doc.paragraphs:
        if para.text:
            text += para.text + "\n"
    return text.strip()
