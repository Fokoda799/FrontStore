from random import randint

from locust import HttpUser, between, task


class UserWebsite(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """Create a cart before running tasks."""
        response = self.client.post(
            "/store/carts/",
            name="/store/carts/",
        )

        if response.status_code == 201:
            self.cart_id = response.json()["id"]
        else:
            self.cart_id = None

    @task(4)
    def view_products(self):
        """List products by collection."""
        collection_id = randint(2, 6)

        self.client.get(
            f"/store/products/?collection_id={collection_id}",
            name="/store/products/",
        )

    @task(2)
    def view_product(self):
        """View single product."""
        product_id = randint(1, 100)

        self.client.get(
            f"/store/products/{product_id}/",
            name="/store/products/:id/",
        )

    @task(1)
    def add_product(self):
        """Add product to cart."""
        if not self.cart_id:
            return

        product_id = randint(1, 10)

        self.client.post(
            f"/store/carts/{self.cart_id}/items/",
            name="/store/carts/items/",
            json={
                "product_id": product_id,
                "quantity": 1,
            },
        )

    @task(1)
    def say_hello(self):
        """Health-check endpoint."""
        self.client.get(
            "/play/hello/",
            name="/play/hello/",
        )
