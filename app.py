from flask import Flask, render_template, request
from PyPDF2 import PdfReader
import os

app = Flask(__name__)


# Function to clean extracted text
def clean_text(text):
    lines = text.splitlines()

    cleaned_lines = []

    for line in lines:
        line = line.strip()

        if line:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        # Get job description from the form
        job_description = request.form["job_description"]

        # Clean job description
        job_description = clean_text(job_description)

        # Get uploaded resume
        resume = request.files["resume"]

        # Check whether a file was selected
        if resume.filename == "":
            return "Please select a resume."

        # Create file path
        file_path = os.path.join("uploads", resume.filename)

        # Save resume
        resume.save(file_path)

        print("Resume saved:", file_path)

        # Read the PDF
        reader = PdfReader(file_path)

        # Extract text from all pages
        text = ""

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text

        # Clean extracted resume text
        text = clean_text(text)

        # Display the results in terminal
        print("\n========== JOB DESCRIPTION ==========")
        print(job_description)

        print("\n========== RESUME TEXT ==========")
        print(text)

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)