import requests
import os

# 🔹 PSX API URL (announcements)
URL = "https://dps.psx.com.pk/announcements/companies"

# 🔹 WhatsApp API (UltraMsg) - Using environment variables for safety
INSTANCE_ID = os.getenv("WHATSAPP_INSTANCE_ID", "instance168787")
TOKEN = os.getenv("WHATSAPP_TOKEN", "fposw4le00f7yreu")
PHONE = os.getenv("WHATSAPP_PHONE", "923322894427")

def get_latest_announcement():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(URL, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        # first/latest announcement
        if "data" in data and len(data["data"]) > 0:
            latest = data["data"][0]
            company = latest.get("symbol", "")
            title = latest.get("title", "")
            date = latest.get("date", "")
            return f"{company} - {title} ({date})"
        else:
            print("Error: No data found in API response")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching announcement: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def read_last():
    try:
        with open("last.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "none"
    except Exception:
        return "none"

def save_last(data):
    with open("last.txt", "w") as f:
        f.write(data)

def send_whatsapp(message):
    url = f"https://api.ultramsg.com/{INSTANCE_ID}/messages/chat"
    payload = {
        "token": TOKEN,
        "to": PHONE,
        "body": message
    }
    try:
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print(f"Error sending WhatsApp: {e}")

def main():
    latest = get_latest_announcement()
    
    if latest is None:
        print("Skipping update due to error.")
        return

    last = read_last()

    if latest != last:
        print("New PSX announcement found!")
        msg = f"📢 PSX Update:\n{latest}"
        send_whatsapp(msg)
        save_last(latest)
    else:
        print("No new update")

if __name__ == "__main__":
    main()