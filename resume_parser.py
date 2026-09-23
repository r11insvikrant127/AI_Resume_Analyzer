import re

from pypdf import PdfReader


def extract_resume_text(uploaded_file):
    """
    Extract text from all pages of a PDF resume.
    """

    try:
        reader = PdfReader(uploaded_file)

        pages = []

        for page in reader.pages:
            text = page.extract_text()

            if text:
                pages.append(text)

        return "\n".join(pages)

    except Exception as e:
        raise Exception(
            f"Unable to read PDF: {e}"
        )


def clean_resume_text(text):
    """
    Normalize whitespace in extracted resume text.
    """

    if not text:
        return ""

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()