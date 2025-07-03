import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path, password=""):
    """
    Extracts all visible text from a PDF using PyMuPDF (fitz).
    Handles password-protected PDFs too.
    """
    try:
        doc = fitz.open(pdf_path)

        if doc.needs_pass:
            if not password:
                return {"status": "ERR", "message": "PDF is password protected. Please provide a password."}
            if not doc.authenticate(password):
                return {"status": "ERR", "message": "Invalid PDF password."}

        full_text = ""
        for page in doc:
            text = page.get_text()
            full_text += text + "\n"

        if not full_text.strip():
            return {"status": "ERR", "message": "No text found. PDF may be image-based."}

        return {
            "status": "SUCCESS",
            "text": full_text.strip()
        }

    except Exception as e:
        return {"status": "ERR", "message": f"Exception: {e}"}


if __name__ == "__main__":
    print("\n=== Aadhaar PDF Text Extractor ===")
    pdf_path = input("Enter PDF path: ").strip()
    password = input("Enter password (leave blank if none): ").strip()

    result = extract_text_from_pdf(pdf_path, password)

    print("\n=== RESULT ===")
    if result["status"] == "SUCCESS":
        print(result["text"])
    else:
        print(f"Error: {result['message']}")
