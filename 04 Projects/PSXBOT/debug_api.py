import requests

URL = "https://dps.psx.com.pk/announcements/companies"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://dps.psx.com.pk/announcements",
    "X-Requested-With": "XMLHttpRequest",
    "Connection": "keep-alive",
}

try:
    response = requests.get(URL, headers=headers, timeout=15)
    print(f"Status Code: {response.status_code}")
    print("Content Preview (first 500 chars):")
    print(response.text[:500])
    if response.status_code == 200:
        print("\nSuccess! Data received.")
    else:
        print("\nFailed to bypass maintenance page.")
except Exception as e:
    print(f"Error: {e}")
