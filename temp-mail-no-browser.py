import argparse
import json
import re
import secrets
import time
import webbrowser

import requests

try:
    from colorama import Fore, init

    init(autoreset=True)
except ImportError:  # colors are optional
    class Fore:
        GREEN = RED = CYAN = YELLOW = LIGHTGREEN_EX = ""

    def init(autoreset=True):
        pass

# Base URL for the Mail.tm API
BASE_URL = "https://api.mail.tm"
def banner():
    print("""
    
    ████████╗███████╗███╗   ███╗██████╗     ███╗   ███╗ █████╗ ██╗██╗     
    ╚══██╔══╝██╔════╝████╗ ████║██╔══██╗    ████╗ ████║██╔══██╗██║██║     
       ██║   █████╗  ██╔████╔██║██████╔╝    ██╔████╔██║███████║██║██║     
       ██║   ██╔══╝  ██║╚██╔╝██║██╔═══╝     ██║╚██╔╝██║██╔══██║██║██║     
       ██║   ███████╗██║ ╚═╝ ██║██║         ██║ ╚═╝ ██║██║  ██║██║███████╗
       ╚═╝   ╚══════╝╚═╝     ╚═╝╚═╝         ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝╚══════╝
                                                                     
      
         ██████╗ ███████╗███╗   ██╗███████╗██████╗  █████╗ ████████╗ ██████╗ ██████╗ 
        ██╔════╝ ██╔════╝████╗  ██║██╔════╝██╔══██╗██╔══██╗╚══██╔══╝██╔═══██╗██╔══██╗
        ██║  ███╗█████╗  ██╔██╗ ██║█████╗  ██████╔╝███████║   ██║   ██║   ██║██████╔╝
        ██║   ██║██╔══╝  ██║╚██╗██║██╔══╝  ██╔══██╗██╔══██║   ██║   ██║   ██║██╔══██╗
        ╚██████╔╝███████╗██║ ╚████║███████╗██║  ██║██║  ██║   ██║   ╚██████╔╝██║  ██║
         ╚═════╝ ╚══════╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝
                                                          
        ╔═══════════════════╗   ╔═════════════════════════════════╗
        ║ AmirHossein Zarei ║   ║   Temporary Email Generator     ║
        ╚═══════════════════╝   ╚═════════════════════════════════╝
                  
        🌐 Github:  github.com/a-z-exe
        📱 Telegram: t.me/A_Z_exe
        📷 Instagram: instagram.com/A_Z_exe
    """)
def generate_account():
    """
    Creates a temporary email account and returns the session, email address, and token
    """
    session = requests.Session()

    # Get available domains
    try:
        res = session.get(f"{BASE_URL}/domains", timeout=15)
        res.raise_for_status()
        domains = res.json()["hydra:member"]
    except (requests.RequestException, KeyError, IndexError) as exc:
        print(f"{Fore.RED}[!] Could not load mail.tm domains: {exc}")
        return None, None, None, None

    domain = domains[0]["domain"]

    # Generate a unique username based on timestamp
    username = str(int(time.time() * 1000))[-8:]
    address = f"{username}@{domain}"
    password = secrets.token_urlsafe(12)

    payload = {"address": address, "password": password}
    try:
        res = session.post(f"{BASE_URL}/accounts", json=payload, timeout=15)
    except requests.RequestException as exc:
        print(f"{Fore.RED}[!] Error creating email: {exc}")
        return None, None, None, None

    if res.status_code == 201:
        print(f"{Fore.GREEN}[+] Email created: {address}")
    else:
        print(f"{Fore.RED}[!] Error creating email: {res.text}")
        return None, None, None, None

    # Get authentication token
    try:
        res = session.post(f"{BASE_URL}/token", json=payload, timeout=15)
    except requests.RequestException as exc:
        print(f"{Fore.RED}[!] Error getting token: {exc}")
        return None, None, None, None
    if res.status_code == 200:
        token = res.json()["token"]
        session.headers.update({"Authorization": f"Bearer {token}"})
        return session, address, password, token
    else:
        print(f"{Fore.RED}[!] Error getting token: {res.text}")
        return None, None, None, None

def strip_html(text):
    """
    Removes HTML tags from text
    """
    return re.sub(r'<[^>]*>', ' ', text)

