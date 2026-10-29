from flask import render_template, request, redirect, url_for, session, flash, make_response
from . import users_bp


@users_bp.route("/hi/<name>")
def greetings(name):
    age = request.args.get("age")

    return render_template(
        "users/hi.html",
        name=name.upper(),
        age=age,
        title="Привітання"
    )


@users_bp.route("/admin")
def admin():
    return redirect(
        url_for(
            "users.greetings",
            name="Administrator",
            age=45
        )
    )

@users_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if username == "admin" and password == "12345":
            session["username"] = username
            flash("Вхід виконано успішно!", "success")
            return redirect(url_for("users.profile"))
        else:
            flash("Неправильний логін або пароль!", "danger")

    return render_template(
        "users/login.html",
        title="Вхід"
    )

@users_bp.route("/profile")
def profile():
    if "username" not in session:
        flash("Спочатку увійдіть у систему!", "warning")
        return redirect(url_for("users.login"))

    cookies = {
        key: value
        for key, value in request.cookies.items()
        if key != "session"
    }

    return render_template(
        "users/profile.html",
        title="Мій профіль",
        username=session["username"],
        cookies=cookies
    )

@users_bp.route("/logout", methods=["POST"])
def logout():
    session.pop("username", None)
    flash("Ви успішно вийшли із системи!", "info")
    return redirect(url_for("users.login"))

@users_bp.route("/add-cookie", methods=["POST"])
def add_cookie():
    if "username" not in session:
        flash("Спочатку увійдіть у систему!", "warning")
        return redirect(url_for("users.login"))

    key = request.form.get("key", "").strip()
    value = request.form.get("value", "")
    max_age_text = request.form.get("max_age", "3600").strip()

    if not key:
        flash("Введіть назву cookie!", "danger")
        return redirect(url_for("users.profile"))

    if key == "session":
        flash("Cookie з назвою 'session' змінювати не можна!", "danger")
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
        samesite="Lax"
    )

    flash(f"Cookie '{key}' успішно додано!", "success")

    return response

@users_bp.route("/delete-cookie", methods=["POST"])
def delete_cookie():
    if "username" not in session:
        flash("Спочатку увійдіть у систему!", "warning")
        return redirect(url_for("users.login"))

    key = request.form.get("key", "").strip()

    if not key:
        flash("Введіть назву cookie для видалення!", "danger")
        return redirect(url_for("users.profile"))

    if key == "session":
        flash("Службову cookie 'session' видаляти не можна!", "danger")
        return redirect(url_for("users.profile"))

    if key not in request.cookies:
        flash(f"Cookie '{key}' не знайдено!", "warning")
        return redirect(url_for("users.profile"))

    flash(f"Cookie '{key}' успішно видалено!", "success")

    response = make_response(redirect(url_for("users.profile")))
    response.delete_cookie(key)

    return response

@users_bp.route("/delete-all-cookies", methods=["POST"])
def delete_all_cookies():
    if "username" not in session:
        flash("Спочатку увійдіть у систему!", "warning")
        return redirect(url_for("users.login"))

    response = make_response(redirect(url_for("users.profile")))

    count = 0

    for key in request.cookies:
        if key != "session":
            response.delete_cookie(key)
            count += 1

    if count > 0:
        flash("Усі користувацькі cookies успішно видалено!", "success")
    else:
        flash("Немає cookies для видалення!", "info")

    return response

@users_bp.route("/set-theme/<theme>")
def set_theme(theme):
    if theme not in ["light", "dark"]:
        flash("Невідома тема оформлення!", "danger")
        return redirect(url_for("home"))

    session["theme"] = theme

    if theme == "dark":
        flash("Темну тему увімкнено!", "success")
    else:
        flash("Світлу тему увімкнено!", "success")

    return redirect(request.referrer or url_for("home"))