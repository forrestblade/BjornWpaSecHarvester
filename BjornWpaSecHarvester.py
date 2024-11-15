from urllib.request import Request, urlopen
from dotenv import load_dotenv
import os
import requests
import time
import shutil

def download_and_process_file():
    # Load variables from the .env file
    load_dotenv()

    # Read values from the .env file
    cookie_value = os.getenv('COOKIE_VALUE')
    url = os.getenv('URL')
    discord_webhook_url = os.getenv('DISCORD_WEBHOOK_URL')

    # Create a request with a cookie header
    req = Request(url, headers={'Cookie': f'key={cookie_value}'})

    # Download the file
    with urlopen(req) as response, open('wpa-sec.founds.potfile', 'wb') as out_file:
        out_file.write(response.read())

    print("File downloaded successfully.")

    # Read the data from the downloaded file wpa-sec.founds.potfile with proper encoding (utf-8)
    with open("wpa-sec.founds.potfile", "r", encoding="utf-8") as potfile:
        lines = potfile.readlines()

    # Store unique networks (SSID + password)
    unique_networks = set()

    # Process lines from wpa-sec.founds.potfile
    for line in lines:
        # Split the line by the ":" separator
        parts = line.strip().split(":")
        
        # Skip lines with fewer than 4 parts
        if len(parts) < 4:
            continue

        # Retain the last two parts (SSID + password)
        network_info = f"{parts[2]}:{parts[3]}"
        
        # Add to the set of unique networks
        unique_networks.add(network_info)

    # Try to read data from my-cracked.txt and add to the set of unique networks
    try:
        with open("my-cracked.txt", "r", encoding="utf-8") as cracked_file:
            cracked_lines = cracked_file.readlines()

        for line in cracked_lines:
            # Split the line by the ":" separator
            network_info = line.strip()
            
            # Add to the set of unique networks
            unique_networks.add(network_info)
    except FileNotFoundError:
        print("File my-cracked.txt not found. Continuing without it.")

    # Save unique networks to networks.txt with utf-8 encoding
    with open("networks.txt", "w", encoding="utf-8") as output_file:
        for network in sorted(unique_networks):
            output_file.write(f"{network}\n")

    print("Duplicates removed and data saved to networks.txt.")

    # Send the networks.txt file to Discord using the webhook
    with open("networks.txt", "rb") as file:
        response = requests.post(discord_webhook_url, files={"file": file})

    if response.status_code == 204:
        print("File networks.txt has been sent to Discord.")
    else:
        print(f"Failed to send the file. Error code: {response.status_code}")

def process_networks():
    input_file = "networks.txt"
    done_file = "networks_done.txt"

    if not shutil.which("nmcli"):
        print("nmcli is not installed. Please install it and try again.")
        return
    
    try:
        with open(input_file, "r") as f:
            all_networks = set(line.strip() for line in f if line.strip())
    except FileNotFoundError:
        print(f"I can't find the {input_file} file.")
        return

    try:
        with open(done_file, "r") as f:
            processed_networks = set(line.strip() for line in f if line.strip())
    except FileNotFoundError:
        processed_networks = set()
    
    new_networks = all_networks - processed_networks

    if not new_networks:
        print("No new networks found to process....")
        return

    for network in new_networks:
        try:
            ssid, password = network.split(":")
            command = (
                f'sudo nmcli connection add type wifi ifname "*" con-name "{ssid}" ssid "{ssid}" '
                f'&& sudo nmcli connection modify "{ssid}" wifi-sec.key-mgmt wpa-psk wifi-sec.psk "{password}" connection.autoconnect yes'
            )
            print(f"Network: {ssid} injected!")
            time.sleep(1)  # Opóźnienie 1 sekundy
        except ValueError:
            print(f"Invalid line format: {network}")

    shutil.copyfile(input_file, done_file)
    print(f"Copy of the file saved under the name: {done_file}")

if __name__ == "__main__":
    download_and_process_file()
    process_networks()
