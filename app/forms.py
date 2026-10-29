from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    EmailField,
    SelectField,
    TextAreaField,
    SubmitField
)
from wtforms.validators import DataRequired, Email, Length


class ContactForm(FlaskForm):
    name = StringField(
        "Ім'я",
        validators=[
            DataRequired(message="Введіть ім'я."),
            Length(min=2, max=100, message="Ім'я має містити від 2 до 100 символів.")
        ]
    )

    email = EmailField(
        "Email",
        validators=[
            DataRequired(message="Введіть email."),
            Email(message="Введіть коректну email-адресу.")
        ]
    )

    subject = SelectField(
        "Тема звернення",
        choices=[
            ("question", "Запитання"),
            ("cooperation", "Співпраця"),
            ("feedback", "Відгук"),
            ("other", "Інше")
        ],
        validators=[
            DataRequired(message="Оберіть тему звернення.")
        ]
    )

    message = TextAreaField(
        "Повідомлення",
        validators=[
            DataRequired(message="Введіть повідомлення."),
            Length(min=10, max=2000, message="Повідомлення має містити від 10 до 2000 символів.")
        ],
        render_kw={"rows": 5}
    )

    submit = SubmitField("Надіслати")