from datetime import datetime

import click
from flask import flash, redirect, render_template, request, url_for
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload

from app import db
from app.posts import post_bp
from app.posts.forms import PostForm
from app.posts.models import Post, Tag
from app.users.models import User


def populate_choices(form):
    users = db.session.scalars(select(User).order_by(User.username)).all()
    tags = db.session.scalars(select(Tag).order_by(Tag.name)).all()
    form.author_id.choices = [(user.id, f"{user.username} ({user.email})") for user in users]
    form.tags.choices = [(tag.id, tag.name) for tag in tags]


def selected_tags(form):
    if not form.tags.data:
        return []
    return db.session.scalars(
        select(Tag).where(Tag.id.in_(form.tags.data)).order_by(Tag.name)
    ).all()


def post_query():
    return select(Post).options(
        joinedload(Post.user),
        selectinload(Post.tags),
    )


@post_bp.route("/create", methods=["GET", "POST"])
def create_post():
    form = PostForm()
    populate_choices(form)

    if form.validate_on_submit():
        user = db.session.get(User, form.author_id.data)
        if user is None:
            form.author_id.errors.append("Обраний автор більше не існує.")
        else:
            post = Post(
                title=form.title.data,
                content=form.content.data,
                posted=form.publish_date.data or datetime.utcnow(),
                category=form.category.data,
                is_active=form.enabled.data,
                user=user,
                tags=selected_tags(form),
            )
            db.session.add(post)
            db.session.commit()
            flash("Допис успішно створено!", "success")
            return redirect(url_for("posts.post_detail", id=post.id))

    return render_template("posts/post_form.html", form=form)


@post_bp.route("", methods=["GET"])
@post_bp.route("/", methods=["GET"])
def list_posts():
    posts = db.session.scalars(
        post_query()
        .where(Post.is_active.is_(True))
        .order_by(Post.posted.desc())
    ).all()
    return render_template("posts/post_list.html", posts=posts)


@post_bp.route("/author/<int:user_id>", methods=["GET"])
def posts_by_author(user_id):
    user = db.get_or_404(User, user_id)
    posts = db.session.scalars(
        post_query().where(Post.user_id == user.id).order_by(Post.posted.desc())
    ).all()
    return render_template("posts/post_list.html", posts=posts, author=user)


@post_bp.route("/<int:id>", methods=["GET"])
def post_detail(id):
    post = db.session.scalar(post_query().where(Post.id == id))
    if post is None:
        from flask import abort
        abort(404)
    return render_template("posts/post_detail.html", post=post)


@post_bp.route("/<int:id>/update", methods=["GET", "POST"])
def update_post(id):
    post = db.get_or_404(Post, id)
    form = PostForm(obj=post)
    populate_choices(form)

    if not form.is_submitted():
        form.enabled.data = post.is_active
        form.publish_date.data = post.posted
        form.author_id.data = post.user_id
        form.tags.data = [tag.id for tag in post.tags]

    if form.validate_on_submit():
        user = db.session.get(User, form.author_id.data)
        if user is None:
            form.author_id.errors.append("Обраний автор більше не існує.")
        else:
            post.title = form.title.data
            post.content = form.content.data
            post.category = form.category.data
            post.is_active = form.enabled.data
            post.posted = form.publish_date.data or post.posted
            post.user = user
            post.tags = selected_tags(form)
            db.session.commit()
            flash("Допис успішно оновлено!", "success")
            return redirect(url_for("posts.post_detail", id=post.id))

    return render_template("posts/post_form.html", form=form, post=post)


@post_bp.route("/<int:id>/delete", methods=["GET", "POST"])
def delete_post(id):
    post = db.get_or_404(Post, id)
    if request.method == "POST":
        db.session.delete(post)
        db.session.commit()
        flash("Допис успішно видалено!", "success")
        return redirect(url_for("posts.list_posts"))
    return render_template("posts/post_delete.html", post=post)


@click.command("posts-by-user")
@click.argument("user_id", type=int)
def posts_by_user_command(user_id):
    """Print every post that belongs to a user, including inactive posts."""
    user = db.session.get(User, user_id)
    if user is None:
        click.echo(f"Користувача id={user_id} не знайдено.")
        raise click.exceptions.Exit(1)
    posts = db.session.scalars(
        post_query().where(Post.user_id == user_id).order_by(Post.id)
    ).all()
    click.echo(f"Дописів користувача id={user_id} ({user.username}): {len(posts)}")
    for post in posts:
        click.echo(f"  #{post.id} {post.title} | теги: {', '.join(tag.name for tag in post.tags)}")


