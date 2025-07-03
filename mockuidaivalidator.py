"""
Purpose  : Receives the input and checks against the mock uidai database and returns status
@author  : Karthikeyan V
Comments : UIDAI APIs are not available to developers. So mock the workflow
two aadhar details were stored in a AadhaarUsers ( assuming it to be UIDAI 
                                                  database)
and validating the extracted information against this database
"""

import boto3

# ✅ Create a session using your IAM profile
session = boto3.Session(profile_name='vkarthik-iam')

# ✅ Connect to DynamoDB in the correct region
dynamodb = session.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('AadhaarUsers')

def run_mock_uidai_validator(input_str: str) -> str:
    """
    Input: "Name: XXXXXXX\nDOB: DD/MM/YYYY\nAadhaar: 123456789012"
    """

    # ✅ Parse input lines
    lines = input_str.splitlines()
    name = lines[0].split(":")[1].strip()
    dob = lines[1].split(":")[1].strip()
    aadhaar = lines[2].split(":")[1].strip()

    # ✅ Query DynamoDB table
    response = table.get_item(Key={"AadhaarNumber": aadhaar})
    item = response.get('Item')

    if item:
        # ✅ Cross-check name & DOB
        if item['Name'].lower() == name.lower() and item['DOB'] == dob:
            return f'{{"status": "SUCCESS", "message": "Valid Aadhaar", "name": "{name}", "dob": "{dob}", "aadhaar": "{aadhaar}"}}'
        else:
            return f'{{"status": "FAILURE", "message": "Name or DOB mismatch", "name": "{name}", "dob": "{dob}", "aadhaar": "{aadhaar}"}}'
    else:
        return f'{{"status": "FAILURE", "message": "No record found", "name": "{name}", "dob": "{dob}", "aadhaar": "{aadhaar}"}}'

# ✅ Manual test runner
if __name__ == "__main__":
    print("\n=== Mock UIDAI Validator ===\n")
    # ✅ Example test input
    input_data = (
        "Name: XXXXXXX\n"
        "DOB: 01/01/2007\n"
        "Aadhaar: 123456789012"
    )

    # ✅ Run validator and show result
    result = run_mock_uidai_validator(input_data)
    print(f"Input:\n{input_data}\n")
    print(f"Result:\n{result}")
