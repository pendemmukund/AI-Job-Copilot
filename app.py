
from flask import Flask, render_template, request
from PyPDF2 import PdfReader
from werkzeug.utils import secure_filename
import ollama
import os
import re

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf"}


# Clean the extracted text
def clean_text(text):
    lines = text.splitlines()
    cleaned_lines = []

    for line in lines:
        line = line.strip()
        if line:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


# Extract sections from the resume
def extract_sections(text):
    sections = {
        "education": "",
        "skills": "",
        "projects": "",
        "experience": "",
        "certifications": ""
    }

    section_headers = {
        "education": "education",
        "skills": "skills",
        "technical skills": "skills",
        "projects": "projects",
        "experience": "experience",
        "professional experience": "experience",
        "certifications": "certifications",
        "certifications & leadership": "certifications"
    }

    current_section = None

    for line in text.splitlines():
        line = line.strip()
        line_lower = line.lower().rstrip(":")

        if line_lower in section_headers:
            current_section = section_headers[line_lower]
            continue

        if current_section and line:
            sections[current_section] += line + "\n"

    return sections


# Normalize different names for the same skill
def clean_skill(skill):
    skill = skill.strip()
    skill = skill.lstrip("-•*").strip()
    skill_lower = skill.lower()

    if re.search(r"\bpython\b", skill_lower):
        return "Python"

    elif re.search(r"\bflask\b", skill_lower):
        return "Flask"

    elif re.search(r"\bsql\b", skill_lower):
        return "SQL"

    elif re.search(r"\brest\s+apis?\b", skill_lower):
        return "REST API"

    elif (
        ("html" in skill_lower and "css" in skill_lower)
        or "html/css" in skill_lower
        or "html and css" in skill_lower
    ):
        return "HTML/CSS"

    elif re.fullmatch(r"html5?|css3?", skill_lower):
        return "HTML/CSS"

    elif (
        ("git" in skill_lower and "github" in skill_lower)
        or "git/github" in skill_lower
    ):
        return "Git/GitHub"

    elif skill_lower in ["git", "github"]:
        return "Git/GitHub"

    elif (
        "object-oriented" in skill_lower
        or "object oriented" in skill_lower
        or skill_lower == "oop"
        or "(oop)" in skill_lower
    ):
        return "OOP"

    elif (
        "problem-solving" in skill_lower
        or "problem solving" in skill_lower
        or "debugging" in skill_lower
    ):
        return "Problem-Solving & Debugging"

    elif re.search(r"\bpandas\b", skill_lower):
        return "Pandas"

    elif re.search(r"\bnumpy\b", skill_lower):
        return "NumPy"

    elif re.search(r"\bmatplotlib\b", skill_lower):
        return "Matplotlib"

    elif "machine learning" in skill_lower:
        return "Machine Learning"

    elif re.search(r"\bllm\b", skill_lower):
        return "LLM APIs"

    elif re.search(r"\bjavascript\b", skill_lower):
        return "JavaScript"

    elif re.search(r"\bstreamlit\b", skill_lower):
        return "Streamlit"

    elif re.search(r"\bpypdf2\b", skill_lower):
        return "PyPDF2"

    elif re.search(r"\bsqlite\b", skill_lower):
        return "SQLite"

    elif re.search(r"\bmysql\b", skill_lower):
        return "MySQL"

    elif "gemini" in skill_lower:
        return "Gemini API"

    elif re.search(r"\bdbms\b", skill_lower):
        return "DBMS"

    elif "data structures" in skill_lower:
        return "Data Structures & Algorithms"

    elif "backend" in skill_lower:
        return "Backend Development"

    elif "exception handling" in skill_lower:
        return "Exception Handling"

    elif re.search(r"\bartificial intelligence\b", skill_lower):
        return "AI"

    elif re.search(r"\bai\b", skill_lower):
        return "AI"

    return skill


# Extract skills from the resume's Skills section
def extract_resume_skills(text):
    sections = extract_sections(text)
    skills_text = sections["skills"]

    skills = []

    for line in skills_text.splitlines():
        line = line.strip()

        if not line:
            continue

        # Remove category labels such as "Languages:"
        if ":" in line:
            line = line.split(":", 1)[1]

        for skill in line.split(","):
            skill = skill.strip()

            if skill:
                skills.append(clean_skill(skill))

    return list(dict.fromkeys(skills))


# Find known skills mentioned in a job-description line
def extract_skills_from_line(line):
    line_lower = line.lower()
    skills = []

    skill_patterns = [
        (r"\bpython\b", "Python"),
        (r"\bflask\b", "Flask"),
        (r"\bsql\b", "SQL"),
        (r"\brest\s+apis?\b", "REST API"),
        (r"\bhtml\b.*\bcss\b|\bcss\b.*\bhtml\b", "HTML/CSS"),
        (r"\bgit\b.*\bgithub\b|\bgithub\b.*\bgit\b", "Git/GitHub"),
        (r"\bobject[- ]oriented\b|\boop\b", "OOP"),
        (r"\bproblem[- ]solving\b|\bdebugging\b",
         "Problem-Solving & Debugging"),
        (r"\bpandas\b", "Pandas"),
        (r"\bnumpy\b", "NumPy"),
        (r"\bmatplotlib\b", "Matplotlib"),
        (r"\bmachine learning\b", "Machine Learning"),
        (r"\bjavascript\b", "JavaScript"),
        (r"\bstreamlit\b", "Streamlit"),
        (r"\bmysql\b", "MySQL"),
        (r"\bsqlite\b", "SQLite"),
        (r"\bdbms\b", "DBMS"),
        (r"\bdata structures\b", "Data Structures & Algorithms"),
        (r"\bbackend\b", "Backend Development"),
        (r"\bexception handling\b", "Exception Handling"),
        (r"\bartificial intelligence\b|\bai\b", "AI"),
        (r"\bllm\b", "LLM APIs")
    ]

    for pattern, skill_name in skill_patterns:
        if re.search(pattern, line_lower):
            skills.append(skill_name)

    # Use normalization for other individual skill names
    if not skills:
        normalized = clean_skill(line)

        if normalized != line:
            skills.append(normalized)
        elif line:
            skills.append(line.strip())

    return list(dict.fromkeys(skills))


