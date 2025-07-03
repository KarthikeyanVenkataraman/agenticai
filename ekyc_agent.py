import os
import ast
import json
import re  # ✅ For fallback extraction
from dotenv import load_dotenv

from langchain.agents import Tool, initialize_agent
from langchain_openai import ChatOpenAI

# ------------------------------
# ✅ Load env vars from .env
# ------------------------------
load_dotenv()

llm = ChatOpenAI(
    temperature=0,
    model_name="gpt-3.5-turbo"
)

# ------------------------------
# ✅ Import your actual extractors
# ------------------------------
from aadhar_textpdf_extractor import extract_text_from_pdf
from aadhar_pdfimage_extractor import extract_text_from_image_pdf

# ✅ Use FINAL version of text metadata extractor
from aadhar_textmetadata_extractor import extract_text_metadata

# ✅ Import your mock UIDAI validator
from mockuidaivalidator import run_mock_uidai_validator

# ✅ Import your failure email sender
from send_failure_email import send_failure_email

# ✅ Import your onboarding agent entrypoint

from onboarding_agent import run_onboarding, onboarding_dispatcher


# ------------------------------
# ✅ Tool wrappers
# ------------------------------
def run_pdf_extractor(input_str: str) -> str:
    parts = [p.strip() for p in input_str.split(",")]
    pdf_path = parts[0]
    password = parts[1] if len(parts) > 1 else ""
    result = extract_text_from_pdf(pdf_path, password)
    return result["text"] if result["status"] == "SUCCESS" else "ERR: " + result["message"]

def run_image_extractor(pdf_path: str) -> str:
    result = extract_text_from_image_pdf(pdf_path)
    return result["text"] if result["status"] == "SUCCESS" else "ERR: " + result["message"]

def run_text_metadata_extractor(text: str) -> str:
    # ✅ Defensive unwrap for possible dict input
    if text.strip().startswith("{'status':"):
        try:
            obj = ast.literal_eval(text)
            text = obj.get("text", "")
        except Exception:
            pass
    result = extract_text_metadata(text)
    return f"Name: {result['name']}\nDOB: {result['dob']}\nAadhaar: {result['aadhaar_number']}"

def run_mock_uidai(text: str) -> str:
    # ✅ Force validator input to multiline
    if ',' in text:
        text = text.replace(",", "\n")
    json_result = run_mock_uidai_validator(text)
    return json_result.strip()  # ✅ Always return clean JSON only

"""
def run_ocr_metadata_extractor(text: str) -> str:
    result = extract_ocr_metadata(text)
    return f"Name: {result['name']}\nDOB: {result['dob']}\nAadhaar: {result['aadhaar_number']}"
"""

# ------------------------------
# ✅ Register tools
# ------------------------------
tools = [
    Tool(
        name="PDF Extractor",
        func=run_pdf_extractor,
        description="Extract text from an editable Aadhaar PDF. Input: <pdf_path>,<password>"
    ),
    Tool(
        name="Text Metadata Extractor",
        func=run_text_metadata_extractor,
        description="Extract Name, DOB, Aadhaar number from plain text."
    ),
    Tool(
        name="Mock UIDAI Validator",
        func=run_mock_uidai,
        description="Validate extracted Aadhaar details against mock UIDAI database."
    ),
]

# ------------------------------
# ✅ Init agent
# ------------------------------
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent_type="zero-shot-react-description",
    verbose=True
)

