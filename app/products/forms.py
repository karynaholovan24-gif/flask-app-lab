from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    IntegerField,
    StringField,
    TextAreaField,
    DecimalField,
    SelectField,
    SubmitField
)
from wtforms.validators import (
    DataRequired,
    InputRequired,
    Length,
    NumberRange,
    Optional
)


class ProductForm(FlaskForm):
    name = StringField(
        "Назва товару",
        validators=[
            DataRequired(message="Введіть назву товару."),
            Length(
                min=3,
                message="Назва повинна містити щонайменше 3 символи."
            )
        ]
    )

    content = TextAreaField(
        "Опис товару",
        validators=[
            DataRequired(message="Введіть опис товару.")
        ],
        render_kw={"rows": 5, "cols": 40}
    )

    price = DecimalField(
        "Ціна",
        places=2,
        validators=[
            InputRequired(message="Введіть ціну."),
            NumberRange(
                min=0.01,
                message="Ціна повинна бути більшою за 0."
            )
        ]
    )

    category = SelectField(
        "Категорія",
        choices=[
            ("electronics", "Електроніка"),
            ("clothing", "Одяг"),
            ("books", "Книги"),
            ("other", "Інше")
        ],
        validators=[
            DataRequired(message="Оберіть категорію.")
        ]
    )

    quantity = IntegerField(
        "Кількість",
        validators=[
            InputRequired(message="Введіть кількість."),
            NumberRange(
                min=0,
                message="Кількість не може бути від'ємною."
            )
        ]
    )

    image = FileField(
        "Зображення товару",
        validators=[
            Optional(),
            FileAllowed(
                ["jpg", "jpeg", "png"],
                "Дозволені лише зображення JPG, JPEG та PNG."
            )
        ]
    )

    submit = SubmitField("Зберегти товар")