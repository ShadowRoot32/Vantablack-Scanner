import google.generativeai as genai
import os
import yaml

# 1. Load API Key dari config.yaml
try:
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
        api_key = config['api_keys']['gemini']
except Exception as e:
    print("Gagal baca config.yaml. Pastikan file ada.")
    exit()

if not api_key:
    print("API Key Gemini kosong di config.yaml!")
    exit()

# 2. Cek Model
print(f"Sedang mengecek akses untuk API Key: {api_key[:5]}...xxx")
genai.configure(api_key=api_key)

try:
    print("\nModel yang tersedia untuk Anda:")
    found = False
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f" - {m.name}")
            found = True
    if not found:
        print("Tidak ada model generative yang ditemukan. Cek billing/lokasi API Key Anda.")
except Exception as e:
    print(f"Error Koneksi: {e}")