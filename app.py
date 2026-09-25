from flask import Flask, render_template, request
from PyPDF2 import PdfReader
import os

app = Flask(__name__)


# -----------------------------
# Clean text
# -----------------------------
def clean_text(text):

    lines = text.splitlines()

    cleaned_lines = []

    for line in lines:

        line = line.strip()

        if line:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


# -----------------------------
# Extract resume sections
# -----------------------------
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

        elif line_lower in ["skills", "technical skills"]:

            current_section = "skills"

        elif line_lower == "projects":

            current_section = "projects"

        elif line_lower in ["experience", "professional experience"]:

            current_section = "experience"

        elif line_lower in [
            "certifications",
            "certifications & leadership"
        ]:

            current_section = "certifications"

        elif current_section:

            sections[current_section] += line + "\n"

    return sections


# -----------------------------
# Normalize a skill
# -----------------------------
def clean_skill(skill):

    skill = skill.strip()

    # Remove bullet symbols
    skill = skill.lstrip("-•*").strip()

    skill_lower = skill.lower()

    # Python
    if "python" in skill_lower:

        return "Python"

    # Flask
    elif "flask" in skill_lower:

        return "Flask"

    # SQL
    elif (
        skill_lower == "sql"
        or "sql and database" in skill_lower
        or "sql queries" in skill_lower
    ):

        return "SQL"

    # REST API
    elif "rest api" in skill_lower or "rest apis" in skill_lower:

        return "REST API"

    # HTML/CSS
    elif (
        ("html" in skill_lower and "css" in skill_lower)
        or "html and css" in skill_lower
        or "html/css" in skill_lower
    ):

        return "HTML/CSS"

    # HTML by itself
    elif skill_lower in ["html", "html5"]:

        return "HTML/CSS"

    # CSS by itself
    elif skill_lower in ["css", "css3"]:

        return "HTML/CSS"

    # Git and GitHub
    elif (
        ("git" in skill_lower and "github" in skill_lower)
        or "git/github" in skill_lower
        or "git and github" in skill_lower
    ):

        return "Git/GitHub"

    # Git by itself
    elif skill_lower == "git":

        return "Git/GitHub"

    # GitHub by itself
    elif skill_lower == "github":

        return "Git/GitHub"

    # Object-Oriented Programming
    elif (
        "object-oriented" in skill_lower
        or "object oriented" in skill_lower
        or skill_lower == "oop"
        or "(oop)" in skill_lower
    ):

        return "OOP"

    # Problem solving
    elif (
        "problem-solving" in skill_lower
        or "problem solving" in skill_lower
        or "debugging" in skill_lower
    ):

        return "Problem-Solving & Debugging"

    # Pandas
    elif "pandas" in skill_lower:

        return "Pandas"

    # NumPy
    elif "numpy" in skill_lower:

        return "NumPy"

    # Matplotlib
    elif "matplotlib" in skill_lower:

        return "Matplotlib"

    # Machine Learning
    elif "machine learning" in skill_lower:

        return "Machine Learning"

    # LLM APIs
    elif "llm" in skill_lower:

        return "LLM APIs"

    # JavaScript
    elif "javascript" in skill_lower:

        return "JavaScript"

    # Streamlit
    elif "streamlit" in skill_lower:

        return "Streamlit"

    # PyPDF2
    elif "pypdf2" in skill_lower:

        return "PyPDF2"

    # SQLite
    elif "sqlite" in skill_lower:

        return "SQLite"

    # MySQL
    elif "mysql" in skill_lower:

        return "MySQL"

    # Gemini API
    elif "gemini" in skill_lower:

        return "Gemini API"

    # DBMS
    elif "dbms" in skill_lower:

        return "DBMS"

    # Data Structures
    elif "data structures" in skill_lower:

        return "Data Structures & Algorithms"

    # Backend Development
    elif "backend" in skill_lower:

        return "Backend Development"

    # Exception Handling
    elif "exception handling" in skill_lower:

        return "Exception Handling"

    # Return original skill if no match
    return skill


# -----------------------------
# Extract skills from resume
# -----------------------------
def extract_resume_skills(text):

    sections = extract_sections(text)

    skills_text = sections["skills"]

    skills = []

    lines = skills_text.splitlines()

    for line in lines:

        line = line.strip()

        if not line:
            continue

        # Remove category name before colon
        if ":" in line:

            line = line.split(":", 1)[1]

        # Split multiple skills
        skill_list = line.split(",")

        for skill in skill_list:

            skill = skill.strip()

            if skill:

                skill = clean_skill(skill)

                skills.append(skill)

    return skills


