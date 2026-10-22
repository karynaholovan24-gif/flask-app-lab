from flask import render_template, request, flash
from . import app


@app.route("/")
def home():
    return render_template(
        "homepage.html",
        title="Головна",
        page="home"
    )


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
            flash("Дякую! Форму перевірено.", "success")
        else:
            flash("Заповніть усі поля форми.", "danger")

    return render_template(
        "contacts.html",
        title="Контакти",
        page="contacts"
    )