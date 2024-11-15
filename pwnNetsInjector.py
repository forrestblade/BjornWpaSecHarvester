import time
import shutil

def process_networks():
    input_file = "networks.txt"
    done_file = "networks_done.txt"
    
    try:
        with open(input_file, "r") as f:
            all_networks = set(line.strip() for line in f if line.strip())
    except FileNotFoundError:
        print(f"I can't find {input_file} file.")
        return

    try:
        with open(done_file, "r") as f:
            processed_networks = set(line.strip() for line in f if line.strip())
    except FileNotFoundError:
        processed_networks = set()
    
    new_networks = all_networks - processed_networks

    if not new_networks:
        print("No new networks to process...")
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

    shutil.copy(input_file, done_file)
    print(f"Copy file saved under ne name: {done_file}")

if __name__ == "__main__":
    process_networks()
