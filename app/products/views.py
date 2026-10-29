from datetime import datetime
from flask import render_template, abort, redirect, url_for, flash

from . import products_bp
from .database import products_table, Product
from .forms import ProductForm
from .uploads import save_product_image


@products_bp.route("/")
def product_list():
    products = products_table.all()

    return render_template(
        "products/products.html",
        products=products,
        title="Список товарів"
    )


@products_bp.route("/<int:product_id>")
def product_detail(product_id):
    product = products_table.get(Product.id == product_id)

    if product is None:
        abort(404)

    return render_template(
        "products/detail_product.html",
        product=product,
        title=product["name"]
    )


@products_bp.route("/add", methods=["GET", "POST"])
def product_add():
    form = ProductForm()

    if form.validate_on_submit():
        existing_ids = [
            product["id"] for product in products_table.all()
        ]

        new_id = max(existing_ids, default=0) + 1

        image_path = ""

        if form.image.data:
            try:
                image_path = save_product_image(form.image.data)
            except ValueError as error:
                form.image.errors.append(str(error))

                return render_template(
                    "products/product_form.html",
                    form=form,
                    title="Додати товар"
                )

        new_product = {
            "id": new_id,
            "name": form.name.data,
            "content": form.content.data,
            "price": float(form.price.data),
            "category": form.category.data,
            "quantity": form.quantity.data,
            "image": image_path,
            "created_at": datetime.now().isoformat()
        }

        products_table.insert(new_product)

        flash("Товар успішно додано!", "success")

        return redirect(url_for("products.product_list"))

    return render_template(
        "products/product_form.html",
        form=form,
        title="Додати товар"
    )


@products_bp.route("/<int:product_id>/edit", methods=["GET", "POST"])
def product_edit(product_id):
    product = products_table.get(Product.id == product_id)

    if product is None:
        abort(404)

    form = ProductForm()

    if form.validate_on_submit():
        image_path = product.get("image", "")

        if form.image.data:
            try:
                image_path = save_product_image(form.image.data)
            except ValueError as error:
                form.image.errors.append(str(error))

                return render_template(
                    "products/product_form.html",
                    form=form,
                    title="Редагувати товар"
                )

        products_table.update(
            {
                "name": form.name.data,
                "content": form.content.data,
                "price": float(form.price.data),
                "category": form.category.data,
                "quantity": form.quantity.data,
                "image": image_path
            },
            Product.id == product_id
        )

        flash("Товар успішно оновлено!", "success")

        return redirect(
            url_for("products.product_detail", product_id=product_id)
        )

    if not form.is_submitted():
        form.name.data = product["name"]
        form.content.data = product["content"]
        form.price.data = product["price"]
        form.category.data = product["category"]
        form.quantity.data = product["quantity"]

    return render_template(
        "products/product_form.html",
        form=form,
        title="Редагувати товар"
    )


@products_bp.route("/<int:product_id>/delete", methods=["POST"])
def product_delete(product_id):
    product = products_table.get(Product.id == product_id)

    if product is None:
        abort(404)

    products_table.remove(Product.id == product_id)

    flash("Товар успішно видалено!", "success")

    return redirect(url_for("products.product_list"))