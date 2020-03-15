import requests


class Problem:
    def __init__(self, name):
        problem = requests.get(f"https://dmoj.ca/api/problem/info/{name}").json()
        self.name = problem["name"]
        self.authors = problem["authors"]
        self.types = problem["types"]
        self.group = problem["group"]
        self.time_limit = problem["time_limit"]
        self.memory_limit = problem["memory_limit"]
        self.points = problem["points"]
        self.partial = problem["partial"]
        self.languages = problem["languages"]
        self.link = f"https://dmoj.ca/problem/{self.name}"

    def get_memory_limit_in_mb(self):
        return round(self.memory_limit/1000)
