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

HOME_PATH = os.path.expanduser("~") 
IP_FILE = os.path.join(HOME_PATH, ".aladdin_ip")
URL_FILE = os.path.join(HOME_PATH, ".aladdin_url") # Portal URL သိမ်းရန်

def Logo():
    os.system("clear")
    print(f"{b}    ___    __    ___    ____  ____  _____  _   __")
    print(f"   /   |  / /   /   |  / __ \/ __ \/  _/ |/ / / /")
    print(f"  / /| | / /   / /| | / / / / / / // / |   / / / ")
    print(f" / ___ |/ /___/ ___ |/ /_/ / /_/ // / /   |/_/  ")
    print(f"/_/  |_/_____/_/  |_/_____/_____/___//_/|_/(_)  {w}")
    print(f"{g}           [ ALADDIN UNIVERSAL v12.3 ]{w}")
    print("-" * 50)

class AladdinTool:
    def __init__(self):
        # IP ဖတ်ခြင်း
        self.ip = open(IP_FILE, "r").read().strip() if os.path.exists(IP_FILE) else "192.168.110.1"
        # URL ဖတ်ခြင်း (မရှိရင် default သုံးမယ်)
        if os.path.exists(URL_FILE):
            self.session_url = open(URL_FILE, "r").read().strip()
        else:
            self.session_url = ""

    async def keep_alive(self):
        if not self.session_url:
            print(f"{r}[!] Error: Please run Setup (Option 1) first!{w}")
            return
            
        Logo()
        print(f"{g}[+] Internet Keep-Alive Running...{w}")
        print(f"{y}[*] Gateway: {self.ip}{w}")
        
        connector = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            session_id = None
            while True:
                try:
                    if not session_id:
                        # လက်ရှိ Portal URL ကနေ Session ID ကို တိုက်ရိုက်ရှာမယ်
                        async with session.get(self.session_url, timeout=15, ssl=False) as req:
                            final_url = str(req.url)
                            match = re.search(r"sessionId=([a-zA-Z0-9\-]+)", final_url)
                            if match:
                                session_id = match.group(1)
                                print(f"{g}[+] Session ID Found: {session_id}{w}")
                            else:
                                # URL ထဲမှာ တန်းမပါရင် body ထဲမှာ ရှာမယ်
                                text = await req.text()
                                match_body = re.search(r'sessionId\s*:\s*"([a-zA-Z0-9\-]+)"', text)
                                if match_body: session_id = match_body.group(1)

                    if session_id:
                        params = {'token': session_id, 'phoneNumber': '09'+''.join(random.choice(string.digits) for _ in range(8))}
                        async with session.post(f"http://{self.ip}:2060/wifidog/auth?", params=params, timeout=10) as res:
                            print(f"{w}[{time.strftime('%H:%M:%S')}] Status: {res.status} - Online{w}")
                    else:
                        print(f"{r}[!] Waiting for Portal Redirect...{w}", end='\r')
                except Exception as e:
                    session_id = None
                    print(f"{r}[!] Connection lost. Retrying...{w}", end='\r')
                await asyncio.sleep(5)

def setup_process():
    Logo()
    print(f"{y}[*] Initializing Dynamic Setup...{w}")
    # Gateway IP ကို အရင်ဆုံး သတ်မှတ်မယ် (Note 8 အတွက် Manual က ပိုသေချာတယ်)
    ip_input = input(f"{y}[?] Enter Router IP (Default 192.168.110.1): {w}") or "192.168.110.1"
    with open(IP_FILE, "w") as f: f.write(ip_input)

    print(f"{y}[*] Detecting Portal URL (Please wait...){w}")
    try:
        # Google ကို ခေါ်ပြီး Portal ဆီ Redirect ဖြစ်အောင် လုပ်မယ်
        r = requests.get("http://connectivitycheck.gstatic.com/generate_204", timeout=10, verify=False, allow_redirects=True)
        portal_url = r.url
        
        if "http" in portal_url and ip_input in portal_url or "ruijie" in portal_url.lower():
            with open(URL_FILE, "w") as f: f.write(portal_url)
            print(f"{g}[+] Portal URL Captured Successfully!{w}")
            print(f"{w}URL: {portal_url[:50]}...{w}")
        else:
            # တကယ်လို့ Redirect မဖြစ်ရင် Manual URL လိုအပ်နိုင်တယ်
            print(f"{r}[!] Automatic URL capture failed.{w}")
            manual_url = input(f"{y}[?] Please paste the Login Page URL here: {w}")
            if manual_url:
                with open(URL_FILE, "w") as f: f.write(manual_url)
    except Exception as e:
        print(f"{r}[!] Error during setup: {str(e)}{w}")
    
    time.sleep(2)

if __name__ == "__main__":
    while True:
        tool = AladdinTool()
        Logo()
        print(f"{y}Target: {tool.ip}{w}")
        print("-" * 50)
        print("[1] Run Full Setup (Capture Portal)")
        print("[2] Internet Keep-Alive")
        print("[0] Exit")
        choice = input(f"\n{y}Select > {w}")
        if choice == '1': setup_process()
        elif choice == '2':
            try: asyncio.run(tool.keep_alive())
            except KeyboardInterrupt: pass
        elif choice == '0': break
  
