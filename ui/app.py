from flask import Flask, render_template, request
from engine import evaluate, write_artifacts

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    artifacts = None
    job_text = ""

    if request.method == "POST":
        job_text = request.form.get("job_text", "")
        result = evaluate(job_text)
        artifacts = write_artifacts(job_text, result)

    return render_template(
        "index.html",
        job_text=job_text,
        result=result,
        artifacts=artifacts
    )

if __name__ == "__main__":
    app.run(debug=True)
