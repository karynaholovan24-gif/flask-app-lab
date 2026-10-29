from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    EmailField,
    SelectField,
    TextAreaField,
    SubmitField
)
from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    Optional,
    Regexp
)


class ContactForm(FlaskForm):
    name = StringField(
        "Ім'я",
        validators=[
            DataRequired(message="Введіть ім'я."),
            Length(
                min=4,
                max=10,
                message="Ім'я має містити від 4 до 10 символів."
            )
        ]
    )

    email = EmailField(
        "Email",
        validators=[
            DataRequired(message="Введіть email."),
            Email(message="Введіть коректну email-адресу.")
        ]
    )

    phone = StringField(
        "Телефон",
        validators=[
            Optional(),
            Regexp(
                r"^\+380\d{9}$",
                message="Телефон має бути у форматі +380XXXXXXXXX."
            )
        ],
        render_kw={
            "placeholder": "+380XXXXXXXXX",
            "maxlength": 13
        }
    )

    subject = SelectField(
        "Тема звернення",
        choices=[
            ("question", "Запитання"),
            ("cooperation", "Співпраця"),
            ("feedback", "Відгук"),
            ("other", "Інше")
        ]
    )

    message = TextAreaField(
        "Повідомлення",
        validators=[
            DataRequired(message="Введіть повідомлення."),
            Length(
                max=500,
                message="Повідомлення не може перевищувати 500 символів."
            )
        ],
        render_kw={
            "rows": 5,
            "maxlength": 500
        }
    )

    submit = SubmitField("Надіслати")