# Extract required and preferred skills from the job description
def extract_job_skills(job_description):
    required_skills = []
    preferred_skills = []

    current_section = None

    for line in job_description.splitlines():
        line = line.strip()
        line = line.lstrip("-•*").strip()

        if not line:
            continue

        line_lower = line.lower().rstrip(":")

        if line_lower in ["required skills", "required"]:
            current_section = "required"
            continue

        elif line_lower in [
            "good to have",
            "preferred skills",
            "nice to have"
        ]:
            current_section = "preferred"
            continue

        elif line_lower in [
            "education",
            "experience",
            "responsibilities",
            "qualifications"
        ]:
            current_section = None
            continue

        if current_section == "required":
            required_skills.extend(extract_skills_from_line(line))

        elif current_section == "preferred":
            preferred_skills.extend(extract_skills_from_line(line))

    return {
        "required_skills": list(dict.fromkeys(required_skills)),
        "preferred_skills": list(dict.fromkeys(preferred_skills))
    }


# Compare resume skills with job requirements
def compare_skills(resume_skills, job_skills):
    resume_set = {
        clean_skill(skill).lower()
        for skill in resume_skills
    }

    job_set = {
        clean_skill(skill).lower()
        for skill in job_skills
    }

    matched_skills = resume_set.intersection(job_set)
    missing_skills = job_set - resume_set

    # Convert results back to readable skill names
    display_names = {}

    for skill in resume_skills + job_skills:
        normalized = clean_skill(skill).lower()
        display_names[normalized] = clean_skill(skill)

    matched_skills = {
        display_names.get(skill, skill.title())
        for skill in matched_skills
    }

    missing_skills = {
        display_names.get(skill, skill.title())
        for skill in missing_skills
    }

    return matched_skills, missing_skills


# Calculate required-skill match percentage
def calculate_match_percentage(matched_skills, job_skills):
    unique_job_skills = {
        clean_skill(skill).lower()
        for skill in job_skills
    }

    if not unique_job_skills:
        return 0

    matched = {
        clean_skill(skill).lower()
        for skill in matched_skills
    }

    matched_count = len(matched.intersection(unique_job_skills))

    percentage = (matched_count / len(unique_job_skills)) * 100

    return round(percentage, 2)


# Classify the match strength
def get_match_strength(match_percentage):
    if match_percentage >= 80:
        return "Strong Match"

    elif match_percentage >= 50:
        return "Moderate Match"

    return "Weak Match"


# Generate career analysis using local Ollama
def generate_ai_analysis(
    matched_skills,
    missing_skills,
    match_percentage
):
    prompt = f"""
You are a career assistant helping a fresher prepare for a job.

Skill match percentage: {match_percentage}%

Matched skills:
{", ".join(sorted(matched_skills)) or "None"}

Missing skills:
{", ".join(sorted(missing_skills)) or "None"}

Provide a concise analysis with these sections:
1. Overall assessment
2. Strong areas
3. Skills to improve
4. One practical recommendation

Use simple language.
Do not invent skills the candidate has.
Do not guarantee that the candidate will get the job.
"""

    try:
        response = ollama.chat(
            model="llama3.2",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response["message"]["content"]

    except Exception as error:
        print("Ollama error:", error)

        return (
            "AI analysis is currently unavailable. "
            "Please ensure Ollama is running and the "
            "llama3.2 model is installed. "
            "Your skill-matching results are still available."
        )


# Main Flask route
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":

        job_description = request.form.get(
            "job_description", ""
        )

        if not job_description.strip():
            return "Please enter a job description.", 400

        resume = request.files.get("resume")

        if not resume or not resume.filename:
            return "Please select a resume.", 400

        filename = secure_filename(resume.filename)

        if not filename.lower().endswith(".pdf"):
            return "Please upload a PDF resume.", 400

        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        file_path = os.path.join(UPLOAD_FOLDER, filename)
        resume.save(file_path)

        try:
            reader = PdfReader(file_path)

            extracted_text = ""

            for page in reader.pages:
                page_text = page.extract_text()

                if page_text:
                    extracted_text += page_text + "\n"

        except Exception as error:
            print("PDF reading error:", error)
            return (
                "Unable to read this PDF. "
                "Please upload a valid PDF resume.",
                400
            )

        extracted_text = clean_text(extracted_text)

        if not extracted_text.strip():
            return (
                "No readable text was found in this PDF. "
                "Please upload a text-based PDF resume.",
                400
            )

        # Extract resume and job skills
        resume_skills = extract_resume_skills(extracted_text)
        job_skills = extract_job_skills(job_description)

        required_skills = job_skills["required_skills"]

        # Compare skills
        matched_skills, missing_skills = compare_skills(
            resume_skills,
            required_skills
        )

        # Calculate score and strength
        match_percentage = calculate_match_percentage(
            matched_skills,
            required_skills
        )

        match_strength = get_match_strength(match_percentage)

        # Generate local AI analysis
        ai_analysis = generate_ai_analysis(
            matched_skills,
            missing_skills,
            match_percentage
        )

        # Display the results
        return render_template(
            "results.html",
            matched_skills=sorted(matched_skills),
            missing_skills=sorted(missing_skills),
            match_percentage=match_percentage,
            match_strength=match_strength,
            ai_analysis=ai_analysis
        )

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
