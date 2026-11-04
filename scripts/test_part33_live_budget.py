"""Offline regression checks for the evaluation guard; never calls a provider."""
from concurrent.futures import ThreadPoolExecutor
from email.message import Message
import json
from pathlib import Path
import tempfile
import unittest
from urllib.request import Request

from evaluate_part33_live import BudgetExceeded, CallBudget, CapturedResponse, ROOT


class BudgetTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(dir=ROOT / "tmp", prefix="part33-budget-test-")
        self.budget = CallBudget(Path(self.directory.name), 24)
        self.request = Request("https://api.openai.com/v1/embeddings", data=b'{"input":["fictional"]}', method="POST")

    def tearDown(self):
        self.budget.ledger.close()
        self.directory.cleanup()

    @staticmethod
    def response(_request, *, timeout):
        headers = Message()
        headers["Content-Type"] = "application/json"
        return CapturedResponse(b"{}", 200, headers)

    def test_failure_consumes_budget_and_attempt_25_is_blocked(self):
        def failure(_request, *, timeout):
            raise TimeoutError()
        with self.assertRaises(TimeoutError):
            self.budget.wrap(failure, "embedding")(self.request, timeout=5)
        for _ in range(23):
            self.budget.wrap(self.response, "embedding")(self.request, timeout=5)
        with self.assertRaises(BudgetExceeded):
            self.budget.wrap(self.response, "embedding")(self.request, timeout=5)
        self.budget.wait_idle()
        self.assertEqual(self.budget.started, 24)
        self.assertEqual(self.budget.active, 0)
        events = [json.loads(line) for line in (Path(self.directory.name) / "provider-attempts.jsonl").read_text().splitlines()]
        self.assertEqual(sum(e["event"] == "attempt_started" for e in events), 24)
        self.assertEqual(sum(e["event"] == "attempt_error" for e in events), 1)

    def test_concurrent_reservations_cannot_exceed_cap(self):
        def attempt(_number):
            try:
                self.budget.wrap(self.response, "embedding")(self.request, timeout=5)
                return "allowed"
            except BudgetExceeded:
                return "blocked"
        with ThreadPoolExecutor(max_workers=4) as pool:
            outcomes = list(pool.map(attempt, range(30)))
        self.assertEqual(outcomes.count("allowed"), 24)
        self.assertEqual(outcomes.count("blocked"), 6)

    def test_unrelated_tasks_and_uncounted_connections_are_blocked(self):
        title = Request("https://api.openai.com/v1/responses", data=b'{"instructions":"Generate a title"}', method="POST")
        with self.assertRaisesRegex(RuntimeError, "Unapproved provider task"):
            self.budget.wrap(self.response, "reply")(title, timeout=10)
        import http.client
        with self.budget.transport_guard(), self.assertRaisesRegex(RuntimeError, "Uncounted outgoing HTTP blocked"):
            http.client.HTTPSConnection("api.openai.com").connect()
        self.assertEqual(self.budget.started, 0)


if __name__ == "__main__":
    unittest.main()
