import unittest
from app import app


class TestUserBlueprint(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_greetings(self):
        response = self.app.get("/users/hi/John?age=30")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"JOHN", response.data)
        self.assertIn(b"30", response.data)

    def test_admin(self):
        response = self.app.get(
            "/users/admin",
            follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"ADMINISTRATOR", response.data)
        self.assertIn(b"45", response.data)


if __name__ == "__main__":
    unittest.main()