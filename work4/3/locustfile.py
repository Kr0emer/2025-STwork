from locust import HttpUser, task, between
class WebsiteUser(HttpUser):
    wait_time = between(1, 3)
    @task
    def order_book(self):
        self.client.post("/order", json={"item": "book", "qty": 1})