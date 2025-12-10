# app.py
from flask import Flask, request, jsonify, send_file
from database import Database
import requests
import os
from datetime import datetime

app = Flask(__name__)
db = Database()

# إعدادات WhatsApp (استخدم Twilio أو خدمة مشابهة)
WHATSAPP_API_URL = "https://api.twilio.com/2010-04-01/Accounts/{}/Messages.json"
WHATSAPP_FROM_NUMBER = "whatsapp:+14155238886"  # رقم Twilio التجريبي

@app.route('/api/add-customer', methods=['POST'])
def add_customer():
    """إضافة مشتري جديد وإرسال الرابط له"""
    try:
        data = request.json
        name = data.get('name')
        phone = data.get('phone')
        email = data.get('email', '')
        amount = float(data.get('amount', 0))
        
        # تنظيف رقم الهاتف
        phone = phone.replace('+', '').replace(' ', '')
        if not phone.startswith('966'):  # إذا كان رقم سعودي
            phone = '966' + phone.lstrip('0')
        
        # إضافة المشتري إلى قاعدة البيانات
        customer_id = db.add_customer(name, phone, email, amount)
        
        # توليد رابط التحميل السري
        download_url, secret_key = db.generate_download_link(customer_id)
        
        # إرسال الرابط عبر WhatsApp
        message = f"""
        🎉 تهانينا {name}!

        ✅ تم تأكيد شرائك للكتاب الإلكتروني بنجاح.

        📖 رابط تحميل الكتاب (صالح لمدة 24 ساعة):
        {download_url}

        ⚠️ ملاحظة: هذا الرابط صالح للاستخدام لمرة واحدة فقط.

        شكراً لثقتك بنا! 📚
        """
        
        # إرسال عبر WhatsApp
        send_whatsapp_message(phone, message)
        
        # إرسال عبر البريد الإلكتروني (إذا وجد)
        if email:
            send_email(email, "رابط تحميل الكتاب الإلكتروني", message)
        
        return jsonify({
            'success': True,
            'message': 'تم إرسال الرابط بنجاح',
            'download_url': download_url,
            'customer_id': customer_id
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

def send_whatsapp_message(to_phone, message):
    """إرسال رسالة عبر WhatsApp"""
    # هذه دالة تجريبية - تحتاج إلى إعداد Twilio فعلي
    try:
        # إذا كان لديك حساب Twilio فعلي
        # account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        # auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        
        # payload = {
        #     'From': WHATSAPP_FROM_NUMBER,
        #     'To': f'whatsapp:+{to_phone}',
        #     'Body': message
        # }
        
        # response = requests.post(
        #     WHATSAPP_API_URL.format(account_sid),
        #     auth=(account_sid, auth_token),
        #     data=payload
        # )
        
        # بديل مؤقت: طباعة الرسالة للاختبار
        print(f"📱 WhatsApp إلى {to_phone}:")
        print(message)
        print("-" * 50)
        
        return True
    except Exception as e:
        print(f"خطأ في إرسال WhatsApp: {e}")
        return False

@app.route('/download', methods=['GET'])
def download_book():
    """صفحة تحميل الكتاب (تتحقق من المفتاح السري)"""
    secret_key = request.args.get('key')
    
    if not secret_key:
        return "رابط غير صالح", 400
    
    # التحقق من صحة المفتاح
    cursor = db.conn.cursor()
    cursor.execute('''
        SELECT dl.*, c.name 
        FROM download_links dl
        JOIN customers c ON dl.customer_id = c.id
        WHERE dl.secret_key = ? 
        AND dl.is_used = 0
        AND datetime(dl.expires_at) > datetime('now')
    ''', (secret_key,))
    
    link_data = cursor.fetchone()
    
    if not link_data:
        return """
        <div style="text-align: center; padding: 50px; font-family: Arial;">
            <h2 style="color: red;">⛔ رابط غير صالح</h2>
            <p>قد يكون الرابط:</p>
            <ul>
                <li>منتهي الصلاحية (صالح لمدة 24 ساعة فقط)</li>
                <li>مستخدم مسبقاً</li>
                <li>غير صحيح</li>
            </ul>
            <p>يرجى التواصل مع الدعم إذا كنت تواجه مشكلة.</p>
        </div>
        """, 403
    
    # تحديث حالة الرابط كمستخدم
    db.mark_link_as_used(secret_key)
    
    # هنا يمكنك:
    # 1. إعادة توجيه إلى رابط التحميل المباشر
    # 2. عرض زر التحميل
    # 3. عرض الكتاب مباشرة في المتصفح
    
    return f"""
    <!DOCTYPE html>
    <html dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>تحميل الكتاب</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                text-align: center;
                padding: 50px;
                background-color: #f5f5f5;
            }}
            .container {{
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
                max-width: 500px;
                margin: 0 auto;
            }}
            .btn {{
                background-color: #4CAF50;
                color: white;
                padding: 15px 30px;
                text-decoration: none;
                border-radius: 5px;
                display: inline-block;
                margin-top: 20px;
                font-size: 18px;
            }}
            .warning {{
                color: #ff9800;
                margin-top: 20px;
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎉 تهانينا {link_data[6]}!</h1>
            <p>يمكنك الآن تحميل الكتاب الإلكتروني</p>
            <a href="/static/ebook.pdf" class="btn" download="الكتاب_الإلكتروني.pdf">
                ⬇️ تحميل الكتاب الآن
            </a>
            <div class="warning">
                ⚠️ هذا الرابط صالح للاستخدام لمرة واحدة فقط
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/api/bulk-send', methods=['POST'])
def bulk_send():
    """إرسال جماعي للمشترين المعلقين"""
    cursor = db.conn.cursor()
    cursor.execute('''
        SELECT c.id, c.name, c.phone, c.email
        FROM customers c
        LEFT JOIN download_links dl ON c.id = dl.customer_id
        WHERE dl.id IS NULL OR c.status = 'pending'
    ''')
    
    pending_customers = cursor.fetchall()
    results = []
    
    for customer in pending_customers:
        customer_id, name, phone, email = customer
        
        try:
            # توليد رابط جديد
            download_url, _ = db.generate_download_link(customer_id)
            
            # إرسال الرسالة
            message = f"عزيزي {name}، رابط تحميل كتابك: {download_url}"
            send_whatsapp_message(phone, message)
            
            # تحديث الحالة
            cursor.execute('UPDATE customers SET status = "sent" WHERE id = ?', (customer_id,))
            
            results.append({
                'phone': phone,
                'status': 'success',
                'download_url': download_url
            })
        except Exception as e:
            results.append({
                'phone': phone,
                'status': 'failed',
                'error': str(e)
            })
    
    db.conn.commit()
    return jsonify({'results': results, 'total': len(results)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)