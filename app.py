from flask import Flask,render_template,request

app = Flask(__name__)


@app.route("/",methods=["GET", "POST"])
def home():
    if request.method == "POST":
        job_description = request.form["job_description"]
        resume = request.files['resume']
        print(job_description)
        resume.save("uploads/" + resume.filename)
        print("Resume saved:", resume.filename)
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