def extract_code(text):
    """
    Extracts verification codes from email text using various patterns
    """
    # Clean the text by removing HTML tags and normalizing spaces
    text = strip_html(text)
    text = re.sub(r'\s+', ' ', text)
    
    # Look for exact patterns with the verification code after them
    specific_patterns = [
        r'verification code is\s+([A-Z0-9]{4,10})\b',
        r'code is\s+([A-Z0-9]{4,10})\b',
        r'verification code\s*[:]\s*([A-Z0-9]{4,10})\b',
    ]
    
    for pattern in specific_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    
    # Try to extract from subject line or any other part of the text
    subject_pattern = r'verification code is\s+([A-Z0-9]{4,10})\b'
    subject_match = re.search(subject_pattern, text, re.IGNORECASE)
    if subject_match:
        return subject_match.group(1)
    
    # If no match found with specific patterns, try to search for isolated code format
    standalone_code_pattern = r'\b([A-Z0-9]{6})\b'  # Looking specifically for 6-character codes
    matches = re.findall(standalone_code_pattern, text)
    if matches:
        # Filter out common HTML/technical terms that might be matched incorrectly
        common_terms = ["HTML", "UTF8", "UTF-8", "HTTPS", "HTTP", "BODY", "HEAD", "TITLE", "META"]
        valid_codes = [m for m in matches if m not in common_terms]
        if valid_codes:
            return valid_codes[0]
    
    return None

def save_code(code, email):
    """
    Saves the verification code to codes.txt file
    """
    with open("codes.txt", "a", encoding="utf-8") as f:
        f.write(f"{email}: {code}\n")
    print(f"{Fore.GREEN}[✓] Code {code} saved to codes.txt")

def save_account_info(email, password, token):
    """
    Save account information to a JSON file
    """
    account_info = {
        "email": email,
        "password": password,
        "token": token,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    with open("account_info.json", "w", encoding="utf-8") as f:
        json.dump(account_info, f, indent=4)

    print(f"{Fore.GREEN}[+] Account information saved to account_info.json")

def open_mail_website(email, password):
    """
    Open the mail.tm website in the default browser
    """
    url = "https://mail.tm/en/"

    print(f"{Fore.CYAN}[*] Opening {url} in your browser")
    print(f"{Fore.CYAN}[*] Use the email: {email}")
    print(f"{Fore.CYAN}[*] Password: {password}")

    webbrowser.open(url)

def check_messages(session, email, wait_time=60, interval=5):
    """
    Checks for new emails and extracts verification codes
    """
    print(f"{Fore.YELLOW}⏳ Checking emails for {wait_time} seconds... Checking every {interval} seconds")

    end_time = time.time() + wait_time
    seen = set()

    while time.time() < end_time:
        res = session.get(f"{BASE_URL}/messages", timeout=15)
        if res.status_code == 200:
            messages = res.json()["hydra:member"]
            for msg in messages:
                if msg["id"] not in seen:
                    seen.add(msg["id"])
                    subject = msg['subject']
                    sender = msg['from']['address']
                    print(f"\n📨 New message: {subject} from {sender}")
                    msg_id = msg["id"]

                    # Get full message content
                    full_msg = session.get(f"{BASE_URL}/messages/{msg_id}", timeout=15).json()
                    text = full_msg.get("text", "") or full_msg.get("html", "")
                    if isinstance(text, list):
                        text = "\n".join(text)

                    # Add subject to text to help with code extraction
                    full_text = f"{subject}\n{text}"
                    
                    # Show preview of content
                    print(f"{Fore.CYAN}📄 Content:\n{text[:300]}")

                    # Extract and save verification code
                    code = extract_code(full_text)
                    if code:
                        print(f"{Fore.LIGHTGREEN_EX}🔑 Verification code found: {code}")
                        save_code(code, email)
        else:
            print(f"{Fore.RED}[!] Error retrieving messages: {res.text}")

        time.sleep(interval)

    print(f"\n{Fore.GREEN}✅ Email checking complete.")

def main():
    parser = argparse.ArgumentParser(
        description="Create a mail.tm inbox and extract verification codes."
    )
    parser.add_argument("--wait", type=int, default=60,
                        help="Seconds to watch for new mail (default: 60)")
    parser.add_argument("--interval", type=int, default=5,
                        help="Seconds between inbox checks (default: 5)")
    parser.add_argument("--open", action="store_true",
                        help="Open the mail.tm website after creating the inbox")
    args = parser.parse_args()

    banner()
    session, email, password, token = generate_account()

    if not session:
        return 1

    save_account_info(email, password, token)

    if args.open:
        open_mail_website(email, password)

    check_messages(session, email, wait_time=args.wait, interval=args.interval)

    if input(f"{Fore.YELLOW}Did you find the verification code manually? (Y/N): ").strip().upper() == "Y":
        code = input(f"{Fore.YELLOW}Enter the verification code: ").strip()
        save_code(code, email)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
