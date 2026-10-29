import logging
from pathlib import Path

from flask import render_template, redirect, url_for, flash, request

from . import app
from .forms import ContactForm


# Налаштування журналу повідомлень
log_dir = Path(app.root_path).parent / "logs"
log_dir.mkdir(exist_ok=True)

contact_logger = logging.getLogger("contact_form")
contact_logger.setLevel(logging.INFO)

if not contact_logger.handlers:
    file_handler = logging.FileHandler(
        log_dir / "contacts.log",
        encoding="utf-8"
    )
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(message)s")
    )
    contact_logger.addHandler(file_handler)


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
    form = ContactForm()

    if form.validate_on_submit():
        try:
            contact_logger.info(
                "Ім'я: %s | Email: %s | Тема: %s | Повідомлення: %s",
                form.name.data,
                form.email.data,
                form.subject.data,
                form.message.data
            )

            flash(
                "Повідомлення успішно надіслано та записано в журнал!",
                "success"
            )

            return redirect(url_for("contacts"))

        except OSError:
            app.logger.exception("Помилка запису контактної форми")

            flash(
                "Не вдалося зберегти повідомлення. Спробуйте ще раз.",
                "danger"
            )

    elif request.method == "POST":
        flash(
            "Форма містить помилки. Перевірте введені дані.",
            "danger"
        )

    return render_template(
        "contacts.html",
        title="Контакти",
        page="contacts",
        form=form
    )