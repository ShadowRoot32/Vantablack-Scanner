import subprocess
import shutil
import requests
import re
import json
import time
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

class ScannerEngine:
    def __init__(self, waf_module):
        self.waf = waf_module
        self.crawled_urls = set()
        self.subdomains = set()
        self.secrets = []
        self.hidden_files = []
    
    def check_tools(self):
        tools = ["nmap", "nuclei", "sqlmap"]
        missing = [t for t in tools if not shutil.which(t)]
        return missing

    # --- 1. SUBDOMAIN ENUMERATION (ROOT MAPPING) ---
    def get_subdomains(self, target):
        domain = urlparse(target).netloc
        try:
            # Menggunakan crt.sh untuk mencari subdomain dari sertifikat SSL
            url = f"https://crt.sh/?q=%.{domain}&output=json"
            r = requests.get(url, timeout=20)
            if r.status_code == 200:
                data = r.json()
                for entry in data:
                    name_value = entry['name_value']
                    # Bersihkan hasil (kadang ada newline)
                    sub = name_value.split('\n')[0]
                    if "*" not in sub and domain in sub:
                        self.subdomains.add(sub)
            return list(self.subdomains)[:15] # Ambil 15 sampel saja biar report gak kepanjangan
        except: 
            return []

    # --- 2. DEEP SPIDER & HIDDEN FILE HUNTER ---
    def spider(self, target):
        domain = urlparse(target).netloc
        
        # A. Basic Crawl
        try:
            r = requests.get(target, headers=self.waf.get_headers(), timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            self.crawled_urls.add(target)
            for a in soup.find_all('a', href=True):
                full = urljoin(target, a['href'])
                if domain in full: self.crawled_urls.add(full)
        except: pass

        # B. Hidden File Brute Force (The "Root" Search)
        # Mencari file sensitif yang sering ditinggalkan developer
        sensitive_paths = [
            "/.env", "/.git/config", "/config.php", "/.DS_Store", 
            "/sitemap.xml", "/robots.txt", "/backup.zip", "/phpinfo.php"
        ]
        
        for path in sensitive_paths:
            full_url = target.rstrip("/") + path
            try:
                # Cek status code
                resp = requests.head(full_url, headers=self.waf.get_headers(), timeout=3)
                if resp.status_code == 200:
                    self.hidden_files.append(full_url)
            except: pass
            
        return len(self.crawled_urls)

    # --- 3. NMAP (VULN SCRIPT ENGINE) ---
    def run_nmap(self, domain):
        try:
            # -sV: Version Detection
            # --script=vuln: Menjalankan script NSE untuk mencari CVE otomatis
            # -T4: Kecepatan agresif
            cmd = f"nmap -sV --script=vuln -T4 --top-ports 100 {domain}"
            return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout
        except: return "Nmap Failed"

    # --- 4. NUCLEI (CRITICAL & HIGH FOCUS) ---
    def run_nuclei(self, target):
        try:
            # -severity critical,high: Hanya cari bug parah
            # -dast: Scan dinamis
            cmd = f"nuclei -u {target} -severity critical,high,medium -silent -json"
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            findings = []
            for line in res.stdout.splitlines():
                try: findings.append(json.loads(line))
                except: pass
            return findings
        except: return []

    # --- 5. SQLMAP (LEVEL 3 - DEEP INJECTION) ---
    def run_sqlmap(self):
        targets = [u for u in self.crawled_urls if "?" in u][:3]
        vulns = []
        for t in targets:
            try:
                # --level 3: Cek juga User-Agent dan Referer
                # --risk 2: Coba teknik heavy query time-based
                # --tamper: Bypass WAF sederhana
                cmd = f"sqlmap -u \"{t}\" --batch --random-agent --level 3 --risk 2 --dbs --tamper=space2comment"
                res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=180)
                if "available databases" in res.stdout:
                    vulns.append(t)
            except: pass
        return vulns

    # --- 6. JS SECRET SCANNER ---
    def scan_js_secrets(self, target):
        domain = urlparse(target).netloc
        patterns = {
            "Google API": r"AIza[0-9A-Za-z-_]{35}",
            "AWS Access Key": r"AKIA[0-9A-Z]{16}",
            "JWT Token": r"eyJ[a-zA-Z0-9\-_]+\.eyJ[a-zA-Z0-9\-_]+\.[a-zA-Z0-9\-_]+",
            "Mailgun API": r"key-[0-9a-zA-Z]{32}"
        }
        try:
            r = requests.get(target, headers=self.waf.get_headers(), timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            scripts = [urljoin(target, s['src']) for s in soup.find_all('script', src=True)]
            for s in scripts:
                if domain in s:
                    try:
                        js = requests.get(s, timeout=5).text
                        for name, regex in patterns.items():
                            if re.search(regex, js):
                                self.secrets.append(f"{name} in {s}")
                    except: pass
        except: pass
        return self.secrets