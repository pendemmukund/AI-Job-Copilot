from flask import Flask,render_template,request

app = Flask(__name__)


@app.route("/",methods=["GET", "POST"])
def home():
    if request.method == "POST":
        job_description = request.form["job_description"]
        print(job_description)
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
