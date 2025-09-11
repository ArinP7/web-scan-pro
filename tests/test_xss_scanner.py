import unittest
from xss_scanner import XSSScanner

class TestXSSScanner(unittest.TestCase):
    def setUp(self):
        self.scanner = XSSScanner()

    def test_detect_xss_in_payload(self):
        payload = "<script>alert('XSS')</script>"
        result = self.scanner.scan(payload)
        self.assertTrue(result['vulnerable'])
        self.assertIn('XSS', result['details'])

    def test_no_xss_in_safe_payload(self):
        payload = "Hello, world!"
        result = self.scanner.scan(payload)
        self.assertFalse(result['vulnerable'])

if __name__ == '__main__':
    unittest.main()
