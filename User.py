import requests
import Submission
import Problem


class User:
    def __init__(self, name):
        user = requests.get(f"https://dmoj.ca/api/user/info/{name}").json()
        self.name = name
        self.points = user["points"]
        self.performance_points = round(user["performance_points"])
        self.solved_problems = user["solved_problems"]
        self.contests = user["contests"]["history"]
        self.current_rating = user["contests"]["current_rating"]
        self.volatility = user["contests"]["volatility"]
        self.submissions = requests.get(f"https://dmoj.ca/api/user/submissions/{name}").json()
        self.results = {}
        for ID in self.submissions:
            submission = self.submissions[ID]
            if submission["result"] is not None:
                if submission["result"] in self.results:
                    self.results[submission["result"]] += 1
                else:
                    self.results[submission["result"]] = 1
        self.ac_rate = round(self.results["AC"]/len(self.submissions), 4)*100

    # Gets nth most recent submission
    def recent_submission(self, n):
        submission_keys = list(self.submissions.keys())
        # print(submission_keys[0])
        submission = self.submissions[submission_keys[-n]]
        problem = Problem.Problem(submission["problem"])
        time = submission["time"]
        memory = submission["memory"]
        points_earned = submission["points"]
        verdict = submission["result"]
        return Submission.Submission(problem, verdict, time, points_earned, memory)
