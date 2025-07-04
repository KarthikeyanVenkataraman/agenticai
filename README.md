# Agentic AI Driven eKYCand Automated Onboarding

==== This is work in progress. Will be updated in detail in couple of days. Idea is to pull the code and setup in your own devlopment environment to see the power of Agentic AI. It requires few additional libraries and also ChromaDB which I will provide detailed instructions to setup. ====

I have developed a functional prototype on my local machine for a FinTech use case utilizing Agentic AI. I aimed to showcase two AI agents (ekyc & customer onboarding) interacting with one another, while incorporating a RAG in the loop. Attached are screenshots for your reference. In summary, I have employed LangChain and the OpenAI API to utilize the GPT-3.5 Turbo LLM, along with ChromaDB to establish vector embeddings for my customer onboarding rules, which are stored in PDF format as plain text. ChromaDB serves to illustrate the capability of integrating RAG within an agentic workflow. Furthermore, although we prefer agents to operate autonomously, there remains a necessity for human intervention. I have constructed two scenarios where Human-in-the-Loop (HILT) is also demonstrated through an email notification.

<img width="818" alt="image" src="https://github.com/user-attachments/assets/5b95af9c-055e-4f58-ae94-d6e806d8231a" />


✅ eKYC Agent: Uses custom Python extractors to pull data from Aadhaar PDFs, then leverages LangChain agents and OpenAI GPT-3.5 Turbo to orchestrate tool calls, parse metadata, and validate against a mock UIDAI.

✅ Onboarding Agent with RAG: Uses Retrieval-Augmented Generation with LangChain and GPT-3.5 Turbo to dynamically fetch Standard Operating Procedures from ChromaDB (vector store) for compliant onboarding of the customer.

✅ Human-in-the-Loop: Flags edge cases like minors based on SOPs or  eKYC failures for manual review, with automated email alerts sent via Google SMTP.

✅ DynamoDB Integration: Persists verified customer profiles instantly in AWS DynamoDB, enabling real-time downstream loan processing ( downstream loan processing - out of scope ).

1. Please setup a local environment where you can run python like C:\Karthik\agenticai\venv
2. All code will reside under C:\Karthik\agenticai\code
3. HTML files will reside in C:\Karthik\agenticai\code\templates
4. Two UI apps are also built namely app.py and agent_ui.py ( UX for customer and agentic ai demo )

* aadhar_textpdf_extractor.py 		- Extracts all the text from the given text based PDF
* aadhar_textmetadata_extractor.py 	- Extracts the Name, DOB, Aadhar number
* mockuidaivalidator.py		- Receives the input and checks against the mock uidai database and returns status
* send_failure_email.py		- Sends an email to human in case there is a failure
* ekyc_agent.py			- Agent for eKYC processing
* app.py - Customer uploads the Aadhar vard via UI
* customer_onboarding_failure - Sends an email to human in case there is a failure when onboarding failed due to SOP
* onboarding_agent.py - Onboarding agent for customer
* agent_ui.py - UI built just for demo purposes to show how the agent runs in LangChain.

* UI related files (.html) needs to be stored in a folder like C:\Karthik\agenticai\code\templates



