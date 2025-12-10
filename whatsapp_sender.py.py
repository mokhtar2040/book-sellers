# whatsapp_sender.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

class WhatsAppSender:
    def __init__(self):
        self.driver = webdriver.Chrome()  # تحتاج ChromeDriver
        self.driver.get("https://web.whatsapp.com")
        print("🔍 يرجى مسح QR Code يدوياً...")
        time.sleep(15)  # وقت للمسح اليدوي
    
    def send_message(self, phone_number, message):
        """إرسال رسالة إلى رقم معين"""
        try:
            # الانتقال إلى الدردشة مع الرقم
            chat_url = f"https://web.whatsapp.com/send?phone={phone_number}"
            self.driver.get(chat_url)
            time.sleep(5)
            
            # إدخال الرسالة وإرسالها
            message_box = self.driver.find_element(By.XPATH, '//div[@contenteditable="true"]')
            message_box.send_keys(message)
            message_box.send_keys(Keys.ENTER)
            
            print(f"✅ تم الإرسال إلى {phone_number}")
            time.sleep(2)
            
            return True
        except Exception as e:
            print(f"❌ خطأ في الإرسال إلى {phone_number}: {e}")
            return False
    
    def close(self):
        self.driver.quit()

# استخدام المثال
# sender = WhatsAppSender()
# sender.send_message("966501234567", "رابط كتابك: https://...")
# sender.close()