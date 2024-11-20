import os
import logging
import time
import subprocess
from urllib.request import Request, urlopen
import requests
from dotenv import load_dotenv
import shutil  # Required for file operations like copyfile

# Constants for file names
POTFILE = os.getenv("POTFILE", "wpa-sec.founds.potfile")
CRACKED_FILE = os.getenv("CRACKED_FILE", "my-cracked.txt")
NETWORKS_FILE = os.getenv("NETWORKS_FILE", "networks.txt")
DONE_FILE = os.getenv("DONE_FILE", "networks_done.txt")


# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def download_file(url, cookie_value, output_file):
    """Downloads a file from the given URL using a cookie for authentication."""
    try:
        req = Request(url, headers={'Cookie': f'key={cookie_value}'})
        with urlopen(req) as response, open(output_file, "wb") as out_file:
            out_file.write(response.read())
        logger.info(f"File {output_file} downloaded successfully.")
    except Exception as e:
        logger.error(f"Error downloading file {output_file}: {e}")
        raise


def process_potfile(input_file, unique_networks):
    """Processes the downloaded potfile and extracts unique networks."""
    try:
        with open(input_file, "r", encoding="utf-8") as potfile:
            lines = potfile.readlines()

        for line in lines:
            parts = line.strip().split(":")
            if len(parts) >= 4:
                unique_networks.add(":".join(parts[2:4]))
        logger.info(f"Processed {input_file} and extracted unique networks.")
    except FileNotFoundError:
        logger.warning(f"File {input_file} not found. Skipping processing.")
    except UnicodeDecodeError as e:
        logger.error(f"Error decoding {input_file}: {e}")


def process_cracked_file(input_file, unique_networks):
    """Adds networks from the cracked file to the set of unique networks."""
    try:
        with open(input_file, "r", encoding="utf-8") as cracked_file:
            lines = cracked_file.readlines()

        for line in lines:
            unique_networks.add(line.strip())
        logger.info(f"Processed {input_file} and added networks to the set.")
    except FileNotFoundError:
        logger.warning(f"File {input_file} not found. Continuing without it.")


def save_unique_networks(output_file, unique_networks):
    """Saves unique networks to a file."""
    try:
        with open(output_file, "w", encoding="utf-8") as output:
            for network in sorted(unique_networks):
                output.write(f"{network}\n")
        logger.info(f"Unique networks saved to {output_file}.")
    except OSError as e:
        logger.error(f"Error saving {output_file}: {e}")


def send_to_discord(webhook_url, file_path):
    """Sends a file to Discord using a webhook."""
    try:
        with open(file_path, "rb") as file:
            response = requests.post(webhook_url, files={"file": file})
        if response.status_code == 204:
            logger.info(f"File {file_path} has been sent to Discord.")
        else:
            logger.warning(f"Failed to send {file_path}. HTTP status code: {response.status_code}")
    except Exception as e:
        logger.error(f"Error sending file {file_path} to Discord: {e}")


def manage_networks(input_file, done_file):
    """Adds new networks to the Wi-Fi configuration using nmcli."""
    if not shutil.which("nmcli"):
        logger.error("nmcli is not installed. Please install it and try again.")
        return

    try:
        with open(input_file, "r") as f:
            all_networks = set(line.strip() for line in f if line.strip())
    except FileNotFoundError:
        logger.error(f"Input file {input_file} not found.")
        return

    try:
        with open(done_file, "r") as f:
            processed_networks = set(line.strip() for line in f if line.strip())
    except FileNotFoundError:
        processed_networks = set()

    new_networks = all_networks - processed_networks

    if not new_networks:
        logger.info("No new networks found to process.")
        return

    try:
        result = subprocess.run(
            ["nmcli", "-t", "-f", "DEVICE,TYPE", "device", "status"],
            capture_output=True,
            text=True,
            check=True
        )
        wifi_device = next(
            (line.split(":")[0] for line in result.stdout.splitlines() if "wifi" in line),
            None
        )
        if not wifi_device:
            logger.error("No Wi-Fi device found.")
            return
    except subprocess.CalledProcessError as e:
        logger.error(f"Error while detecting Wi-Fi device: {e}")
        return

    for network in new_networks:
        try:
            ssid, password = network.split(":")
            command = [
                "nmcli", "connection", "add", "type", "wifi", "ifname", wifi_device,
                "con-name", ssid, "ssid", ssid, "wifi-sec.key-mgmt", "wpa-psk", "wifi-sec.psk", password,
                "connection.autoconnect", "yes"
            ]
            subprocess.run(command, check=True)
            time.sleep(1)
        except ValueError:
            logger.warning(f"Invalid line format in network: {network}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Error adding network {network}: {e}")

    shutil.copyfile(input_file, done_file)
    logger.info(f"Processed networks saved to {done_file}.")


def main():
    load_dotenv()

    cookie_value = os.getenv('COOKIE_VALUE', '')
    url = os.getenv('URL', '')
    discord_webhook_url = os.getenv('DISCORD_WEBHOOK_URL', '')

    if not cookie_value or not url:
        logger.error("Missing COOKIE_VALUE or URL in environment variables.")
        return

    unique_networks = set()

    try:
        download_file(url, cookie_value, POTFILE)
        process_potfile(POTFILE, unique_networks)
        process_cracked_file(CRACKED_FILE, unique_networks)
        save_unique_networks(NETWORKS_FILE, unique_networks)
        if discord_webhook_url:
            send_to_discord(discord_webhook_url, NETWORKS_FILE)
        manage_networks(NETWORKS_FILE, DONE_FILE)
    except Exception as e:
        logger.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()

