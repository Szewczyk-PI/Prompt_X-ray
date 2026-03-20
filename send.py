import requests
import os
import re
import csv
import sys
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("API_TOKEN")

MONTHS = {
      "sty": 1, "lut": 2, "mar": 3, "kwi": 4, "maj": 5, "cze": 6,
      "lip": 7, "sie": 8, "wrz": 9, "paź": 10, "lis": 11, "gru": 12
  }

def parse_date(date_str):
      try:
          parts = date_str.replace(",", "").split()
          day, month, year, time = int(parts[0]), MONTHS[parts[1]], int(parts[2]), parts[3]
          return datetime(year, month, day, *map(int, time.split(":")))
      except:
          return datetime.min

def query(uuid: str):
      response = requests.get(
          url=f"https://mind.cyberfolks.pl/api/query/{uuid}",
          headers={"Authorization": f"Bearer {TOKEN}"}
      )
      response.raise_for_status()
      return response.json()

print("Wklej tekst i nacisnij Ctrl+Z + Enter:")
lines = [line.rstrip() for line in sys.stdin if line.strip()]

lines.sort(key=lambda l: parse_date(re.search(r'\d{1,2} \w+ \d{4}, \d{2}:\d{2}:\d{2}', l).group(0) if re.search(r'\d{1,2} \w+ \d{4}, \d{2}:\d{2}:\d{2}', l) else ""))

with open("wynik.csv", "w", newline="", encoding="utf-8-sig") as f:
      writer = csv.writer(f, delimiter="\t")
      #writer.writerow(["Data", "UUID", "Grupa zapytań"])
      for line in lines:
          uuid_match = re.search(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', line)
          date_match = re.search(r'\d{1,2} \w+ \d{4}, \d{2}:\d{2}:\d{2}', line)
          if not uuid_match:
              continue
          uuid = uuid_match.group(0)
          data = date_match.group(0) if date_match else "Brak daty"
          try:
              result = query(uuid)
              genesys_id = result["data"]["genesys_conversation_id"]
              writer.writerow([data, uuid, genesys_id])
          except Exception as e:
              writer.writerow([data, uuid, f"Błąd: {e}"])

print("Zapisano do wynik.csv")