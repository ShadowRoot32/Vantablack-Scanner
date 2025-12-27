class Vantablack:
    def __init__(self, target):
        self.target = target
        self.report_dir = CONFIG['settings']['reports_dir']
        # ... kode lain ...
        
        # [TIMER] Inisialisasi Timer
        self.timer = ScanTimer()