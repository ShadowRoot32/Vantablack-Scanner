# VANTABLACK 💀
> **The Angel of Digital Death** - Automated Penetration Testing & Mobile Security Orchestrator.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-red)

**Vantablack** adalah alat orkestrasi keamanan ofensif canggih yang dirancang untuk mengotomatiskan seluruh *kill chain*: dari pengintaian (recon) hingga pelaporan profesional. Alat ini mengintegrasikan **Multi-AI Brains** (Gemini, OpenAI, Claude) untuk menganalisis kerentanan dan menulis laporan *penetration testing* secara otomatis.

## 🔥 Fitur Utama

- **💀 Grim Reaper CLI**: Antarmuka terminal sederhana & cepat.
- **📱 Android Pentest**: Otomatis mendeteksi *hardcoded secrets* (API Keys, AWS Tokens, Firebase URLs) di file `.apk`.
- **🕸️ Advanced Web Audit**:
  - **CSRF Scanner**: Mendeteksi form tanpa token anti-CSRF.
  - **SSRF Prober**: Mengecek parameter URL untuk indikasi SSRF.
  - **Hidden File Hunter**: Mencari file sensitif (`.env`, `.git`).
- **🧠 Omni-Intelligence**: Sistem AI *Auto-failover*. Jika Gemini gagal, otomatis pindah ke OpenAI/Mistral/Ollama.
- **⚡ Core Engines**: Ditenagai oleh Nmap (NSE Vuln), Nuclei (Criticals), dan SQLMap (Level 3).

---

## 🚀 Cara Instalasi

### 1. Clone Repository
Download source code ke komputer Anda:
```bash
git clone [https://github.com/USERNAME_GITHUB_ANDA/Vantablack-Scanner.git](https://github.com/USERNAME_GITHUB_ANDA/Vantablack-Scanner.git)
cd Vantablack-Scanner
```

## 🚀 Instalasi Tools Pendukung
Pastikan tools utama terinstall (Kali Linux / Ubuntu):
```bash
sudo apt update
sudo apt install nmap sqlmap nuclei -y
```

## 🚀 Install Library Python
```bash
pip install -r requirements.txt
```

##⚙️ Konfigurasi & API Key
Agar fitur AI berjalan, Anda harus memasukkan API Key. Vantablack menggunakan sistem "Failover", artinya Anda bisa memasukkan banyak key sekaligus sebagai cadangan.

1. Buat File Config
Duplikasi file contoh config:
## Linux/Mac
```bash
cp config.example.yaml config.yaml
```
## Windows (CMD)
```bash
copy config.example.yaml config.yaml
```

2. Edit Config & Masukkan Key
Buka file config.yaml dengan text editor (Notepad/Nano/VSCode). Isi API Key di dalam tanda kutip "".
api_keys:
  - **UTAMA (Wajib isi minimal satu)
     -gemini: "AIzaSy..."      # Dapatkan Gratis di Google AI Studio
  - **CADANGAN (Opsional - Jika Gemini error, otomatis pakai ini)
     -openai: "sk-proj-..."    # OpenAI GPT-4 Key
     -anthropic: ""            # Claude Key
     -mistral: ""              # Mistral AI Key
  - **LOKAL (Opsional - Jika tidak ada internet)
     -ollama_url: "http://localhost:11434"
     Catatan: File config.yaml tidak akan ikut ter-upload ke GitHub (karena .gitignore), jadi kunci rahasia Anda aman.

## 🎮 Cara Pemakaian
Jalankan script utama menggunakan Python:
```bash
python main.py
```

1. Input Target
Vantablack menerima dua jenis target:
Website Pentest: Masukkan URL lengkap.
>> [https://example.com](https://example.com)
Aksi: Spidering, Nmap, Nuclei, SQLMap, CSRF/SSRF Check.

2. Mobile Security Audit: Masukkan lokasi file APK.
>> /home/user/downloads/target_aplikasi.apk
Aksi: Static Analysis, Pencarian Hardcoded Secrets.

## 📂 Output & Laporan
Setelah scan selesai, laporan akan dibuat otomatis oleh AI.

Lokasi: Folder ./reports/

Format: REPORT_NamaTarget_Timestamp.md

Anda bisa membuka file .md tersebut dengan Text Editor atau Markdown Viewer untuk melihat hasil analisis lengkap, langkah perbaikan, dan tingkat risiko.

⚠️ Disclaimer
Vantablack dibuat untuk TUJUAN EDUKASI dan PENGUJIAN KEAMANAN LEGAL (Bug Bounty/Pentesting dengan izin). Pengembang tidak bertanggung jawab atas penyalahgunaan alat ini.
