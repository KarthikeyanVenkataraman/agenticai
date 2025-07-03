"""
Purpose  : UI to demonstrate the Agent workflow. Runs on 5001
@author  : Karthikeyan V
"""

from flask import Flask, render_template, request, redirect, url_for
import os
from ekyc_agent import run_ekyc_from_ui  # <- reuse the helper you made


app = Flask(__name__)

UPLOAD_FOLDER = r"C:\Karthik\agenticai\code\user_uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/", methods=["GET"])
def list_files():
    # Get all PDF files in the uploads folder
    files = [f for f in os.listdir(UPLOAD_FOLDER) if f.lower().endswith(".pdf")]
    return render_template("list_files.html", files=files)

@app.route("/submit", methods=["POST"])
def submit_file():
    filename = request.form.get("filename")
    if filename:
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # 👉 Pass only the path
        logs = run_ekyc_from_ui(pdf_path)

        return render_template("result.html", logs=logs.splitlines())
    return "No file selected.", 400

if __name__ == "__main__":
    app.run(debug=True, port=5001)