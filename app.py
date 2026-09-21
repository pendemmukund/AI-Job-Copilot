from flask import Flask, render_template, request
from PyPDF2 import PdfReader
import os

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        job_description = request.form["job_description"]

        resume = request.files["resume"]

        if resume.filename == "":
            return "Please select a resume."

        file_path = os.path.join("uploads", resume.filename)

        resume.save(file_path)

        print("Resume saved:", file_path)

        reader = PdfReader(file_path)

        text = ""

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text

        print("\nExtracted Resume Text:")
        print(text)

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)