# -----------------------------
# Extract skills from job description
# -----------------------------
def extract_job_skills(job_description):

    required_skills = []

    preferred_skills = []

    lines = job_description.splitlines()

    current_section = None

    for line in lines:

        line = line.strip()

        line_lower = line.lower()

        # Remove bullet
        line = line.lstrip("-•*").strip()

        line_lower = line.lower()

        if line_lower == "required skills:":

            current_section = "required"

            continue

        elif line_lower in [
            "good to have:",
            "preferred skills:"
        ]:

            current_section = "preferred"

            continue

        elif line_lower in [
            "education:",
            "experience:"
        ]:

            current_section = None

            continue

        if current_section and line:

            # A job requirement can contain multiple concepts
            # such as "HTML and CSS basics"
            if "html" in line_lower and "css" in line_lower:

                required_skill = "HTML/CSS"

            elif "git" in line_lower and "github" in line_lower:

                required_skill = "Git/GitHub"

            elif "pandas" in line_lower and "numpy" in line_lower:

                # Add both separately
                if current_section == "required":
                    required_skills.append("Pandas")
                    required_skills.append("NumPy")
                else:
                    preferred_skills.append("Pandas")
                    preferred_skills.append("NumPy")

                continue

            elif (
                "problem-solving" in line_lower
                or "problem solving" in line_lower
                or "debugging" in line_lower
            ):

                required_skill = "Problem-Solving & Debugging"

            else:

                required_skill = clean_skill(line)

            if current_section == "required":

                required_skills.append(required_skill)

            elif current_section == "preferred":

                preferred_skills.append(required_skill)

    return {
        "required_skills": required_skills,
        "preferred_skills": preferred_skills
    }


# -----------------------------
# Compare skills
# -----------------------------
def compare_skills(resume_skills, job_skills):

    resume_set = set()

    for skill in resume_skills:

        normalized_skill = clean_skill(skill)

        resume_set.add(normalized_skill.lower())


    job_set = set()

    for skill in job_skills:

        normalized_skill = clean_skill(skill)

        job_set.add(normalized_skill.lower())


    matched_skills = resume_set.intersection(job_set)

    missing_skills = job_set - resume_set

    return matched_skills, missing_skills


# -----------------------------
# Home route
# -----------------------------
@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        # Get job description
        job_description = request.form.get(
            "job_description",
            ""
        )

        if not job_description.strip():

            return "Please enter a job description."


        # Get uploaded resume
        resume = request.files.get("resume")

        if not resume or resume.filename == "":

            return "Please select a resume."


        # Create uploads folder
        os.makedirs("uploads", exist_ok=True)


        # Save resume
        file_path = os.path.join(
            "uploads",
            resume.filename
        )

        resume.save(file_path)

        print("\nResume saved:", file_path)


        # Read PDF
        reader = PdfReader(file_path)

        text = ""

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:

                text += page_text


        # Clean resume text
        text = clean_text(text)


        # Extract job skills
        job_skills = extract_job_skills(
            job_description
        )


        # Extract resume skills
        resume_skills = extract_resume_skills(
            text
        )


        # Compare skills
        matched_skills, missing_skills = compare_skills(
            resume_skills,
            job_skills["required_skills"]
        )


        # Print results for testing
        print("\n========== RESUME SKILLS ==========")

        for skill in resume_skills:

            print(skill)


        print("\n========== JOB REQUIRED SKILLS ==========")

        for skill in job_skills["required_skills"]:

            print(skill)


        print("\n========== SKILL MATCHING ==========")

        print("\nMatched Skills:")

        for skill in matched_skills:

            print(skill)


        print("\nMissing Skills:")

        for skill in missing_skills:

            print(skill)


        print("\n====================================")


        # Show results page
        return render_template(
            "results.html",
            matched_skills=sorted(matched_skills),
            missing_skills=sorted(missing_skills)
        )


    # GET request
    return render_template("index.html")


# -----------------------------
# Run Flask
# -----------------------------
if __name__ == "__main__":

    app.run(debug=True)