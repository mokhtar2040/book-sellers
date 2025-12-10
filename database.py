# database.py
import sqlite3
import secrets
import string
from datetime import datetime

class Database:
    def __init__(self, db_name='ebook_store.db'):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        
        # جدول المشترين
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT UNIQUE NOT NULL,
                email TEXT,
                amount_paid REAL,
                purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pending'
            )
        ''')
        
        # جدول الروابط السرية
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS download_links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                secret_key TEXT UNIQUE NOT NULL,
                download_url TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                is_used INTEGER DEFAULT 0,
                used_at TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers (id)
            )
        ''')
        
        self.conn.commit()
    
    def add_customer(self, name, phone, email, amount):
        """إضافة مشتري جديد"""
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO customers (name, phone, email, amount_paid)
                VALUES (?, ?, ?, ?)
            ''', (name, phone, email, amount))
            customer_id = cursor.lastrowid
            self.conn.commit()
            return customer_id
        except sqlite3.IntegrityError:
            # إذا كان الرقم موجود بالفعل
            cursor.execute('SELECT id FROM customers WHERE phone = ?', (phone,))
            return cursor.fetchone()[0]
    
    def generate_download_link(self, customer_id, base_url="https://yourdomain.com/download"):
        """توليد رابط تحميل سري لمرة واحدة"""
        # توليد مفتاح سري عشوائي
        alphabet = string.ascii_letters + string.digits
        secret_key = ''.join(secrets.choice(alphabet) for _ in range(32))
        
        # إنشاء رابط التحميل
        download_url = f"{base_url}?key={secret_key}"
        
        # تاريخ انتهاء (24 ساعة من الآن)
        from datetime import datetime, timedelta
        expires_at = datetime.now() + timedelta(hours=24)
        
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO download_links (customer_id, secret_key, download_url, expires_at)
            VALUES (?, ?, ?, ?)
        ''', (customer_id, secret_key, download_url, expires_at))
        
        self.conn.commit()
        return download_url, secret_key
    
    def get_customer_by_phone(self, phone):
        """الحصول على بيانات المشتري بواسطة رقم الهاتف"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM customers WHERE phone = ?', (phone,))
        return cursor.fetchone()
    
    def mark_link_as_used(self, secret_key):
        """تحديد الرابط كمستخدم"""
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE download_links 
            SET is_used = 1, used_at = CURRENT_TIMESTAMP
            WHERE secret_key = ? AND is_used = 0
        ''', (secret_key,))
        self.conn.commit()
        return cursor.rowcount > 0