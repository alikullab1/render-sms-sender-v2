import requests
import time
from datetime import datetime

# === Server settings ===
url = "https://api.sms-gate.app/3rdparty/v1/message"
username = "XRNXXE"
password = "-vxuufekhppp1x"

# === Load phone numbers ===
with open("numbers.txt", "r", encoding="utf-8") as f:
    phone_numbers = [line.strip() for line in f if line.strip()]

# === Load messages ===
with open("messages.txt", "r", encoding="utf-8") as f:
    messages = [line.strip() for line in f if line.strip()]

# === Track successfully sent numbers ===
sent_numbers = []

# === Function to log sent number ===
def log_sent_number(number):
    with open("sent_log.txt", "a", encoding="utf-8") as log_file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file.write(f"{timestamp} - Sent to {number}\n")

# === Function to send single message with retries ===
def send_single_message(phone_number, message_text, index):
    max_retries = 5
    delay = 10  # seconds
    attempt = 1

    payload = {
        "message": message_text,
        "phoneNumbers": [phone_number]
    }

    while attempt <= max_retries:
        try:
            response = requests.post(
                url,
                json=payload,
                auth=(username, password),
                headers={"Content-Type": "application/json"}
            )

            # Case 1: HTTP 202 → success
            if response.status_code == 202:
                print(f"✅ Message #{index+1} sent (202 Accepted) to: {phone_number}")
                sent_numbers.append(phone_number)
                log_sent_number(phone_number)
                return True

            # Case 2: HTTP 200 + JSON "state": "Pending"
            elif response.status_code == 200:
                try:
                    res_json = response.json()
                    if res_json.get("state") == "Pending":
                        print(f"✅ Message #{index+1} sent (state: Pending) to: {phone_number}")
                        sent_numbers.append(phone_number)
                        log_sent_number(phone_number)
                        return True
                    else:
                        print(f"❌ Message #{index+1} returned unexpected state: {res_json.get('state')}")
                        return False
                except ValueError:
                    print(f"❌ Message #{index+1}: Failed to parse JSON. Response: {response.text}")
                    return False

            # Other codes
            else:
                print(f"❌ HTTP error for message #{index+1}: {response.status_code} - {response.text}")
                return False

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            print(f"⚠️ Network error on attempt {attempt}/{max_retries} for message #{index+1}: {e}")
            if attempt < max_retries:
                print(f"🔁 Retrying in {delay} seconds...")
                time.sleep(delay)
            attempt += 1

    print(f"❌ Failed to send message #{index+1} after {max_retries} attempts.")
    return False

# === Main loop to send one message to one number ===
for i in range(min(len(phone_numbers), len(messages))):
    phone_number = phone_numbers[i]
    message_text = messages[i]

    send_single_message(phone_number, message_text, i)

    if i < len(phone_numbers) - 1:
        print("⏳ Waiting 30 seconds before next message...\n")
        time.sleep(30)

# === Remove sent numbers from numbers.txt ===
remaining_numbers = [num for num in phone_numbers if num not in sent_numbers]

with open("numbers.txt", "w", encoding="utf-8") as f:
    for num in remaining_numbers:
        f.write(num + "\n")

print("\n📁 Sent numbers have been removed from numbers.txt.")
print("📝 Log saved to sent_log.txt.")
