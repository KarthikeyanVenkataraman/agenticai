import re

def extract_text_metadata(input_data) -> dict:
    """
    Robust Aadhaar text extractor — works even if whole text is one line.
    """
    # Normalize input
    if isinstance(input_data, dict) and "text" in input_data:
        text = input_data["text"]
    else:
        text = input_data

    # Force split by newlines OR fallback split by '  ' or Tamil + English markers
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if len(lines) <= 1:
        # Fallback: break on Tamil → English transitions
        lines = re.split(r'(?<=[^\x00-\x7F])\s+(?=[A-Za-z])', text)
        lines = [l.strip() for l in lines if l.strip()]

    name = None
    dob = None
    aadhaar_number = None

    # 1️⃣ Name: Tamil line → next line is English OR fallback to pattern
    for i, line in enumerate(lines):
        if re.search(r'[^\x00-\x7F]', line):
            if i + 1 < len(lines):
                english_candidate = lines[i + 1].strip()
                ascii_candidate = re.sub(r'[^\x00-\x7F]', '', english_candidate).strip()
                if len(ascii_candidate.split()) >= 2 and not ascii_candidate.lower().startswith('c/o'):
                    name = ascii_candidate
                    break

    if not name:
        # Fallback: Regex find longest A-Z block
        match = re.search(r'\b[A-Z][A-Za-z\s\.]{2,}\b', text)
        if match:
            name = match.group().strip()

    # 2️⃣ DOB
    dob_pattern = re.compile(r'\b\d{2}[/-]\d{2}[/-]\d{4}\b')
    for i, line in enumerate(lines):
        if 'DOB' in line.upper():
            found = dob_pattern.search(line)
            if found:
                dob = found.group()
                break
            if i + 1 < len(lines):
                found = dob_pattern.search(lines[i + 1])
                if found:
                    dob = found.group()
                    break
    if not dob:
        found = dob_pattern.search(text)
        if found:
            dob = found.group()

    # 3️⃣ Aadhaar number
    aadhaar_pattern = re.compile(r'\b\d{4}\s\d{4}\s\d{4}\b')
    for m in aadhaar_pattern.finditer(text):
        idx = m.start()
        window = text[max(0, idx - 30): idx + 30]
        if 'VID' in window.upper():
            continue
        aadhaar_number = m.group().replace(' ', '')
        break

    return {
        "name": name,
        "dob": dob,
        "aadhaar_number": aadhaar_number
    }
