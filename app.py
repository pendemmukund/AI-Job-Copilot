import markdown
from markupsafe import Markup
from flask import Flask, render_template, request
from PyPDF2 import PdfReader
from werkzeug.utils import secure_filename
import ollama
import os
import re
from flask import Flask, render_template, request, make_response

import bleach


app = Flask(__name__)

UPLOAD_FOLDER = "uploads"


# Clean extracted resume text
def clean_text(text):
    cleaned_lines = []

    for line in text.splitlines():
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
        line_lower = line.strip().lower().rstrip(":")

        if line_lower in section_headers:
            current_section = section_headers[line_lower]
            continue

        if current_section:
            sections[current_section] += line.strip() + "\n"

    return sections


# Normalize skill names
def clean_skill(skill):
    skill = skill.strip().lstrip("-•*").strip()
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

    elif "artificial intelligence" in skill_lower:
        return "AI"

    elif re.search(r"\bai\b", skill_lower):
        return "AI"

    elif re.search(r"\bllm\b", skill_lower):
        return "LLM APIs"

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

        # Remove labels such as "Languages:" or "Frameworks:"
        if ":" in line:
            line = line.split(":", 1)[1]

        for skill in line.split(","):
            skill = skill.strip()

            if skill:
                skills.append(clean_skill(skill))

    return list(dict.fromkeys(skills))


# Extract known skills from a job-description line
def extract_skills_from_line(line):
    line_lower = line.lower()
    skills = []

    skill_patterns = [
        (r"\bpython\b", "Python"),
        (r"\bflask\b", "Flask"),
        (r"\bsql\b", "SQL"),
        (r"\brest\s+apis?\b", "REST API"),
        (
            r"\bhtml\b.*\bcss\b|\bcss\b.*\bhtml\b",
            "HTML/CSS"
        ),
        (
            r"\bgit\b.*\bgithub\b|\bgithub\b.*\bgit\b",
            "Git/GitHub"
        ),
        (
            r"\bobject[- ]oriented\b|\boop\b",
            "OOP"
        ),
        (
            r"\bproblem[- ]solving\b|\bdebugging\b",
            "Problem-Solving & Debugging"
        ),
        (r"\bpandas\b", "Pandas"),
        (r"\bnumpy\b", "NumPy"),
        (r"\bmatplotlib\b", "Matplotlib"),
        (r"\bmachine learning\b", "Machine Learning"),
        (r"\bjavascript\b", "JavaScript"),
        (r"\bstreamlit\b", "Streamlit"),
        (r"\bmysql\b", "MySQL"),
        (r"\bsqlite\b", "SQLite"),
        (r"\bdbms\b", "DBMS"),
        (
            r"\bdata structures\b",
            "Data Structures & Algorithms"
        ),
        (r"\bbackend\b", "Backend Development"),
        (
            r"\bexception handling\b",
            "Exception Handling"
        ),
        (
            r"\bartificial intelligence\b|\bai\b",
            "AI"
        ),
        (r"\bllm\b", "LLM APIs")
    ]

    for pattern, skill_name in skill_patterns:
        if re.search(pattern, line_lower):
            skills.append(skill_name)

    # Normalize a line if no known skill was detected
    if not skills:
        normalized = clean_skill(line)

        if normalized != line:
            skills.append(normalized)

    return list(dict.fromkeys(skills))


# Extract required and preferred job skills
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
            required_skills.extend(
                extract_skills_from_line(line)
            )

        elif current_section == "preferred":
            preferred_skills.extend(
                extract_skills_from_line(line)
            )

    return {
        "required_skills": list(dict.fromkeys(required_skills)),
        "preferred_skills": list(dict.fromkeys(preferred_skills))
    }


