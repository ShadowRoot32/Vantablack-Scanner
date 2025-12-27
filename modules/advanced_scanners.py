import requests
from bs4 import BeautifulSoup

class AdvancedWebScanner:
    def __init__(self, waf_module):
        self.waf = waf_module
    
    def scan_csrf(self, target, forms):
        """
        Mendeteksi form tanpa Anti-CSRF Token (Materi Silabus Hari ke-8)
        """
        vulnerable_forms = []
        csrf_tokens = ['csrf', 'xsrf', 'token', '_token', 'authenticity_token']
        
        for form in forms:
            is_protected = False
            inputs = form.find_all('input')
            for i in inputs:
                name = i.get('name', '').lower()
                if any(token in name for token in csrf_tokens):
                    is_protected = True
                    break
            
            # Jika form punya action (POST) tapi tidak ada token -> Potensi CSRF
            if not is_protected and form.get('action') and form.get('method', '').upper() == 'POST':
                vulnerable_forms.append(form.get('action'))
        
        return vulnerable_forms

    def scan_file_upload(self, forms):
        """
        Mendeteksi fitur File Upload yang berpotensi tidak aman (Materi Silabus Hari ke-8)
        """
        upload_endpoints = []
        for form in forms:
            # Cek enctype="multipart/form-data" atau input type="file"
            if 'multipart/form-data' in str(form) or form.find('input', type='file'):
                action = form.get('action', 'Unknown Endpoint')
                upload_endpoints.append(action)
        return upload_endpoints

    def scan_ssrf(self, target_urls):
        """
        Mendeteksi potensi SSRF pada parameter URL (Materi Silabus Hari ke-11)
        """
        payloads = [
            "http://127.0.0.1", "http://localhost", 
            "http://169.254.169.254/latest/meta-data/" # AWS Metadata
        ]
        ssrf_vulns = []
        
        for url in target_urls:
            if "=" in url:
                for payload in payloads:
                    # Ganti value parameter dengan payload SSRF
                    base, params = url.split('?', 1) if '?' in url else (url, "")
                    if params:
                        test_url = f"{base}?{params.split('=')[0]}={payload}"
                        try:
                            # Timeout cepat karena SSRF internal seringkali cepat atau timeout total
                            r = requests.get(test_url, headers=self.waf.get_headers(), timeout=3)
                            # Indikasi: Jika respon 200 dan ada tanda-tanda root/meta-data
                            if r.status_code == 200 and ("root:" in r.text or "ami-id" in r.text):
                                ssrf_vulns.append(test_url)
                        except: pass
        return ssrf_vulns