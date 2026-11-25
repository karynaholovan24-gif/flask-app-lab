from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DateTimeLocalField,
    SelectField,
    SelectMultipleField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Length


class PostForm(FlaskForm):
    title = StringField(
        "Назва допису",
        validators=[DataRequired(), Length(max=150)],
    )
    content = TextAreaField("Вміст допису", validators=[DataRequired()])
    enabled = BooleanField("Активний допис", default=True)
    publish_date = DateTimeLocalField(
        "Дата публікації",
        format="%Y-%m-%dT%H:%M",
        render_kw={"step": 60},
    )
    category = SelectField(
        "Категорія",
        choices=[
            ("news", "Новини"),
            ("publication", "Публікації"),
            ("tech", "Технології"),
            ("other", "Інше"),
        ],
        default="other",
    )
    author_id = SelectField(
        "Автор",
        coerce=int,
        validators=[DataRequired(message="Оберіть автора.")],
    )
    tags = SelectMultipleField("Теги", coerce=int)
    submit = SubmitField("Зберегти допис")
