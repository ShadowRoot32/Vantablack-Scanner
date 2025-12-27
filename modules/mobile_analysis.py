import re
import os

class AndroidScanner:
    def analyze_apk(self, apk_path):
        """
        Static Analysis APK untuk mencari Hardcoded Secrets (Materi Silabus Hari ke-15 & 16)
        """
        findings = []
        if not os.path.exists(apk_path):
            return ["APK file not found"]

        # Pola regex untuk mencari kunci rahasia yang tertinggal
        patterns = {
            "Google API Key": r"AIza[0-9A-Za-z-_]{35}",
            "Firebase URL": r"https://[a-z0-9-]+\.firebaseio\.com",
            "AWS Access Key": r"AKIA[0-9A-Z]{16}",
            "AWS Secret Key": r"[0-9a-zA-Z/+]{40}",
            "Private Key Block": r"-----BEGIN PRIVATE KEY-----",
            "Generic API Token": r"(api_key|access_token|secret)[\s=:'\"]+([a-zA-Z0-9-]{20,})"
        }
        
        try:
            # Baca file APK sebagai binary (seolah-olah 'strings' command)
            with open(apk_path, 'rb') as f:
                content = f.read().decode('utf-8', errors='ignore')
                
            for name, regex in patterns.items():
                matches = list(set(re.findall(regex, content))) # Unique matches
                if matches:
                    # Ambil maksimal 3 sampel per tipe biar log tidak penuh
                    samples = ", ".join([str(m)[:10]+"..." for m in matches[:3]])
                    findings.append(f"{name}: Found {len(matches)} (Sample: {samples})")
        except Exception as e:
            return [f"Error analyzing APK: {str(e)}"]
            
        return findings