"""Insert data into products table

Revision ID: 0322ffd16e8f
Revises: debac67e3e04
Create Date: 2026-11-19 02:40:06.688059

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0322ffd16e8f'
down_revision = 'debac67e3e04'
branch_labels = None
depends_on = None


def upgrade():
    categories_table = sa.table(
        "categories",
        sa.column("id", sa.Integer),
        sa.column("name", sa.String),
    )
    products_table = sa.table(
        "products",
        sa.column("id", sa.Integer),
        sa.column("name", sa.String),
        sa.column("price", sa.Float),
        sa.column("active", sa.Boolean),
        sa.column("category_id", sa.Integer),
    )

    bind = op.get_bind()
    category_names = ["Electronics", "Books", "Clothing"]
    existing_categories = set(
        bind.execute(sa.select(categories_table.c.name)).scalars()
    )
    new_categories = [
        {"name": name}
        for name in category_names
        if name not in existing_categories
    ]
    if new_categories:
        op.bulk_insert(categories_table, new_categories)

    category_ids = dict(
        bind.execute(
            sa.select(categories_table.c.name, categories_table.c.id)
        ).all()
    )
    op.bulk_insert(
        products_table,
        [
            {
                "name": "Laptop",
                "price": 1200.0,
                "active": True,
                "category_id": category_ids["Electronics"],
            },
            {
                "name": "Smartphone LG",
                "price": 800.0,
                "active": True,
                "category_id": category_ids["Electronics"],
            },
            {
                "name": "Novel",
                "price": 20.0,
                "active": True,
                "category_id": category_ids["Books"],
            },
            {
                "name": "T-Shirt",
                "price": 25.0,
                "active": False,
                "category_id": category_ids["Clothing"],
            },
        ],
    )


def downgrade():
    products_table = sa.table(
        "products",
        sa.column("name", sa.String),
    )
    categories_table = sa.table(
        "categories",
        sa.column("id", sa.Integer),
        sa.column("name", sa.String),
    )
    products_with_categories = sa.table(
        "products",
        sa.column("category_id", sa.Integer),
    )

    op.execute(
        sa.delete(products_table).where(
            products_table.c.name.in_(
                ["Laptop", "Smartphone LG", "Novel", "T-Shirt"]
            )
        )
    )
    op.execute(
        sa.delete(categories_table)
        .where(categories_table.c.name.in_(
            ["Electronics", "Books", "Clothing"]
        ))
        .where(
            ~sa.exists(
                sa.select(1)
                .select_from(products_with_categories)
                .where(
                    products_with_categories.c.category_id
                    == categories_table.c.id
                )
            )
        )
    )