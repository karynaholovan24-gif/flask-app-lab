
from flask import Flask, render_template, request, flash

app = Flask(__name__)
app.secret_key = "lab2-secret-key"


@app.route("/")
@app.route("/resume")
def resume():
    return render_template(
        "resume.html",
        title="Моє резюме",
        page="resume"
    )


@app.route("/contacts", methods=["GET", "POST"])
def contacts():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()

        if name and email and message:
            flash(
                "Дякую! Форму перевірено.",
                "success"
            )
        else:
            flash("Заповніть усі поля форми.", "danger")

    return render_template(
        "contacts.html",
        title="Контакти",
        page="contacts"
    )


if __name__ == "__main__":
    app.run(debug=True)
