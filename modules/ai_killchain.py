import sys
import google.generativeai as genai
import requests
import json

# Import optional libraries safely
try: import openai
except: pass
try: import anthropic
except: pass
try: from mistralai.client import MistralClient
except: pass

class AIBrain:
    def __init__(self, config):
        self.keys = config.get('api_keys', {})

    def get_active_provider(self):
        for k, v in self.keys.items():
            if v and "ollama" not in k: return k.upper()
        return "OLLAMA (Local)" if self.keys.get('ollama_url') else "NONE"

    def generate_report(self, prompt):
        """Multi-Stage AI Failover System with Raw Fallback"""
        
        # 1. GEMINI (Google) - Dengan List Model Lengkap
        if self.keys.get("gemini"):
            try:
                genai.configure(api_key=self.keys["gemini"])
                
                # Daftar semua kemungkinan nama model dari yang terbaru sampai terlama
                candidate_models = [
                    "gemini-1.5-flash",
                    "gemini-1.5-flash-latest",
                    "gemini-1.5-flash-001",
                    "gemini-1.5-pro",
                    "gemini-1.5-pro-latest",
                    "gemini-1.5-pro-001",
                    "gemini-pro",
                    "gemini-1.0-pro"
                ]

                # Loop coba satu per satu
                for model_name in candidate_models:
                    try:
                        model = genai.GenerativeModel(model_name)
                        response = model.generate_content(prompt)
                        if response.text:
                            return response.text
                    except:
                        continue # Jika error, lanjut ke model berikutnya di list
            except Exception as e: 
                pass # Lanjut ke provider lain jika Gemini gagal total

        # 2. OPENAI (GPT-4/3.5)
        if self.keys.get("openai") and 'openai' in sys.modules:
            try:
                client = openai.OpenAI(api_key=self.keys["openai"])
                # Coba GPT-4o dulu, fallback ke 3.5
                for m in ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]:
                    try:
                        res = client.chat.completions.create(
                            model=m, messages=[{"role": "user", "content": prompt}]
                        )
                        return res.choices[0].message.content
                    except: continue
            except: pass

        # 3. MISTRAL
        if self.keys.get("mistral") and 'mistralai' in sys.modules:
            try:
                client = MistralClient(api_key=self.keys["mistral"])
                res = client.chat(model="mistral-large-latest", messages=[{"role": "user", "content": prompt}])
                return res.choices[0].message.content
            except: pass

        # 4. OLLAMA (Local AI - Jika punya)
        if self.keys.get("ollama_url"):
            try:
                res = requests.post(f"{self.keys['ollama_url']}/api/generate", 
                                  json={"model": "llama3", "prompt": prompt, "stream": False})
                return res.json()['response']
            except: pass

        # --- FINAL FALLBACK: RAW DATA REPORT ---
        # Jika semua AI Gagal/Error/404/Quota Habis, kembalikan Data Mentah.
        # Jangan kembalikan pesan error, tapi kembalikan Prompt-nya sendiri (yang berisi data scan).
        
        fallback_report = f"""
# AUTOMATED SCAN REPORT (RAW DATA MODE)
**NOTE:** The AI Analysis Engine failed to respond (API Error/Quota Exceeded). 
Below is the raw intelligence data collected from the target.

## Target Intelligence
{prompt}

## Recommended Actions (Generic)
1. **Analyze Open Ports:** Check if the ports listed above are necessary.
2. **Review Nuclei Hits:** If any CVEs are listed in the JSON data, patch immediately.
3. **Database Security:** If SQLMap showed vulnerabilities, sanitize all input parameters.
        """
        return fallback_report