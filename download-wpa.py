from urllib.request import Request, urlopen
from dotenv import load_dotenv
import os
import requests

# Załaduj zmienne z pliku .env
load_dotenv()

# Odczytaj wartości z pliku .env
cookie_value = os.getenv('COOKIE_VALUE')
url = os.getenv('URL')
discord_webhook_url = os.getenv('DISCORD_WEBHOOK_URL')

# Tworzenie zapytania z nagłówkiem cookie
req = Request(url, headers={'Cookie': f'key={cookie_value}'})

# Pobieranie pliku
with urlopen(req) as response, open('wpa-sec.founds.potfile', 'wb') as out_file:
    out_file.write(response.read())

print("Plik pobrany pomyślnie.")

# Wczytanie danych z pobranego pliku wpa-sec.founds.potfile z poprawnym kodowaniem (utf-8)
with open("wpa-sec.founds.potfile", "r", encoding="utf-8") as potfile:
    lines = potfile.readlines()

# Przechowywanie unikalnych sieci (SSID + hasło)
unique_networks = set()

# Przetwarzanie linii z wpa-sec.founds.potfile
for line in lines:
    # Podzielenie linii po separatorze ":"
    parts = line.strip().split(":")
    
    # Jeżeli linia ma mniej niż 4 części, ignoruj ją
    if len(parts) < 4:
        continue

    # Zachowanie ostatnich dwóch części (SSID + hasło)
    network_info = f"{parts[2]}:{parts[3]}"
    
    # Dodanie do zbioru unikalnych sieci
    unique_networks.add(network_info)

# Wczytanie danych z my-cracked.txt i dodanie ich do zbioru unikalnych sieci
with open("my-cracked.txt", "r", encoding="utf-8") as cracked_file:
    cracked_lines = cracked_file.readlines()

for line in cracked_lines:
    # Podzielenie linii po separatorze ":"
    network_info = line.strip()
    
    # Dodanie do zbioru unikalnych sieci
    unique_networks.add(network_info)

# Zapisanie unikalnych sieci do pliku networks.txt z kodowaniem utf-8
with open("networks.txt", "w", encoding="utf-8") as output_file:
    for network in sorted(unique_networks):
        output_file.write(f"{network}\n")

print("Duplikaty usunięte i dane zapisane do networks.txt")

# Wysyłanie pliku networks.txt do Discorda za pomocą webhooka
with open("networks.txt", "rb") as file:
    response = requests.post(discord_webhook_url, files={"file": file})

if response.status_code == 204:
    print("Plik networks.txt został wysłany do Discorda.")
else:
    print(f"Nie udało się wysłać pliku. Kod błędu: {response.status_code}")
 