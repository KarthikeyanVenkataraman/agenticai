"""
Purpose  : UI for uploading the Aadhar files
@author  : Karthikeyan V

"""


from flask import Flask, render_template, request
import os

app = Flask(__name__)

UPLOAD_FOLDER = r"C:\Karthik\agenticai\code\user_uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/", methods=["GET", "POST"])
def upload_file():
    message = ""
    if request.method == "POST":
        pdf = request.files['aadhaar_file']   
        password = request.form.get("password", "").strip()
        phone = request.form.get("phone", "").strip()

        if pdf:
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf.filename)
            pdf.save(save_path)

            filename_wo_ext, _ = os.path.splitext(save_path)

            if password:
                pw_file = filename_wo_ext + "_password.txt"
                with open(pw_file, "w") as f:
                    f.write(password)

            if phone:
                phone_file = filename_wo_ext + "_phone.txt"
                with open(phone_file, "w") as f:
                    f.write(phone)

            message = "✅ Thanks for providing your Aadhaar successfully. We will provide you the status of your loan."

    return render_template("upload.html", message=message)

if __name__ == "__main__":
    app.run(debug=True)
