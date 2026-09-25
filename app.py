from flask import Flask, render_template, request
from PyPDF2 import PdfReader
import os

app = Flask(__name__)


# Clean the extracted text by removing empty lines and extra spaces
def clean_text(text):

    lines = text.splitlines()
    cleaned_lines = []

    for line in lines:
        line = line.strip()

        if line:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


# Extract the important sections from the resume
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


# Clean individual skill names so they can be compared easily
def clean_skill(skill):

    skill = skill.strip()

    # Remove the '-' from bullet points
    if skill.startswith("-"):
        skill = skill[1:].strip()

    skill_lower = skill.lower()

    # Convert different descriptions into common skill names
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


# Extract required and preferred skills from the job description
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


# Get the skills written inside the Skills section of the resume
def extract_resume_skills(text):

    sections = extract_sections(text)

    skills_text = sections["skills"]

    skills = []

    lines = skills_text.splitlines()

    for line in lines:

        line = line.strip()

        if line:
            skill = clean_skill(line)
            skills.append(skill)

    return skills


# Compare resume skills with the skills required by the job
def compare_skills(resume_skills, job_skills):

    # Convert both lists into sets for easier comparison
    resume_set = set()

    for skill in resume_skills:
        resume_set.add(skill.lower())

    job_set = set()

    for skill in job_skills:
        job_set.add(skill.lower())

    # Skills that are present in both the resume and job description
    matched_skills = resume_set.intersection(job_set)

    # Skills required by the job but missing from the resume
    missing_skills = job_set - resume_set

    return matched_skills, missing_skills


# Main page
@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        # Get the job description entered by the user
        job_description = request.form.get("job_description", "")

        if not job_description.strip():
            return "Please enter a job description."

        job_description = clean_text(job_description)


        # Get the uploaded resume
        resume = request.files.get("resume")

        if not resume or resume.filename == "":
            return "Please select a resume."


        # Create the uploads folder if it doesn't already exist
        os.makedirs("uploads", exist_ok=True)

        file_path = os.path.join("uploads", resume.filename)

        # Save the uploaded resume
        resume.save(file_path)

        print("\nResume saved:", file_path)


        # Read the uploaded PDF
        reader = PdfReader(file_path)

        text = ""

        # Extract text from every page of the resume
        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text


        # Clean the extracted resume text
        text = clean_text(text)


        # Extract different sections from the resume
        resume_sections = extract_sections(text)


        # Extract required and preferred skills from the JD
        job_skills = extract_job_skills(job_description)


        # Extract skills from the resume
        resume_skills = extract_resume_skills(text)


        # Compare resume skills with required job skills
        matched_skills, missing_skills = compare_skills(
            resume_skills,
            job_skills["required_skills"]
        )


        # Print the results in the terminal
        print("\n========== JOB DESCRIPTION ==========")
        print(job_description)


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


        print("\n========== RESUME SKILLS ==========")

        for skill in resume_skills:
            print(skill)


        print("\n========== SKILL MATCHING ==========")

        print("\nMatched Skills:")

        for skill in matched_skills:
            print(skill)


        print("\nMissing Skills:")

        for skill in missing_skills:
            print(skill)


        print("\n====================================")


    return render_template("index.html")


# Start the Flask application
if __name__ == "__main__":
    app.run(debug=True)