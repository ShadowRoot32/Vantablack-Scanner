import os
import sys
import yaml
import time
import requests
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.align import Align
from bs4 import BeautifulSoup

# --- IMPORT MODUL ---
from modules.waf_evasion import WAFEvasion
from modules.ai_killchain import AIBrain
from modules.scanner_core import ScannerEngine
from modules.scan_timer import ScanTimer
from modules.advanced_scanners import AdvancedWebScanner
from modules.mobile_analysis import AndroidScanner

# Init Console
console = Console()

# --- LOAD CONFIG ---
if not os.path.exists("config.yaml"):
    console.print("[bold red][!] ERROR: config.yaml not found![/bold red]")
    sys.exit(1)

with open("config.yaml", "r") as f:
    CONFIG = yaml.safe_load(f)

# --- INIT MODULES ---
waf = WAFEvasion()
brain = AIBrain(CONFIG)
scanner = ScannerEngine(waf)

# --- THE GRIM REAPER LOGO ---
LOGO = r"""
[bold white]
              ...
            ;::::;
          ;::::; :;
        ;:::::'   :;
       ;:::::;     ;.
      ,:::::'       ;           OOO\
      ::::::;       ;          OOOOO\
      ;:::::;       ;         OOOOOOOO
     ,;::::::;     ;'         / OOOOOOO
   ;:::::::::`. ,,,;.        /  / DOOOOOO
  .';:::::::::::::::::;,     /  /     DOOOO
 ,::::::;::::::;;;;::::;,   /  /        DOOO
;`::::::`'::::::;;;::::: ,#/  /          DOO
:`:::::::`;::::::;;::: ;::#  /            DOO
::`:::::::`;:::::::: ;::::# /              DOO
`:`:::::::`;:::::: ;::::::#/               DOO
 :::`:::::::`;; ;:::::::::##                OO
 ::::`:::::::`;::::::::;:::#                OO
 `:::::`::::::::::::;'`:;::#                O
  `:::::`::::::::;' /  / `:#
   ::::::`:::::;'  /  /   `#
[/bold white]
   [bold red]V A N T A   B L A C K[/bold red]
   [dim]The Angel of Digital Death[/dim]
"""

