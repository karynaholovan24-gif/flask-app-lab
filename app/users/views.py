from flask import render_template, request, redirect, url_for
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