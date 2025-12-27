import time

class ScanTimer:
    def __init__(self):
        self.start_time = None
        self.end_time = None

    def start(self):
        """Memulai stopwatch"""
        self.start_time = time.time()

    def stop(self):
        """Menghentikan stopwatch"""
        self.end_time = time.time()

    def get_duration(self):
        """Menghitung durasi dalam format string yang rapi (HH:MM:SS)"""
        if not self.start_time:
            return "00:00:00"
        
        # Jika stop() belum dipanggil, gunakan waktu sekarang
        end = self.end_time if self.end_time else time.time()
        duration = end - self.start_time

        # Konversi detik ke Jam, Menit, Detik
        hours, rem = divmod(duration, 3600)
        minutes, seconds = divmod(rem, 60)
        
        # Format string (contoh: 00:05:23.45)
        if hours > 0:
            return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
        elif minutes > 0:
            return f"{int(minutes)}m {seconds:.2f}s"
        else:
            return f"{seconds:.2f} seconds"