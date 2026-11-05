
import unittest

from app import create_app, db
from app.posts.models import Post


class PostTests(unittest.TestCase):
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

    def test_post_creation(self):
        post = Post(
            title="Тестовий допис",
            content="Тестовий вміст",
            category="tech",
            author="admin"
        )

        db.session.add(post)
        db.session.commit()

        saved_post = db.session.get(Post, post.id)

        self.assertIsNotNone(saved_post)
        self.assertEqual(saved_post.title, "Тестовий допис")

    def test_post_list(self):
        response = self.client.get("/post")

        self.assertEqual(response.status_code, 200)

    def test_post_detail(self):
        post = Post(
            title="Тест перегляду",
            content="Текст допису",
            category="news"
        )

        db.session.add(post)
        db.session.commit()

        response = self.client.get(f"/post/{post.id}")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Тест перегляду".encode("utf-8"), response.data)

    def test_post_update(self):
        post = Post(
            title="Стара назва",
            content="Старий текст",
            category="other"
        )

        db.session.add(post)
        db.session.commit()

        post.title = "Нова назва"
        db.session.commit()

        updated_post = db.session.get(Post, post.id)

        self.assertEqual(updated_post.title, "Нова назва")

    def test_post_delete(self):
        post = Post(
            title="Для видалення",
            content="Тестовий текст",
            category="other"
        )

        db.session.add(post)
        db.session.commit()

        post_id = post.id

        db.session.delete(post)
        db.session.commit()

        self.assertIsNone(db.session.get(Post, post_id))


if __name__ == "__main__":
    unittest.main()
