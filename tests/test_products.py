import unittest

from app import app


class ProductTests(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

    def test_product_list(self):
        response = self.client.get("/products/")
        self.assertEqual(response.status_code, 200)

    def test_product_detail(self):
        response = self.client.get("/products/1")
        self.assertEqual(response.status_code, 200)

    def test_product_not_found(self):
        response = self.client.get("/products/999999")
        self.assertEqual(response.status_code, 404)

    def test_product_add_page(self):
        response = self.client.get("/products/add")
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()