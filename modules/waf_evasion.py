import random
from fake_useragent import UserAgent

class WAFEvasion:
    def __init__(self):
        self.ua = UserAgent()

    def get_headers(self):
        """Generate Stealth Headers to bypass basic WAF"""
        ip = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
        return {
            "User-Agent": self.ua.random,
            "X-Forwarded-For": ip,
            "X-Client-IP": ip,
            "X-Originating-IP": ip,
            "Referer": "https://google.com"
        }