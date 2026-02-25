from locust import HttpUser, task, between

class CalculatorUser(HttpUser):
    wait_time = between(1, 2)
    host = "http://localhost:8000"

    @task
    def add(self):
        self.client.get("/add?a=1&b=2")

    @task
    def sub(self):
        self.client.get("/sub?a=5&b=3")

    @task
    def mul(self):
        self.client.get("/mul?a=4&b=3")

    @task
    def div(self):
        self.client.get("/div?a=10&b=2")

    @task
    def div_by_zero(self):
        self.client.get("/div?a=10&b=0")

    @task
    def metrics(self):
        self.client.get("/metrics")