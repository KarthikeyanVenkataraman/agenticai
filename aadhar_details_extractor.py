import re

def extract_aadhar_details(text):
    """
    Extract Aadhaar Name, DOB, Aadhaar number from ENGLISH TEXT ONLY.
    Does NOT fallback to C/O, ignores non-English.
    """

    # Clean up newlines and extra whitespace
    text_clean = " ".join(text.split())

    name = None
    dob = None
    aadhaar_number = None

    # 1️⃣ Extract all possible English capitalized word lines
    possible_names = re.findall(
        r"\b([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){0,3})\b",
        text_clean
    )

    # Filter out known noise
    noise_words = ["TO", "ENROLMENT", "DETAILS", "AADHAAR", "VID", "MALE", "FEMALE", "DIST", "STATE", "PIN", "CODE", "ADDRESS", "C/O", "MOBILE"]
    for candidate in possible_names:
        if all(word.upper() not in noise_words for word in candidate.split()):
            name = candidate.strip()
            break

    # 2️⃣ DOB pattern
    dob_match = re.search(r"(?:DOB|Date of Birth)[^\d]*(\d{2}[/-]\d{2}[/-]\d{4})", text_clean, re.IGNORECASE)
    if dob_match:
        dob = dob_match.group(1)

    # 3️⃣ Aadhaar number: always 12 digits, maybe with space
    aadhaar_match = re.search(r"\b\d{4}\s+\d{4}\s+\d{4}\b|\b\d{12}\b", text_clean)
    if aadhaar_match:
        aadhaar_number = aadhaar_match.group(0).replace(" ", "").strip()

    if not any([name, dob, aadhaar_number]):
        return {"status": "ERR97", "message": "No valid Aadhaar fields found."}

    return {
        "status": "SUCCESS",
        "name": name,
        "dob": dob,
        "aadhaar_number": aadhaar_number,
    }

# ✅ Example Test
if __name__ == "__main__":
    sample = """
    Enrolment No.: 2192/40096/05957
    To
    V Karthikeyan
    C/O: P Venkataraman
    P No.21, TVS Emerald Hamlet
    Mobile: 9840821235
    7369 6026 7850
    VID: 9146 3922 9584 6765
    Details as on: 19/06/2025
    Aadhaar no. issued: 29/12/2015
    DOB: 15/02/1978
    """
    print(extract_aadhar_details(sample))