@click.command("seed-lab8")
def seed_lab8_command():
    """Create repeatable Lab 8 data for two users, five posts, and three tags."""
    import secrets
    from werkzeug.security import generate_password_hash

    users_by_name = {user.username: user for user in db.session.scalars(select(User)).all()}
    for username, email in (
        ("user1", "user1@lab8.example.invalid"),
        ("user2", "user2@lab8.example.invalid"),
    ):
        user = users_by_name.get(username)
        if user is None:
            user = User(
                username=username,
                email=email,
                password=generate_password_hash(secrets.token_urlsafe(32)),
            )
            db.session.add(user)
            users_by_name[username] = user
    tags_by_name = {tag.name: tag for tag in db.session.scalars(select(Tag)).all()}
    for name in ("Tech", "Art", "Science"):
        if name not in tags_by_name:
            tag = Tag(name=name)
            db.session.add(tag)
            tags_by_name[name] = tag
    db.session.flush()

    user1 = users_by_name["user1"]
    user2 = users_by_name["user2"]
    tags = [tags_by_name[name] for name in ("Tech", "Art", "Science")]
    posts = db.session.scalars(select(Post).order_by(Post.id)).all()
    sample_titles = [
        "Вступ до Flask",
        "Мистецтво вебдизайну",
        "Наукові нотатки",
        "SQLAlchemy та зв’язки",
        "Практика ORM",
    ]
    while len(posts) < 5:
        index = len(posts)
        post = Post(
            title=sample_titles[index],
            content=f"Демонстраційний допис лабораторної роботи 8 №{index + 1}.",
            category="tech",
            is_active=True,
            user=user1 if index % 2 == 0 else user2,
            tags=[tags[index % 3]],
        )
        db.session.add(post)
        posts.append(post)

    # The lab asks for examples belonging to user ids 1 and 2.
    db.session.flush()
    user_one = db.session.get(User, 1)
    user_two = db.session.get(User, 2)
    if user_one is None or user_two is None:
        click.echo("Потрібно мати щонайменше двох користувачів.")
        raise click.exceptions.Exit(1)
    posts = db.session.scalars(select(Post).order_by(Post.id)).all()
    if posts:
        posts[0].user = user_two
        posts[0].tags = [tags[0], tags[1]]
    if len(posts) > 1:
        posts[1].user = user_one
        if not posts[1].tags:
            posts[1].tags = [tags[1]]
    for index, post in enumerate(posts[:5]):
        if not post.tags:
            post.tags = [tags[index % len(tags)]]
    db.session.commit()
    click.echo(f"Готово: користувачів {db.session.scalar(select(db.func.count()).select_from(User))}, "
               f"дописів {db.session.scalar(select(db.func.count()).select_from(Post))}, "
               f"тегів {db.session.scalar(select(db.func.count()).select_from(Tag))}.")


def register_cli(app):
    app.cli.add_command(posts_by_user_command)
    app.cli.add_command(seed_lab8_command)


@click.command("compare-post-loading")
def compare_post_loading_command():
    """Compare lazy relationship loads with joinedload/selectinload."""
    from sqlalchemy import event, select
    from sqlalchemy.orm import Session, joinedload, selectinload

    engine = db.engine

    def run_variant(label, options=()):
        statements = []

        def record_select(conn, cursor, statement, parameters, context, executemany):
            if statement.lstrip().lower().startswith("select"):
                statements.append(statement)

        event.listen(engine, "before_cursor_execute", record_select)
        try:
            with Session(engine) as session:
                statement = select(Post).order_by(Post.id.desc()).options(*options)
                posts = session.scalars(statement).all()
                output = [
                    (post.title, post.user.username, [tag.name for tag in post.tags])
                    for post in posts
                ]
        finally:
            event.remove(engine, "before_cursor_execute", record_select)

        click.echo(f"\n{label}: {len(output)} дописів, SELECT-запитів: {len(statements)}")
        for title, username, tag_names in output:
            click.echo(f"  {title} | {username} | {', '.join(tag_names)}")
        click.echo("SQL-журнал:")
        for index, sql in enumerate(statements, 1):
            click.echo(f"  SELECT {index}: {' '.join(sql.split())}")
        return len(statements)

    click.echo("SQLALCHEMY_ECHO увімкнено; нижче показано і короткий журнал SELECT.")
    lazy_count = run_variant("Без попереднього завантаження")
    eager_count = run_variant(
        "joinedload(Post.user) + selectinload(Post.tags)",
        (joinedload(Post.user), selectinload(Post.tags)),
    )
    click.echo(f"\nПорівняння SELECT: {lazy_count} → {eager_count}.")


def register_comparison_cli(app):
    app.cli.add_command(compare_post_loading_command)