# ------------------------------
# ✅ CLI Flow with Human-in-the-Loop
# ------------------------------
if __name__ == "__main__":
    print("\n=== eKYC LangChain Agent ===\n")

    pdf_path = input("PDF path: ").strip()
    password = input("PDF password (optional): ").strip()
    pdf_input = f"{pdf_path},{password}" if password else pdf_path
    customer_phone = input("Customer Phone: ").strip()

    # ✅ Plan the agent flow
    query = f"""
    1. Use PDF Extractor with: {pdf_input}
    2. If PDF Extractor succeeds, pass its text to Text Metadata Extractor.
    3. Pass extracted Name, DOB, Aadhaar to Mock UIDAI Validator.
    4. Return ONLY the JSON output from the Mock UIDAI Validator without any extra explanation.
    """

    print("\n=== Final Result ===\n")
    result = agent.run(query)
    print(result)

    try:
        # ✅ Try parsing as JSON
        result_json = json.loads(result)
        if result_json.get("status") == "FAILURE":
            name = result_json.get("name", "UNKNOWN")
            aadhaar = result_json.get("aadhaar", "UNKNOWN")
            reason = result_json.get("message", "Unknown failure")

            send_failure_email(
                to_email="jaidev.karthikeyan@gmail.com",
                name=name,
                aadhaar=aadhaar,         
                phone=customer_phone,
                reason=reason
            )
        elif result_json.get("status") == "SUCCESS":
            # ✅ Extract success details
            name = result_json.get("name", "UNKNOWN")
            dob = result_json.get("dob", "UNKNOWN")
            aadhaar = result_json.get("aadhaar", "UNKNOWN")

            # ✅ Call Onboarding Agent with details
            print("\n=== ✅ Calling Onboarding Agent ===\n")
            onboarding_result = run_onboarding(name=name, dob=dob, aadhaar=aadhaar)
            
            dispatcher_result = onboarding_dispatcher(
                onboarding_result.replace("\n", "") + f",phone:{customer_phone}"
            )
            print(f"\n=== Final Dispatcher Result: {dispatcher_result} ===")

            
            
    except Exception as e:
        # ✅ If parsing failed — fallback with regex extraction
        print(f"Could not parse JSON result: {e}")

        aadhaar_match = re.search(r"Aadhaar[: ]+(\d{8,})", result)
        name_match = re.search(r"Name[: ]+([A-Za-z\s\.]+)", result)
        reason_match = re.search(r"(No record found|mismatch|Failure|Failed)", result, re.IGNORECASE)

        aadhaar = aadhaar_match.group(1) if aadhaar_match else "UNKNOWN"
        name = name_match.group(1) if name_match else "UNKNOWN"
        reason = reason_match.group(1) if reason_match else "Unknown failure"

        send_failure_email(
            to_email="jaidev.karthikeyan@gmail.com",
            name=name,
            aadhaar=aadhaar,
            phone=customer_phone,
            reason=reason
        )



def run_ekyc_from_ui(pdf_path: str) -> str:
    """
    Runs the eKYC + onboarding flow for uploaded file (for web UI).
    Reads <pdf_path> plus _password.txt and _phone.txt companions.
    Returns a log string.
    """
    logs = []
    logs.append("=== 🗂️ eKYC Agent (UI Trigger) ===")
    
    filename_wo_ext, _ = os.path.splitext(pdf_path)
    pw_file = filename_wo_ext + "_password.txt"
    phone_file = filename_wo_ext + "_phone.txt"

    password = ""
    phone = ""

    if os.path.exists(pw_file):
        with open(pw_file, "r") as f:
            password = f.read().strip()

    if os.path.exists(phone_file):
        with open(phone_file, "r") as f:
            phone = f.read().strip()

    logs.append(f"📄 PDF Path: {pdf_path}")
    logs.append(f"🔑 Password: {'(provided)' if password else '(none)'}")
    logs.append(f"📞 Phone: {phone if phone else '(not provided)'}")

    pdf_input = f"{pdf_path},{password}" if password else pdf_path

    query = f"""
    You must follow these steps exactly:
    
    1️⃣ Use the **PDF Extractor** tool with: {pdf_input}
    
    2️⃣ Take the **RAW extracted text block exactly as-is**, do not modify or summarize it, and pass that **entire text block** to the **Text Metadata Extractor** tool.
    
    3️⃣ Then pass the extracted fields (Name, DOB, Aadhaar) to the **Mock UIDAI Validator**.
    
    4️⃣ Return **only** the final JSON output from the Mock UIDAI Validator. Do not explain or modify.
    """

    try:
        result = agent.run(query)
        logs.append("\n=== ✅ Mock UIDAI Validator Result ===")
        logs.append(result)

        import json, re
        result_json = json.loads(result)

        if result_json.get("status") == "FAILURE":
            name = result_json.get("name", "UNKNOWN")
            aadhaar = result_json.get("aadhaar", "UNKNOWN")
            reason = result_json.get("message", "Unknown failure")

            send_failure_email(
                to_email="jaidev.karthikeyan@gmail.com",
                name=name,
                aadhaar=aadhaar,
                phone=phone,
                reason=reason
            )
            logs.append("\n🚩 Failure email sent for failure.")

        elif result_json.get("status") == "SUCCESS":
            name = result_json.get("name", "UNKNOWN")
            dob = result_json.get("dob", "UNKNOWN")
            aadhaar = result_json.get("aadhaar", "UNKNOWN")

            logs.append("\n=== ✅ Running Onboarding Agent ===")
            onboarding_result = run_onboarding(name=name, dob=dob, aadhaar=aadhaar)
            
            dispatcher_result = onboarding_dispatcher(
                onboarding_result.replace("\n", "") + f",phone:{phone}"
            )
            logs.append(f"\n=== Final Dispatcher Result: {dispatcher_result} ===")

        else:
            logs.append("\n⚠️ Unknown status in UIDAI result.")

    except Exception as e:
        logs.append(f"\n❌ Exception: {e}")

    return "\n".join(logs)
