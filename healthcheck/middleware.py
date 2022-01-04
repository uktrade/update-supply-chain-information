import time


class StatsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def process_request(self, request):
        """Start time at request coming in"""
        request.start_time = time.time()
