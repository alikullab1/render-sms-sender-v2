import requests
import time
from datetime import datetime

print("🚀 بدء تشغيل السكربت send.py")

# === Server settings ===
url = "https://api.sms-gate.app/3rdparty/v1/message"
username = "OZRO7V"
password = "0itezfj2l0ahqt"

# === Load phone numbers ===
try:
    with open("numbers.txt", "r", encoding="utf-8") as f:
        phone_numbers = [line.strip() for line in f if line.strip()]
    print(f"📞 تم تحميل {len(phone_numbers)} رقم.")
except Exception as e:
    print(f"❌ خطأ أثناء تحميل الأرقام: {e}")
    phone_numbers = []

# === Load messages ===
try:
    with open("messages.txt", "r", encoding="utf-8") as f:
        messages = [line.strip() for line in f if line.strip()]
    print(f"💬 تم تحميل {len(messages)} رسالة.")
except Exception as e:
    print(f"❌ خطأ أثناء تحميل الرسائل: {e}")
    messages = []

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

            if response.status_code == 202:
                print(f"✅ الرسالة رقم {index+1} تم إرسالها إلى: {phone_number} (202 Accepted)")
                sent_numbers.append(phone_number)
                log_sent_number(phone_number)
                return True

            elif response.status_code == 200:
                try:
                    res_json = response.json()
                    if res_json.get("state") == "Pending":
                        print(f"✅ الرسالة رقم {index+1} في حالة Pending إلى: {phone_number}")
                        sent_numbers.append(phone_number)
                        log_sent_number(phone_number)
                        return True
                    else:
                        print(f"⚠️ الحالة غير متوقعة: {res_json.get('state')}")
                        return False
                except ValueError:
                    print(f"❌ لم يتم تحليل الرد JSON. Response: {response.text}")
                    return False
            else:
                print(f"❌ HTTP error: {response.status_code} - {response.text}")
                return False

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            print(f"⚠️ مشكلة بالشبكة (محاولة {attempt}): {e}")
            if attempt < max_retries:
                print(f"🔁 إعادة المحاولة بعد {delay} ثانية...")
                time.sleep(delay)
            attempt += 1

    print(f"❌ فشل إرسال الرسالة رقم {index+1} بعد {max_retries} محاولات.")
    return False

# === Main loop to send one message to one number ===
if phone_numbers and messages:
    for i in range(min(len(phone_numbers), len(messages))):
        phone_number = phone_numbers[i]
        message_text = messages[i]
        send_single_message(phone_number, message_text, i)

        if i < len(phone_numbers) - 1:
            print("⏳ الانتظار 15 ثانية قبل الرسالة التالية...\n")
            time.sleep(15)

    # === Remove sent numbers from numbers.txt ===
    remaining_numbers = [num for num in phone_numbers if num not in sent_numbers]
    with open("numbers.txt", "w", encoding="utf-8") as f:
        for num in remaining_numbers:
            f.write(num + "\n")

    print("\n📁 تم إزالة الأرقام المرسلة من numbers.txt.")
    print("📝 تم حفظ السجل في sent_log.txt.")

else:
    print("⚠️ لا يوجد أرقام أو رسائل لإرسالها.")
