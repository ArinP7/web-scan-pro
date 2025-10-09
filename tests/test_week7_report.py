import unittest
import os
import json
from week7_report import load_findings, severity_level, generate_summary, save_report

class TestWeek7Report(unittest.TestCase):

    def setUp(self):
        # Setup sample JSON files for testing
        self.weak_creds_data = {
            "working_creds": ["user:pass"]
        }
        self.session_audit_data = {
            "fixated": True
        }
        self.logout_invalid_data = {
            "session_still_valid_after_logout": True
        }
        with open("weak_creds.json", "w") as f:
            json.dump(self.weak_creds_data, f)
        with open("session_audit.json", "w") as f:
            json.dump(self.session_audit_data, f)
        with open("logout_invalid.json", "w") as f:
            json.dump(self.logout_invalid_data, f)

    def tearDown(self):
        # Remove test files
        os.remove("weak_creds.json")
        os.remove("session_audit.json")
        os.remove("logout_invalid.json")
        if os.path.exists("test_report.html"):
            os.remove("test_report.html")
        if os.path.exists("severity_chart.png"):
            os.remove("severity_chart.png")
        if os.path.exists("type_chart.png"):
            os.remove("type_chart.png")

    def test_load_findings(self):
        findings = load_findings()
        self.assertEqual(len(findings), 3)
        types = [f['type'] for f in findings]
        self.assertIn("Weak Credentials", types)
        self.assertIn("Session Fixation", types)
        self.assertIn("Invalid Logout", types)

    def test_severity_level(self):
        self.assertEqual(severity_level("low"), "Low")
        self.assertEqual(severity_level("Medium"), "Medium")
        self.assertEqual(severity_level("HIGH"), "High")
        self.assertEqual(severity_level("unknown"), "Low")

    def test_generate_summary(self):
        findings = load_findings()
        severity_counts, type_counts = generate_summary(findings)
        self.assertEqual(severity_counts["High"], 2)
        self.assertEqual(severity_counts["Medium"], 1)
        self.assertEqual(type_counts["Weak Credentials"], 1)
        self.assertEqual(type_counts["Session Fixation"], 1)
        self.assertEqual(type_counts["Invalid Logout"], 1)

    def test_save_report(self):
        findings = load_findings()
        save_report(findings, "test_report.html")
        self.assertTrue(os.path.exists("test_report.html"))
        self.assertTrue(os.path.exists("severity_chart.png"))
        self.assertTrue(os.path.exists("type_chart.png"))

if __name__ == "__main__":
    unittest.main()
