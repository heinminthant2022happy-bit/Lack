import os
import re
import sys
import base64
import random
import string
import time
import asyncio
import aiohttp
import requests
import urllib3

# SSL Error တွေ ဖုန်းတိုင်းမှာ မတက်အောင် ပိတ်ထားတာပါ
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Colors
w, g, y, r, b = "\033[1;00m", "\033[1;32m", "\033[1;33m", "\033[1;31m", "\033[1;34m"

def Logo():
    os.system("clear")
    print(f"{b}ALADDIN - UNIVERSAL FIX{w}")
    print(f"{g}[ Fixed for GitHub Clone & All Devices ]{w}")
    print("-" * 45)

async def get_session_id(session, session_url):
    # Device အဟောင်းတွေပါ Portal က လက်ခံအောင် Browser User-Agent အစုံသုံးထားတယ်
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        # verify_ssl=False က အရေးကြီးဆုံးပါ (Android version အနိမ့်တွေအတွက်)
        async with session.get(session_url, headers=headers, timeout=15, ssl=False) as req:
            final_url = str(req.url)
            match = re.search(r"[?&]sessionId=([a-zA-Z0-9]+)", final_url)
            return match.group(1) if match else None
    except:
        return None

class AladdinTool:
    def __init__(self):
        # GitHub ကနေ clone ရင် binary string တွေ error မတက်အောင် decode handle လုပ်ထားတယ်
        raw_url = b'aHR0cHM6Ly9wb3J0YWwtYXMucnVpamllbmV0d29ya3MuY29tL2FwaS9hdXRoL3dpZmlkb2c/c3RhZ2U9cG9ydGFsJmd3X2lkPTU4YjRiYmNiZmQwZCZnd19zbj1IMVU0MFNYMDExNTA3Jmd3X2FkZHJlc3M9MTkyLjE2OC45OS4xJmd3X3BvcnQ9MjA2MCZpcD0xOTIuMTY4Ljk5LjU0Jm1hYz0zYTpkZDo3ZTo2NDo4NzozNiZzbG90X251bT0xMyZuYXNpcD0xOTIuMTY4LjEuMTczJnNzaWQ9VkxBTjk5JnVzdGF0ZT0wJm1hY19yZXE9MSZ1cmw9aHR0cCUzQSUyRiUyRjE5Mi4xNjguMC4xJTJGJmNoYXBfaWQ9JTVDMzEwJmNoYXBfY2hhbGxlbmdlPSU1QzIxNiU1QzE2MCU1QzEyMiU1QzE3NyU1QzIxNyU1QzM2MCU1QzM2MyU1QzMyMSU1QzA1NiU1QzExMyU1QzIzMiU1QzIyMSU1QzMzMiU1QzI2MCU1QzI1MCU1QzAwMQ=='
        self.session_url = base64.b64decode(raw_url).decode('utf-8', errors='ignore')
        
        # Path ပြဿနာကို ဖြေရှင်းဖို့ Absolute Path သုံးထားပါတယ်
        self.ip_file = os.path.join(os.path.dirname(__file__), ".ip")
        try:
            self.ip = open(self.ip_file, "r").read().strip()
        except:
            self.ip = "192.168.0.1"

    async def keep_alive(self):
        Logo()
        print(f"{g}[+] Keep-Alive Started. Supporting All Devices...{w}")
        # SSL စစ်တာကို လုံးဝ ပိတ်ထားတဲ့ Connector
        connector = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            session_id = None
            while True:
                if not session_id:
                    session_id = await get_session_id(session, self.session_url)
                
                if session_id:
                    params = {'token': session_id, 'phoneNumber': '09' + ''.join(random.choice(string.digits) for _ in range(8))}
                    try:
                        # Timeout ကို နည်းနည်းတိုးထားတယ် (Connection နှေးတဲ့ Device တွေအတွက်)
                        async with session.post(f"http://{self.ip}:2060/wifidog/auth?", params=params, timeout=10) as res:
                            print(f"{w}[{time.strftime('%H:%M:%S')}] Status: {res.status} - Device Active")
                    except:
                        session_id = None # Fail ရင် session ပြန်ယူမယ်
                else:
                    print(f"{r}[!] Waiting for Portal Response...{w}")
                
                await asyncio.sleep(5)

def setup_process():
    Logo()
    ip_file = os.path.join(os.path.dirname(__file__), ".ip")
    print(f"{y}[*] Searching Gateway...{w}")
    try:
        # verify=False က Device အဟောင်းတွေမှာ error မတက်အောင် လုပ်ပေးပါတယ်
        r = requests.get("http://192.168.0.1", timeout=10, verify=False)
        ip_match = re.search('gw_address=(.*?)&', r.url)
        if ip_match:
            ip = ip_match.group(1)
            with open(ip_file, "w") as f: f.write(ip)
            print(f"{g}[+] Setup Success! IP: {ip}{w}")
        else:
            print(f"{r}[!] Portal not detected.{w}")
    except:
        print(f"{r}[!] Connection Failed. Make sure Ruijie WiFi is connected.{w}")
    time.sleep(2)

if __name__ == "__main__":
    tool = AladdinTool()
    while True:
        Logo()
        print("[1] Start Setup\n[2] Start Keep-Alive\n[0] Exit")
        cmd = input(f"\n{y}Select > {w}")
        if cmd == '1':
            setup_process()
        elif cmd == '2':
            try: asyncio.run(tool.keep_alive())
            except KeyboardInterrupt: pass
        elif cmd == '0':
            break
          
