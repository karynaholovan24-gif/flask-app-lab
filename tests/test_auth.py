import unittest

from sqlalchemy import select
from werkzeug.security import generate_password_hash

from app import create_app, db
from app.users.models import User


class AuthenticationTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def register(self, username="student1", email="student1@example.com", password="secret123"):
        return self.client.post(
            "/users/register",
            data={
                "username": username,
                "email": email,
                "password": password,
                "confirm_password": password,
            },
            follow_redirects=False,
        )

    def add_user(self, username="student1", email="student1@example.com", password="secret123"):
        user = User(username=username, email=email, password="")
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    def test_registration_saves_bcrypt_hash_and_logs_user_in(self):
        response = self.register()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], "/users/account")

        user = db.session.scalar(select(User).where(User.username == "student1"))
        self.assertIsNotNone(user)
        self.assertNotEqual(user.password, "secret123")
        self.assertTrue(user.password.startswith(("$2a$", "$2b$", "$2y$")))
        self.assertTrue(user.check_password("secret123"))
        self.assertEqual(self.client.get("/users/account").status_code, 200)

    def test_registration_rejects_duplicate_username_and_email(self):
        self.add_user()

        by_username = self.client.post(
            "/users/register",
            data={
                "username": "student1",
                "email": "another@example.com",
                "password": "secret123",
                "confirm_password": "secret123",
            },
        )
        self.assertEqual(by_username.status_code, 200)
        self.assertIn("ім’я користувача вже зайняте".encode(), by_username.data)

        by_email = self.client.post(
            "/users/register",
            data={
                "username": "student2",
                "email": "STUDENT1@example.com",
                "password": "secret123",
                "confirm_password": "secret123",
            },
        )
        self.assertEqual(by_email.status_code, 200)
        self.assertIn("електронною поштою вже зареєстрований".encode(), by_email.data)

    def test_registration_validates_username_and_password_confirmation(self):
        response = self.client.post(
            "/users/register",
            data={
                "username": "ab",
                "email": "valid@example.com",
                "password": "secret123",
                "confirm_password": "different123",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("від 4 до 14 символів".encode(), response.data)
        self.assertIn("Паролі не збігаються".encode(), response.data)
        self.assertIsNone(db.session.scalar(select(User).where(User.email == "valid@example.com")))

    def test_registration_rejects_password_longer_than_bcrypt_limit(self):
        response = self.register(password="x" * 73)
        self.assertEqual(response.status_code, 200)
        self.assertIn("не більше 72 байтів UTF-8".encode("utf-8"), response.data)
        self.assertIsNone(db.session.scalar(select(User.id).where(User.email == "student1@example.com")))
    def test_empty_forms_show_validation_errors(self):
        for path in ("/users/register", "/users/login"):
            with self.subTest(path=path):
                response = self.client.post(path, data={})
                self.assertEqual(response.status_code, 200)

    def test_login_logout_and_remember_me(self):
        self.add_user()

        invalid = self.client.post(
            "/users/login",
            data={"email": "student1@example.com", "password": "wrongpass"},
        )
        self.assertEqual(invalid.status_code, 200)
        self.assertIn("Неправильна електронна пошта або пароль".encode(), invalid.data)

        response = self.client.post(
            "/users/login",
            data={
                "email": "STUDENT1@example.com",
                "password": "secret123",
                "remember": "y",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], "/users/account")
        self.assertIn("remember_token", response.headers.get("Set-Cookie", ""))
        self.assertEqual(self.client.get("/users/account").status_code, 200)

        logout = self.client.post("/users/logout")
        self.assertEqual(logout.status_code, 302)
        self.assertEqual(logout.headers["Location"], "/users/login")
        protected = self.client.get("/users/account")
        self.assertEqual(protected.status_code, 302)
        self.assertIn("/users/login", protected.headers["Location"])

    def test_legacy_werkzeug_password_is_upgraded_after_login(self):
        user = User(
            username="legacyuser",
            email="legacy@example.com",
            password=generate_password_hash("secret123"),
        )
        db.session.add(user)
        db.session.commit()

        response = self.client.post(
            "/users/login",
            data={"email": user.email, "password": "secret123"},
        )
        self.assertEqual(response.status_code, 302)
        db.session.refresh(user)
        self.assertTrue(user.password.startswith(("$2a$", "$2b$", "$2y$")))
        self.assertTrue(user.check_password("secret123"))

    def test_account_profile_and_user_list_require_authentication(self):
        for path in ("/users/account", "/users/profile", "/users/list"):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 302)
                self.assertIn("/users/login", response.headers["Location"])

    def test_user_list_shows_registered_users_and_count(self):
        self.add_user()
        response = self.client.get("/users/login")
        self.assertEqual(response.status_code, 200)
        # Registering a second user logs the browser in and gives access to the list.
        self.register("student2", "student2@example.com")
        response = self.client.get("/users/list")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Зареєстровані користувачі (2)".encode(), response.data)
        self.assertIn(b"student1", response.data)
        self.assertIn(b"student2", response.data)

    def test_navigation_changes_for_authenticated_user(self):
        anonymous = self.client.get("/users/login")
        self.assertIn("Реєстрація".encode(), anonymous.data)
        self.assertIn("Вхід".encode(), anonymous.data)

        self.register()
        authenticated = self.client.get("/users/account")
        self.assertIn("Кабінет".encode(), authenticated.data)
        self.assertIn("Вийти".encode(), authenticated.data)
        self.assertNotIn("Реєстрація".encode(), authenticated.data)


if __name__ == "__main__":
    unittest.main()
