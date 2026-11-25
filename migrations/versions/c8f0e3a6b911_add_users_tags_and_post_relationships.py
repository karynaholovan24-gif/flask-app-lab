"""Add users and tags, then connect them to existing posts."""
from alembic import op
import sqlalchemy as sa


revision = "c8f0e3a6b911"
down_revision = "0322ffd16e8f"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=80), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("username", name=op.f("uq_users_username")),
        sa.UniqueConstraint("email", name=op.f("uq_users_email")),
    )
    op.create_table(
        "tags",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tags")),
        sa.UniqueConstraint("name", name=op.f("uq_tags_name")),
    )
    op.create_table(
        "post_tags",
        sa.Column("post_id", sa.Integer(), nullable=False),
        sa.Column("tag_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["post_id"], ["posts.id"], name=op.f("fk_post_tags_post_id_posts"), ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["tag_id"], ["tags.id"], name=op.f("fk_post_tags_tag_id_tags"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("post_id", "tag_id", name=op.f("pk_post_tags")),
    )

    bind = op.get_bind()
    posts_table = sa.table(
        "posts",
        sa.column("id", sa.Integer()),
        sa.column("author", sa.String(length=20)),
        sa.column("user_id", sa.Integer()),
    )
    users_table = sa.table(
        "users",
        sa.column("id", sa.Integer()),
        sa.column("username", sa.String(length=80)),
        sa.column("email", sa.String(length=255)),
        sa.column("password", sa.String(length=255)),
    )
    legacy_authors = bind.execute(
        sa.select(posts_table.c.id, posts_table.c.author).order_by(posts_table.c.id)
    ).all()

    with op.batch_alter_table("posts", schema=None) as batch_op:
        batch_op.add_column(sa.Column("user_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            op.f("fk_posts_user_id_users"), "users", ["user_id"], ["id"], ondelete="CASCADE"
        )

    username_to_id = {}
    for post_id, old_author in legacy_authors:
        username = (old_author or "Anonymous").strip()[:80] or "Anonymous"
        user_id = username_to_id.get(username)
        if user_id is None:
            email = f"legacy-post-author-{post_id}@example.invalid"
            bind.execute(
                users_table.insert().values(
                    username=username,
                    email=email,
                    password="!",
                )
            )
            user_id = bind.execute(
                sa.select(users_table.c.id).where(users_table.c.email == email)
            ).scalar_one()
            username_to_id[username] = user_id
        bind.execute(
            posts_table.update().where(posts_table.c.id == post_id).values(user_id=user_id)
        )

    with op.batch_alter_table("posts", schema=None) as batch_op:
        batch_op.alter_column("user_id", existing_type=sa.Integer(), nullable=False)
        batch_op.drop_column("author")


def downgrade():
    bind = op.get_bind()
    posts_table = sa.table(
        "posts",
        sa.column("id", sa.Integer()),
        sa.column("user_id", sa.Integer()),
        sa.column("author", sa.String(length=20)),
        sa.column("user_id", sa.Integer()),
    )
    users_table = sa.table(
        "users",
        sa.column("id", sa.Integer()),
        sa.column("username", sa.String(length=80)),
    )
    with op.batch_alter_table("posts", schema=None) as batch_op:
        batch_op.add_column(sa.Column("author", sa.String(length=20), nullable=True))

    for post_id, username in bind.execute(
        sa.select(posts_table.c.id, users_table.c.username).select_from(
            posts_table.join(users_table, posts_table.c.user_id == users_table.c.id)
        )
    ):
        bind.execute(
            posts_table.update()
            .where(posts_table.c.id == post_id)
            .values(author=username[:20])
        )

    with op.batch_alter_table("posts", schema=None) as batch_op:
        batch_op.drop_constraint(op.f("fk_posts_user_id_users"), type_="foreignkey")
        batch_op.drop_column("user_id")
        batch_op.alter_column("author", existing_type=sa.String(length=20), nullable=True)

    op.drop_table("post_tags")
    op.drop_table("tags")
    op.drop_table("users")
