from flask_login import UserMixin
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import check_password_hash

from app import bcrypt, db


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)

    posts: Mapped[list["Post"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def set_password(self, raw_password: str) -> None:
        self.password = bcrypt.generate_password_hash(raw_password).decode("utf-8")

    def check_password(self, raw_password: str) -> bool:
        if self.password.startswith(("$2a$", "$2b$", "$2y$")):
            return bcrypt.check_password_hash(self.password, raw_password)

        # Existing Lab 8 accounts used Werkzeug hashes; accept them once and
        # upgrade the hash to bcrypt after their next successful login.
        try:
            return check_password_hash(self.password, raw_password)
        except (TypeError, ValueError):
            return False

    def __repr__(self) -> str:
        return f"<User {self.id}: {self.username}>"