# Compare resume skills with a list of job skills
def compare_skills(resume_skills, job_skills):
    resume_map = {
        clean_skill(skill).lower(): clean_skill(skill)
        for skill in resume_skills
    }

    job_map = {
        clean_skill(skill).lower(): clean_skill(skill)
        for skill in job_skills
    }

    matched_keys = set(resume_map).intersection(job_map)
    missing_keys = set(job_map) - set(resume_map)

    matched_skills = {
        job_map[key] for key in matched_keys
    }

    missing_skills = {
        job_map[key] for key in missing_keys
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

    matched_keys = {
        clean_skill(skill).lower()
        for skill in matched_skills
    }

    matched_count = len(
        matched_keys.intersection(unique_job_skills)
    )

    percentage = (
        matched_count / len(unique_job_skills)
    ) * 100

    return round(percentage, 2)


# Classify resume strength
def get_match_strength(match_percentage):
    if match_percentage >= 80:
        return "Strong Match"

    elif match_percentage >= 50:
        return "Moderate Match"

    return "Weak Match"

def generate_learning_roadmap(missing_skills, missing_preferred_skills):
    roadmap = []

    priority_skills = sorted(missing_skills)
    optional_skills = sorted(missing_preferred_skills)

    if priority_skills:
        roadmap.append({
            "priority": "High",
            "title": "Learn required skills",
            "skills": priority_skills,
            "description": "Focus on these skills first because they are required for the job."
        })

    if optional_skills:
        roadmap.append({
            "priority": "Medium",
            "title": "Learn preferred skills",
            "skills": optional_skills,
            "description": "Study these after the required skills. They can strengthen your profile."
        })

    if not roadmap:
        roadmap.append({
            "priority": "Low",
            "title": "Strengthen your existing skills",
            "skills": [],
            "description": "No missing skills were detected. Practise interview questions and build a project related to this role."
        })

    return roadmap


# Generate AI career analysis using local Ollama

def generate_ai_analysis(
    matched_skills,
    missing_skills,
    match_percentage,
    matched_preferred_skills,
    missing_preferred_skills
):
    prompt = f"""
You are a career advisor helping a fresher prepare for a job.

Required-skill match: {match_percentage}%

Matched required skills:
{", ".join(sorted(matched_skills)) or "None"}

Missing required skills:
{", ".join(sorted(missing_skills)) or "None"}

Preferred skills already present:
{", ".join(sorted(matched_preferred_skills)) or "None"}

Missing preferred skills:
{", ".join(sorted(missing_preferred_skills)) or "None"}

Write a practical career analysis for this candidate.

Include these sections:
1. Overall Assessment
2. Existing Strengths
3. Priority Skills to Improve
4. Recommended Learning Order
5. One Practical Next Step

Rules:
- Prioritize missing required skills over preferred skills.
- Treat preferred skills as optional.
- Recommend only skills listed above.
- Do not claim the candidate has skills that are missing.
- Use simple language suitable for a fresher.
- Keep the response concise and specific.
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

        analysis = response["message"]["content"].strip()

        if analysis:
            return analysis

        return "The AI returned an empty response. Please try again."

    except Exception as error:
        print("Ollama error:", error)

        return (
            "AI recommendations are temporarily unavailable. "
            "Please ensure Ollama is running and try again. "
            "Your skill-matching results are still available."
        )



# Main Flask route
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":

        # Get job description
        job_description = request.form.get(
            "job_description", ""
        )

        if not job_description.strip():
            return "Please enter a job description.", 400

        # Get uploaded resume
        resume = request.files.get("resume")

        if not resume or not resume.filename:
            return "Please select a resume.", 400

        filename = secure_filename(resume.filename)

        if not filename.lower().endswith(".pdf"):
            return "Please upload a PDF resume.", 400

        # Save resume
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        file_path = os.path.join(UPLOAD_FOLDER, filename)
        resume.save(file_path)

        # Extract text from PDF
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

        # 1. Extract resume and job skills
        resume_skills = extract_resume_skills(extracted_text)
        job_skills = extract_job_skills(job_description)

        required_skills = job_skills["required_skills"]
        preferred_skills = job_skills["preferred_skills"]

        # 2. Compare required skills
        matched_skills, missing_skills = compare_skills(
            resume_skills,
            required_skills
        )

        # 3. Compare preferred skills
        matched_preferred_skills, missing_preferred_skills = (
            compare_skills(
                resume_skills,
                preferred_skills
            )
        )

        # 4. Calculate percentage using required skills only
        match_percentage = calculate_match_percentage(
            matched_skills,
            required_skills
        )

        # 5. Calculate resume strength
        match_strength = get_match_strength(match_percentage)

        learning_roadmap = generate_learning_roadmap(
            missing_skills,
            missing_preferred_skills
        )

        # 6. Generate AI analysis        
        ai_analysis = generate_ai_analysis(
            matched_skills,
            missing_skills,
            match_percentage,
            matched_preferred_skills,
            missing_preferred_skills
        )

        # Handle an empty AI response
        if not ai_analysis or not ai_analysis.strip():
            ai_analysis = (
                "AI analysis is currently unavailable. "
                "Please check that Ollama is running and try again."
            )

        # Convert Markdown into HTML and sanitize the generated HTML
        allowed_tags = [
            "p", "strong", "em", "ul", "ol", "li",
            "h1", "h2", "h3", "h4", "blockquote",
            "code", "pre", "br"
        ]

        ai_analysis_html = Markup(
            bleach.clean(
                markdown.markdown(ai_analysis),
                tags=allowed_tags,
                attributes={},
                strip=True
            )
        )


        ai_analysis_html = Markup(
            markdown.markdown(ai_analysis)
        )
        # 7. Render results only after all variables are assigned
        
        return render_template(
            "results.html",
            matched_skills=sorted(matched_skills),
            missing_skills=sorted(missing_skills),
            match_percentage=match_percentage,
            match_strength=match_strength,
            ai_analysis=ai_analysis_html,
            matched_preferred_skills=sorted(matched_preferred_skills),
            missing_preferred_skills=sorted(missing_preferred_skills),
            learning_roadmap=learning_roadmap
        )


    return render_template("index.html")


@app.route("/download-report", methods=["POST"])
def download_report():
    report = request.form.get("report", "")

    if not report.strip():
        return "No report content available.", 400

    response = make_response(report)
    response.headers["Content-Type"] = "text/plain; charset=utf-8"
    response.headers["Content-Disposition"] = (
        "attachment; filename=job_analysis_report.txt"
    )

    return response


if __name__ == "__main__":
    app.run(debug=True)


