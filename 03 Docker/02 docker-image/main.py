import time
from datetime import datetime

while True:
    now = datetime.now()
    formatted_date = now.strftime('%d-%m-%Y')
    with open('data.txt', 'a') as file:
        file.write(f'Data written at: {formatted_date}\n')
    time.sleep(5)  # Wait for 5 seconds before the next entry
    print(f'Log entry added. {formatted_date}\n')