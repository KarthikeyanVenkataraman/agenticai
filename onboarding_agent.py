"""
Purpose  : Agent to run the onboarding process
@author  : Karthikeyan V
Comments : 
    1. insert in dynamo db after SOP is successful from ChromaDB
    2. initiates a email in case the customer is a minor for human agent review
"""

import boto3
from datetime import datetime
from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.agents import Tool, initialize_agent

from customer_onboarding_failure import send_onboarding_failed_email_due_to_minor

# ------------------------------
# ✅ Load environment variables
# ------------------------------
load_dotenv()

# ------------------------------
# ✅ AWS session & DynamoDB
# ------------------------------
session = boto3.Session(profile_name='vkarthik-iam')
dynamodb = session.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('customermaster')

# ------------------------------
# ✅ Init Embeddings + LLM
# ------------------------------
embeddings = OpenAIEmbeddings()
llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")

# ------------------------------
# ✅ Insert customer to DynamoDB
# ------------------------------
def insert_customer_to_dynamodb(name: str, dob: str, aadhaar: str, age: int) -> str:
    try:
        table.put_item(
            Item={
                "AadhaarNumber": aadhaar,
                "Name": name,
                "DOB": dob,
                "Age": age,
                "Status": "ONBOARDED"
            }
        )
        print(f"✅ Inserted into DynamoDB for Aadhaar: {aadhaar}")
        return "INSERTED"
    except Exception as e:
        print(f"⚠️ Insert failed: {e}")
        return f"INSERT_FAILED: {e}"

# ------------------------------
# ✅ Human loop (manual step)
# ------------------------------
def trigger_human_loop(name: str, dob: str, aadhaar: str, age: int, phone: str = "N/A") -> str:
    print(f"🚩 Human loop triggered for: {name} (Age: {age})")
    send_onboarding_failed_email_due_to_minor(
        to_email="jaidev.karthikeyan@gmail.com",
        name=name,
        dob=dob,
        aadhaar=aadhaar,
        phone=phone,
        reason="Customer is a minor (<18 years)"
    )
    return "HUMAN_LOOP_TRIGGERED"

# ------------------------------
# ✅ Main onboarding logic
# ------------------------------

def run_onboarding(name: str, dob: str, aadhaar: str) -> str:
    print("\n=== ✅ Onboarding Agent ===\n")
    print(f"Name: {name}")
    print(f"DOB: {dob}")
    print(f"Aadhaar: {aadhaar}")

    try:
        dob_date = datetime.strptime(dob, "%d/%m/%Y")
        today = datetime.today()
        age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
        print(f"Calculated Age: {age}")
    except Exception as e:
        print(f"⚠️ DOB parse failed: {e}")
        return f"DOB_PARSE_ERROR: {e}"

    vectorstore = Chroma(
        persist_directory="./sop_chroma_db",
        embedding_function=embeddings
    )

    query = f"What happens if the customer is {age} years old?"
    results = vectorstore.similarity_search(query, k=2)

    if not results:
        print("⚠️ SOP match not found.")
    else:
        print("\n=== 📄 SOP Results ===\n")
        for i, doc in enumerate(results, 1):
            print(f"Result #{i}:\n{doc.page_content}\n")
    
    if age < 18:
        print("🚩 Decision: MINOR — needs human loop.")
        return f"HUMAN_LOOP_REQUIRED|name:{name},dob:{dob},aadhaar:{aadhaar},age:{age}"
    else:
        print("✅ Major — auto insert.")
        return f"INSERT_REQUIRED|name:{name},dob:{dob},aadhaar:{aadhaar},age:{age}"


# ------------------------------
# ✅ Dispatcher for LLM input
# ------------------------------
def onboarding_dispatcher(output_str: str) -> str:
    cleaned = output_str.strip().replace("'", "").replace('"', "").replace("\n", "")
    print(f"=== Dispatcher received: {cleaned}")

    try:
        action, data = cleaned.split("|", 1)
        action = action.strip().upper()
        parts = data.split(",")
        args = {}
        for kv in parts:
            key, val = kv.split(":")
            args[key.strip()] = val.strip()

        name = args['name']
        dob = args['dob']
        aadhaar = args['aadhaar']
        age = int(args['age'])

        # Optional: parse phone if ever included in flow later
        phone = args.get('phone', 'N/A')

        if action == "HUMAN_LOOP_REQUIRED":
            return trigger_human_loop(name, dob, aadhaar, age, phone)
        elif action == "INSERT_REQUIRED":
            return insert_customer_to_dynamodb(name, dob, aadhaar, age)
        else:
            return f"UNKNOWN_ACTION: {action}"
    except Exception as e:
        print(f"⚠️ Dispatcher parse failed: {e}")
        return f"DISPATCHER_ERROR: {e}"

# ------------------------------
# ✅ Parse raw LLM input
# ------------------------------
def run_onboarding_tool(input_str: str) -> str:
    try:
        parts = input_str.split(",")
        name = parts[0].split(":")[1].strip()
        dob = parts[1].split(":")[1].strip()
        aadhaar = parts[2].split(":")[1].strip()
    except Exception as e:
        return f"PARSE_ERROR: {e}"
    return run_onboarding(name, dob, aadhaar)

# ------------------------------
# ✅ Define tools for the agent
# ------------------------------
onboarding_tools = [
    Tool(
        name="RunOnboarding",
        func=run_onboarding_tool,
        description="Run onboarding. Input: 'name: X, dob: DD/MM/YYYY, aadhaar: Y'."
    ),
    Tool(
        name="OnboardingDispatcher",
        func=onboarding_dispatcher,
        description="Dispatch result from onboarding logic."
    )
]

# ------------------------------
# ✅ Initialize agent
# ------------------------------
onboarding_agent = initialize_agent(
    tools=onboarding_tools,
    llm=llm,
    agent_type="zero-shot-react-description",
    verbose=True
)

# ------------------------------
# ✅ Manual test runner
# ------------------------------
if __name__ == "__main__":
    print("\n=== Manual Test ===\n")
    query = """
    Run the onboarding process for:
    name: V Karthikeyan, dob: 01/01/2010, aadhaar: 123412341234
    """  # 👈 test with a minor DOB!
    result = onboarding_agent.run(query)
    print(f"\n=== Final Result: {result} ===")
