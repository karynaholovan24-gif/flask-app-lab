from flask_wtf import FlaskForm
from sqlalchemy import func, select
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    Regexp,
    ValidationError,
)

from app import db
from .models import User


class RegistrationForm(FlaskForm):
    username = StringField(
        "Ім’я користувача",
        validators=[
            DataRequired(message="Введіть ім’я користувача."),
            Length(min=4, max=14, message="Ім’я має містити від 4 до 14 символів."),
            Regexp(
                r"^[A-Za-z][A-Za-z0-9._]*$",
                message="Ім’я має починатися з літери та містити лише латинські літери, цифри, крапки або підкреслення.",
            ),
        ],
    )
    email = StringField(
        "Електронна пошта",
        validators=[DataRequired(message="Введіть електронну пошту."), Email(), Length(max=255)],
    )
    password = PasswordField(
        "Пароль",
        validators=[DataRequired(message="Введіть пароль."), Length(min=6, message="Пароль має містити щонайменше 6 символів.")],
    )
    confirm_password = PasswordField(
        "Підтвердження пароля",
        validators=[
            DataRequired(message="Підтвердьте пароль."),
            EqualTo("password", message="Паролі не збігаються."),
        ],
    )
    submit = SubmitField("Зареєструватися")

    def validate_username(self, field):
        exists = db.session.scalar(select(User.id).where(User.username == field.data))
        if exists is not None:
            raise ValidationError("Це ім’я користувача вже зайняте.")

    def validate_email(self, field):
        exists = db.session.scalar(
            select(User.id).where(func.lower(User.email) == (field.data or "").strip().lower())
        )
        if exists is not None:
            raise ValidationError("Користувач із такою електронною поштою вже зареєстрований.")

    def validate_password(self, field):
        if field.data and len(field.data.encode("utf-8")) > 72:
            raise ValidationError("Пароль має містити не більше 72 байтів UTF-8.")


class LoginForm(FlaskForm):
    email = StringField(
        "Електронна пошта",
        validators=[DataRequired(message="Введіть електронну пошту."), Email()],
    )
    password = PasswordField(
        "Пароль",
        validators=[DataRequired(message="Введіть пароль.")],
    )
    remember = BooleanField("Запам’ятати мене")
    submit = SubmitField("Увійти")

    def validate_password(self, field):
        if field.data and len(field.data.encode("utf-8")) > 72:
            raise ValidationError("Пароль має містити не більше 72 байтів UTF-8.")
