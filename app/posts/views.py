from datetime import datetime

from flask import render_template, redirect, url_for, flash, session, request

from app import db
from . import post_bp
from .forms import PostForm
from .models import Post


@post_bp.route("/create", methods=["GET", "POST"])
def create_post():
    form = PostForm()


    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            content=form.content.data,
            posted=form.publish_date.data or datetime.utcnow(),
            category=form.category.data,
            is_active=form.enabled.data,
            author=session.get("username", "Anonymous")
        )

        db.session.add(post)
        db.session.commit()

        flash("Допис успішно створено!", "success")
        return redirect(url_for("posts.create_post"))

    return render_template("posts/post_form.html", form=form)



@post_bp.route("", methods=["GET"])
@post_bp.route("/", methods=["GET"])
def list_posts():
    posts = db.session.scalars(
        db.select(Post)
        .where(Post.is_active.is_(True))
        .order_by(Post.posted.desc())
    ).all()

    return render_template(
        "posts/post_list.html",
        posts=posts
    )



@post_bp.route("/<int:id>", methods=["GET"])
def post_detail(id):
    post = db.get_or_404(Post, id)

    return render_template(
        "posts/post_detail.html",
        post=post
    )


@post_bp.route("/<int:id>/update", methods=["GET", "POST"])
def update_post(id):
    post = db.get_or_404(Post, id)
    form = PostForm(obj=post)

    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.category = form.category.data
        post.is_active = form.enabled.data
        post.posted = form.publish_date.data or post.posted

        db.session.commit()

        flash("Допис успішно оновлено!", "success")
        return redirect(url_for("posts.post_detail", id=post.id))

    if not form.is_submitted():
        form.enabled.data = post.is_active
        form.publish_date.data = post.posted

    return render_template(
        "posts/post_form.html",
        form=form,
        post=post
    )

@post_bp.route("/<int:id>/delete", methods=["GET", "POST"])
def delete_post(id):
    post = db.get_or_404(Post, id)

    if request.method == "POST":
        db.session.delete(post)
        db.session.commit()

        flash("Допис успішно видалено!", "success")
        return redirect(url_for("posts.list_posts"))

    return render_template(
        "posts/post_delete.html",
        post=post
    )