class Vantablack:
    def __init__(self, target):
        self.target = target
        self.report_dir = CONFIG['settings']['reports_dir']
        if not os.path.exists(self.report_dir): os.makedirs(self.report_dir)
        
        self.data = {
            "nmap": "", "nuclei": [], "sqlmap": [], "secrets": [], 
            "subdomains": [], "hidden_files": [], "advanced_web": []
        }
        self.timer = ScanTimer()

    def print_status(self, msg, type="info"):
        """Fungsi print sederhana ala hacker terminal"""
        if type == "info":
            console.print(f"[bold blue][*][/bold blue] {msg}")
        elif type == "success":
            console.print(f"[bold green][+][/bold green] {msg}")
        elif type == "warn":
            console.print(f"[bold yellow][!][/bold yellow] {msg}")
        elif type == "error":
            console.print(f"[bold red][-][/bold red] {msg}")
        elif type == "process":
            console.print(f"[dim]    >> {msg}[/dim]")

    def start(self):
        # 1. Clear Screen & Show Logo
        os.system('cls' if os.name == 'nt' else 'clear')
        console.print(Align.center(LOGO))
        console.print("\n")

        # 2. Cek Tools
        missing = scanner.check_tools()
        if missing:
            self.print_status(f"Tools missing: {missing}", "warn")
            time.sleep(1)

        # 3. Mulai Scan
        self.timer.start()
        self.print_status(f"Target Acquired: [bold white]{self.target}[/bold white]", "success")
        self.print_status("Initiating Killchain Sequence...", "info")
        print("-" * 50)

        # --- JIKA APK (ANDROID) ---
        if self.target.endswith(".apk"):
            self.print_status("Detected Android Package (APK)", "info")
            self.print_status("Running Static Analysis...", "process")
            
            mobile_scan = AndroidScanner()
            apk_secrets = mobile_scan.analyze_apk(self.target)
            self.data["secrets"].extend(apk_secrets)
            
            self.print_status(f"Analysis Done. Found {len(apk_secrets)} potential secrets.", "success")

        # --- JIKA WEBSITE (URL) ---
        else:
            # PHASE 1: RECON
            self.print_status("PHASE 1: RECONNAISSANCE", "info")
            
            subs = scanner.get_subdomains(self.target)
            self.data["subdomains"] = subs
            self.print_status(f"Subdomains Found: {len(subs)}", "process")
            
            count = scanner.spider(self.target)
            self.data["hidden_files"] = scanner.hidden_files
            self.print_status(f"URLs Crawled: {count}", "process")
            if self.data["hidden_files"]:
                self.print_status(f"Hidden Files Found: {len(self.data['hidden_files'])}", "warn")

            # PHASE 2: NETWORK & VULN
            print("-" * 50)
            self.print_status("PHASE 2: VULNERABILITY SCANNING", "info")
            
            domain = self.target.replace("http://","").replace("https://","").split("/")[0]
            self.print_status("Executing Nmap...", "process")
            self.data["nmap"] = scanner.run_nmap(domain)
            
            self.print_status("Executing Nuclei...", "process")
            self.data["nuclei"] = scanner.run_nuclei(self.target)
            self.print_status(f"Nuclei Hits: {len(self.data['nuclei'])}", "success" if len(self.data['nuclei']) > 0 else "process")

            # PHASE 3: INJECTION
            print("-" * 50)
            self.print_status("PHASE 3: SQL INJECTION", "info")
            self.data["sqlmap"] = scanner.run_sqlmap()
            if self.data["sqlmap"]:
                self.print_status(f"VULNERABLE URLs: {len(self.data['sqlmap'])}", "error")
            else:
                self.print_status("No SQL Injection found.", "process")

            # PHASE 4: ADVANCED WEB
            print("-" * 50)
            self.print_status("PHASE 4: ADVANCED AUDIT", "info")
            adv_web = AdvancedWebScanner(waf)
            
            # CSRF/SSRF Logic
            try:
                r = requests.get(self.target, headers=waf.get_headers(), timeout=10)
                soup = BeautifulSoup(r.text, "html.parser")
                forms = soup.find_all('form')
                csrf_vulns = adv_web.scan_csrf(self.target, forms)
                if csrf_vulns:
                    self.print_status(f"CSRF Risks: {len(csrf_vulns)} forms", "warn")
                    self.data["advanced_web"].append(f"CSRF Missing: {len(csrf_vulns)} forms")
            except: pass
            
            targets_with_params = [u for u in scanner.crawled_urls if "=" in u]
            ssrf_vulns = adv_web.scan_ssrf(targets_with_params)
            if ssrf_vulns:
                self.print_status(f"SSRF Indications: {len(ssrf_vulns)} URLs", "warn")
                self.data["advanced_web"].append(f"SSRF: {len(ssrf_vulns)} URLs")

            # Secrets
            self.print_status("Scanning for JS Secrets...", "process")
            self.data["secrets"] = scanner.scan_js_secrets(self.target)
            if self.data["secrets"]:
                 self.print_status(f"Secrets Leaked: {len(self.data['secrets'])}", "warn")

        # --- REPORTING ---
        print("-" * 50)
        self.print_status("PHASE 5: INTELLIGENCE REPORTING", "info")
        self.print_status("Consulting AI Brain...", "process")
        
        self.timer.stop()
        total_time = self.timer.get_duration()

        prompt = f"""
        Role: Elite Cyber Security Specialist. Target: {self.target}. Duration: {total_time}
        DATA: Subdomains:{len(self.data.get('subdomains', []))}, Nmap_Len:{len(self.data['nmap'])}, Nuclei:{len(self.data['nuclei'])}, SQLMap:{len(self.data['sqlmap'])}, Secrets:{len(self.data['secrets'])}.
        Task: Write Penetration Test Report (Markdown).
        """
        
        report = brain.generate_report(prompt)
        
        # Save File
        if self.target.endswith(".apk"):
            safe_name = os.path.basename(self.target)
        else:
            safe_name = self.target.replace("http://","").replace("https://","").replace("/","_")

        fname = f"{self.report_dir}/REPORT_{safe_name}_{int(time.time())}.md"
        with open(fname, "w", encoding="utf-8") as f: f.write(report)

        # FINAL SUMMARY
        print("\n")
        console.print(Panel(f"""
[bold green]MISSION COMPLETE[/bold green]

[white]Target  :[/white] {self.target}
[white]Duration:[/white] {total_time}
[white]Findings:[/white] {len(self.data['nuclei'])} CVEs, {len(self.data['sqlmap'])} SQLi
[white]Report  :[/white] [underline]{os.path.abspath(fname)}[/underline]
""", title="SUMMARY", border_style="white"))

if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        console.print("[bold white]ENTER TARGET (URL / APK Path):[/bold white]")
        target = input(">> ").strip()
        
        if not target: sys.exit()
        
        # Validasi URL simpel
        if not target.endswith(".apk") and not target.startswith("http") and not os.path.exists(target):
             target = "https://" + target
             
        bot = Vantablack(target)
        bot.start()
    except KeyboardInterrupt:
        print("\n[!] Aborted by user.")
        sys.exit()