# AI Job Intelligence & Career Copilot

## About the Project

AI Job Intelligence & Career Copilot is a web application built using Python and Flask. It helps users check how well their resume matches a job description.

The application finds the skills already present in a resume, shows the missing skills, and uses AI to suggest what the user can learn next. It also provides a learning roadmap and allows users to download their analysis report.

I built this project to practise Python web development and learn how AI can be used to help job seekers.

## 🚀 Features

- Upload a resume in PDF format.
- Extract skills from the resume.
- Enter a job description for analysis.
- Calculate the resume's skill match percentage.
- Show matched and missing required skills.
- Identify preferred skills that the user has or needs to learn.
- Generate career suggestions using AI.
- Display a learning roadmap based on missing skills.
- Download the job analysis report as a text file.

## 📸 Screenshots

### Home Page

![Home Page](screenshots/home.png)

### Resume Upload Page

![Resume Upload](screenshots/home2.png)

### Skill Analysis Results

![Skill Analysis](screenshots/skill_analysis.png)

### Skill Analysis — Additional View

![Skill Analysis Details](screenshots/skills_analysis.png)

### Learning Roadmap

![Learning Roadmap](screenshots/roadmap.png)

### Learning Roadmap — Additional View

![Learning Roadmap Details](screenshots/roadmap2.png)

### Learning Roadmap — Further Details

![Learning Roadmap More Details](screenshots/roadmap3.png)

### Learning Roadmap — Final View

![Learning Roadmap Final View](screenshots/roadmap4.png)

### Download Analysis Report

![Download Report](screenshots/download.png)

## 🛠️ Technologies Used

- **Python** – Main programming language.
- **Flask** – Used to build the web application.
- **HTML and CSS** – Used to create and style the web pages.
- **PyPDF2** – Used to read text from PDF resumes.
- **Ollama (Llama 3.2)** – Used to generate AI career suggestions locally.
- **Markdown and Bleach** – Used to format and sanitize the AI-generated content.
- **Git and GitHub** – Used to manage and store the project code.

## ⚙️ How It Works

1. The user uploads a resume in PDF format.
2. The user enters the job description.
3. The application extracts text and identifies skills from the resume.
4. It compares the resume skills with the required and preferred skills in the job description.
5. It calculates the percentage of required skills that match.
6. It shows the skills the user has and the skills that are missing.
7. The AI generates suggestions to help the user improve.
8. A learning roadmap shows which skills to focus on first.
9. The user can download the analysis report.

## 📂 Project Structure

```text
AI-Job-Copilot/
│
├── app.py
├── templates/
│   ├── index.html
│   └── results.html
├── static/
│   └── css/
│       └── style.css
├── uploads/
├── .gitignore
└── README.md
```

## 💻 How to Run the Project

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd AI-Job-Copilot
```

Replace `YOUR_GITHUB_REPOSITORY_URL` with your actual GitHub repository URL.

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install the required packages

```bash
pip install Flask PyPDF2 ollama Markdown bleach
```

### 4. Set up Ollama

Install Ollama from [the official download page](https://ollama.com/download).

Download the Llama 3.2 model:

```bash
ollama pull llama3.2
```

Make sure Ollama is running before using the AI analysis feature.

### 5. Start the application

```bash
python app.py
```

Open this address in your browser:

[http://127.0.0.1:5000/](http://127.0.0.1:5000/)

## 📚 What I Learned

While building this project, I practised:

- Building a web application using Flask.
- Uploading and reading PDF files.
- Extracting and comparing skills using Python.
- Working with HTML templates and CSS.
- Connecting a local AI model using Ollama.
- Handling errors and displaying results.
- Using Git and GitHub to manage project changes.

## 🔮 Future Improvements

- Add support for more resume file formats.
- Improve skill extraction from resumes and job descriptions.
- Generate downloadable PDF reports.
- Add interview questions based on the job description.
- Improve the learning roadmap with more detailed study plans.

## 👨‍💻 Author

**Mukund P.**

GitHub: [pendemmukund](https://github.com/pendemmukund)
