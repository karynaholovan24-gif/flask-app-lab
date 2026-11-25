from flask import (
    flash,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import func, select

from app import db
from . import users_bp
from .forms import LoginForm, RegistrationForm
from .models import User


@users_bp.route("/hi/<name>")
def greetings(name):
    age = request.args.get("age")
    return render_template(
        "users/hi.html",
        name=name.upper(),
        age=age,
        title="Привітання",
    )


@users_bp.route("/admin")
def admin():
    return redirect(url_for("users.greetings", name="Administrator", age=45))


@users_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("users.account"))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data.strip(),
            email=form.email.data.strip().lower(),
            password="",
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash("Реєстрацію успішно завершено. Ви увійшли в систему.", "success")
        return redirect(url_for("users.account"))

    return render_template("users/register.html", title="Реєстрація", form=form)


@users_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("users.account"))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        user = db.session.scalar(
            select(User).where(func.lower(User.email) == email)
        )
        if user is not None and user.check_password(form.password.data):
            if not user.password.startswith(("$2a$", "$2b$", "$2y$")):
                user.set_password(form.password.data)
                db.session.commit()
            login_user(user, remember=form.remember.data)
            flash("Вхід виконано успішно!", "success")
            return redirect(url_for("users.account"))

        flash("Неправильна електронна пошта або пароль.", "danger")

    return render_template("users/login.html", title="Вхід", form=form)


@users_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("Ви вийшли із системи.", "info")
    return redirect(url_for("users.login"))


@users_bp.route("/account")
@login_required
def account():
    return render_template("users/account.html", title="Особистий кабінет")


@users_bp.route("/list")
@login_required
def user_list():
    users = db.session.scalars(select(User).order_by(User.id)).all()
    return render_template(
        "users/list.html",
        title="Зареєстровані користувачі",
        users=users,
        user_count=len(users),
    )


@users_bp.route("/profile")
@login_required
def profile():
    cookies = {
        key: value
        for key, value in request.cookies.items()
        if key not in {"session", "remember_token"}
    }
    return render_template(
        "users/profile.html",
        title="Мій профіль",
        username=current_user.username,
        cookies=cookies,
    )


@users_bp.route("/add-cookie", methods=["POST"])
@login_required
def add_cookie():
    key = request.form.get("key", "").strip()
    value = request.form.get("value", "")
    max_age_text = request.form.get("max_age", "3600").strip()

    if not key:
        flash("Введіть назву cookie!", "danger")
        return redirect(url_for("users.profile"))
    if key in {"session", "remember_token"}:
        flash("Цю службову cookie змінювати не можна!", "danger")
        return redirect(url_for("users.profile"))

    try:
        max_age = int(max_age_text)
        if max_age <= 0:
            raise ValueError
    except ValueError:
        flash("Час зберігання має бути додатним цілим числом!", "danger")
        return redirect(url_for("users.profile"))

    response = make_response(redirect(url_for("users.profile")))
    response.set_cookie(
        key,
        value,
        max_age=max_age,
        httponly=True,
        samesite="Lax",
    )
    flash(f"Cookie '{key}' успішно додано!", "success")
    return response


@users_bp.route("/delete-cookie", methods=["POST"])
@login_required
def delete_cookie():
    key = request.form.get("key", "").strip()
    if not key:
        flash("Введіть назву cookie для видалення!", "danger")
        return redirect(url_for("users.profile"))
    if key in {"session", "remember_token"}:
        flash("Службову cookie видаляти не можна!", "danger")
        return redirect(url_for("users.profile"))
    if key not in request.cookies:
        flash(f"Cookie '{key}' не знайдено!", "warning")
        return redirect(url_for("users.profile"))

    flash(f"Cookie '{key}' успішно видалено!", "success")
    response = make_response(redirect(url_for("users.profile")))
    response.delete_cookie(key)
    return response


@users_bp.route("/delete-all-cookies", methods=["POST"])
@login_required
def delete_all_cookies():
    response = make_response(redirect(url_for("users.profile")))
    user_cookies = [
        key for key in request.cookies
        if key not in {"session", "remember_token"}
    ]
    for key in user_cookies:
        response.delete_cookie(key)

    if user_cookies:
        flash("Усі користувацькі cookies успішно видалено!", "success")
    else:
        flash("Немає cookies для видалення!", "info")
    return response


@users_bp.route("/set-theme/<theme>")
def set_theme(theme):
    if theme not in ["light", "dark"]:
        flash("Невідома тема оформлення!", "danger")
        return redirect(url_for("main.home"))

    session["theme"] = theme
    flash("Темну тему увімкнено!" if theme == "dark" else "Світлу тему увімкнено!", "success")
    return redirect(request.referrer or url_for("main.home"))
