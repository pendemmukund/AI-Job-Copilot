from flask import Flask, render_template, request
from PyPDF2 import PdfReader
import os

app = Flask(__name__)


# -------------------------------
# Clean Text
# -------------------------------
def clean_text(text):

    lines = text.splitlines()

    cleaned_lines = []

    for line in lines:
        line = line.strip()

        if line:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


# -------------------------------
# Extract Resume Sections
# -------------------------------
def extract_sections(text):

    sections = {
        "education": "",
        "skills": "",
        "projects": "",
        "experience": "",
        "certifications": ""
    }

    current_section = None

    lines = text.splitlines()

    for line in lines:

        line_lower = line.lower().strip()

        if line_lower == "education":
            current_section = "education"

        elif line_lower == "skills":
            current_section = "skills"

        elif line_lower == "projects":
            current_section = "projects"

        elif line_lower == "experience":
            current_section = "experience"

        elif line_lower == "certifications":
            current_section = "certifications"

        elif current_section:
            sections[current_section] += line + "\n"

    return sections

def clean_skill(skill):

    skill = skill.strip()

    if skill.startswith("-"):
        skill = skill[1:].strip()

    skill_lower = skill.lower()

    if "python" in skill_lower:
        return "Python"

    elif "flask" in skill_lower:
        return "Flask"

    elif "sql" in skill_lower:
        return "SQL"

    elif "git" in skill_lower and "github" in skill_lower:
        return "Git/GitHub"

    elif "object-oriented" in skill_lower:
        return "OOP"

    elif "rest" in skill_lower:
        return "REST API"

    elif "html" in skill_lower and "css" in skill_lower:
        return "HTML/CSS"

    elif "javascript" in skill_lower:
        return "JavaScript"

    elif "pandas" in skill_lower:
        return "Pandas"

    elif "numpy" in skill_lower:
        return "NumPy"

    elif "machine learning" in skill_lower:
        return "Machine Learning"

    elif "llm" in skill_lower:
        return "LLM APIs"

    return skill


# -------------------------------
# Extract Job Skills
# -------------------------------
def extract_job_skills(job_description):

    required_skills = []
    preferred_skills = []

    lines = job_description.splitlines()

    current_section = None

    for line in lines:

        line_lower = line.lower().strip()

        if line_lower == "required skills:":
            current_section = "required"

        elif line_lower == "good to have:":
            current_section = "preferred"

        elif current_section and line.strip():

            skill = clean_skill(line)

            if current_section == "required":
                required_skills.append(skill)

            elif current_section == "preferred":
                preferred_skills.append(skill)

    return {
        "required_skills": required_skills,
        "preferred_skills": preferred_skills
    }


# -------------------------------
# Home Route
# -------------------------------
@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        # Debug: See what the browser sends
        print("\n========== FORM DATA ==========")
        print(request.form)

        # Get Job Description
        job_description = request.form.get("job_description", "")

        print("\n========== JOB DESCRIPTION ==========")
        print(job_description)

        # Check Job Description
        if not job_description.strip():
            return "Please enter a job description."

        # Clean Job Description
        job_description = clean_text(job_description)


        # Get Resume
        resume = request.files.get("resume")

        if not resume or resume.filename == "":
            return "Please select a resume."


        # Create uploads folder
        os.makedirs("uploads", exist_ok=True)


        # Save Resume
        file_path = os.path.join("uploads", resume.filename)

        resume.save(file_path)

        print("\nResume saved:", file_path)


        # -------------------------------
        # Read PDF
        # -------------------------------

        reader = PdfReader(file_path)

        text = ""

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text


        # Clean Resume Text
        text = clean_text(text)


        # -------------------------------
        # Extract Resume Sections
        # -------------------------------

        resume_sections = extract_sections(text)


        # -------------------------------
        # Extract Job Skills
        # -------------------------------

        job_skills = extract_job_skills(job_description)


        # -------------------------------
        # Display Results in Terminal
        # -------------------------------

        print("\n========== RESUME TEXT ==========")
        print(text)


        print("\n========== RESUME SECTIONS ==========")

        for section, content in resume_sections.items():

            print(f"\n--- {section.upper()} ---")
            print(content)


        print("\n========== JOB SKILLS ==========")

        print("\nRequired Skills:")

        for skill in job_skills["required_skills"]:
            print(skill)


        print("\nPreferred Skills:")

        for skill in job_skills["preferred_skills"]:
            print(skill)


        print("\n====================================")


    return render_template("index.html")


# -------------------------------
# Run Application
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)