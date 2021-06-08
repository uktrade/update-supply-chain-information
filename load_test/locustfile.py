"""Load test scenario file.

This module defines operations that test users are going to do during the test. As we are
interested in finding the max_concurrent_users, 2 tasks have been defined here with
view_tasklist having more weightage than visiting the home page. Test would stop as soon
as seeing non 200 response.

No additional fixtures/config are required(on top of dependency for functional tests)
to run this test.
"""
from random import randint


from locust import HttpUser, task
from locust.exception import ResponseError


class QuickstartUser(HttpUser):
    def validate_resp(self, status_code):
        if status_code != 200:
            print(f"Received error response: {status_code}")
            self.environment.runner.quit()
            raise ResponseError()

    @task
    def home(self):
        resp = self.client.get("")
        self.validate_resp(resp.status_code)

    @task(4)
    def view_tasklists(self):
        supply_chain_index = randint(1, 7)
        route = f"Tasklist-SC{supply_chain_index}"
        resp = self.client.get(f"/supply-chain-{supply_chain_index}/", name=route)
        self.validate_resp(resp.status_code)
