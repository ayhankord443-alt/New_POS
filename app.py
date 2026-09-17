import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template_string, request, send_file, redirect, url_for, send_from_directory, jsonify, session

app = Flask(__name__)
app.secret_key = 'organic_juices_secret_key_2026'

SHARED_PASSWORD = "organic123"

def init_db():
    conn = sqlite3.connect("clean_qayma.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS orders
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  device_id TEXT,
                  item_name TEXT,
                  quantity REAL,
                  unit TEXT,
                  category TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS items
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  category TEXT,
                  item_name TEXT,
                  unit TEXT)''')
                  
    c.execute('''CREATE TABLE IF NOT EXISTS notes
                 (device_id TEXT PRIMARY KEY,
                  note_text TEXT)''')
    
    c.execute("SELECT COUNT(*) FROM items")
    if c.fetchone()[0] == 0:
        default_items = [
            ("فێقی", "نافوكادو", "کیلو"), ("فێقی", "مانكو", "کیلو"), ("فێقی", "موز", "کارتۆن"), 
            ("فێقی", "برتقال", "کیلو"), ("فێقی", "سف", "دانە"), ("فێقی", "ليمون", "کیلو"), 
            ("فێقی", "جويزر", "کیلو"), ("فێقی", "جويز هند", "دانە"), ("فێقی", "هنار", "کیلو"), 
            ("فێقی", "انه ناس", "لبان"), ("فێقی", "خوخ", "کیلو"), ("فێقی", "شاتو", "کیلو"), 
            ("فێقی", "فه صب", "دانە"), ("فێقی", "سندی", "کیلو"), ("فێقی", "كوندور", "کیلو"), 
            ("فێقی", "شوتی", "کیلو"), ("فێقی", "فراولا", "کیلو"), ("فێقی", "كیفی", "کیلو"), 
            ("فێقی", "كاكی", "کیلو"), ("فێقی", "هیزیر", "کیلو"), ("فێقی", "هرميك", "کیلو"),
            
            ("مەعمەل", "خوخ", "کیلو"), ("مەعمەل", "مانكو", "کیلو"), ("مەعمەل", "شاتو", "کیلو"), 
            ("مەعمەل", "انه ناس", "لبان"), ("مەعمەل", "شيرلوكو", "دانە"), ("مەعمەل", "بابه t + ii cm", "دانە"), 
            ("مەعمەل", "تمرهندی مزن", "دانە"), ("مەعمەل", "تمرهندی بجيك", "دانە"), ("مەعمەل", "مویش مزن", "کیلو"), 
            ("مەعمەل", "مویش بجيك", "کیلو"), ("مەعمەل", "به فر", "دانە"), ("مەعمەل", "ئاف", "دانە"), 
            ("مەعمەل", "عصير حليك", "دانە"), ("مەعمەل", "عصير زنجبيل+مانكو", "دانە"), ("مەعمەل", "کرينجوس", "دانە"), 
            ("مەعمەل", "باقركه ری بيستی", "دانە"), ("مەعمەل", "دزهو کردن", "دانە"),
            
            ("مەغزەن", "كلاس+قباغ", "دانە"), ("مەغزەن", "بطل مزن+قباغ", "دانە"), ("مەغزەن", "بطل بجيك+قباغ", "دانە"),
            ("مەغزەن", "قصاب", "دانە"), ("مەغزەن", "كلينيس", "دانە"), ("مەغزەن", "بوكس (۲)", "دانە"), 
            ("مەغزەن", "بوكس (٤)", "دانە"), ("مەغزەن", "بوكس (٦)", "دانە"), ("مەغزەن", "علاكه لوكو", "دانە"), 
            ("مەغزەن", "علاكه زلال", "دانە"), ("مەغزەن", "زاهی", "دانە"), ("مەغزەن", "كليت", "دانە"), 
            ("مەغزەن", "باس باس", "کیلو"), ("مەغزەن", "باته", "کیلو"), ("مەغزەن", "مساحه", "دانە"), 
            ("مەغزەن", "فرجه", "دانە"), ("مەغزەن", "دسكورك", "دانە"), ("مەغزەن", "وره فه كاشير", "دانە"), 
            ("مەغزەن", "بوكس فواكه", "دانە"), ("مەغزەن", "جتل", "دانە"), ("مەغزەن", "قباغ", "دانە"), 
            ("مەغزەن", "كلاس تيست", "دانە"), ("مەغزەن", "جامسی", "دانە"), ("مەغزەن", "معتر جو", "دانە"), 
            ("مەغزەن", "خارنا بالندا", "دانە")
        ]
        c.executemany("INSERT INTO items (category, item_name, unit) VALUES (?, ?, ?)", default_items)
        conn.commit()
    conn.close()

init_db()

def get_all_items_dict():
    conn = sqlite3.connect("clean_qayma.db")
    c = conn.cursor()
    c.execute("SELECT category, item_name, unit FROM items")
    rows = c.fetchall()
    conn.close()
    
    items_dict = {}
    for cat, name, unit in rows:
        if cat not in items_dict:
            items_dict[cat] = []
        items_dict[cat].append((name, unit))
    return items_dict

LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="ku" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>چوونەژوورەوە - ئۆرگانیک جویس</title>
    <style>
        body { font-family: system-ui, -apple-system, sans-serif; background-color: #f7f9f6; margin: 0; padding: 20px; display: flex; justify-content: center; align-items: center; height: 100vh; text-align: center; color: #1a1a1a; box-sizing: border-box; }
        .card { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.08); width: 100%; max-width: 360px; border: 1px solid #e0e0e0; }
        h2 { color: #1b5e20; margin-bottom: 10px; font-size: 22px; }
        input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ccc; border-radius: 6px; box-sizing: border-box; font-size: 15px; }
        button { width: 100%; padding: 12px; background: #2e7d32; color: white; border: none; border-radius: 6px; font-size: 16px; cursor: pointer; font-weight: bold; margin-top: 10px; }
        button:hover { background: #1b5e20; }
        .bio-btn { background: #1b5e20; margin-top: 8px; display: none; font-size: 16px; padding: 14px; }
        .error { color: #c62828; margin-bottom: 10px; font-size: 14px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="card">
        <h2>ئۆرگانیک جویس</h2>
        <p style="color: #555; margin-top: 0; font-size: 13px;">جارا ئێكێ ڕەمزی گشتی بنڤیسە، ژ بۆ جارێن داهاتی ب فەیس ئایدی / پەنجەمۆر بچۆ ژوورەوە</p>
        {% if error %}<div class="error">{{ error }}</div>{% endif %}
        <form method="POST" id="loginForm">
            <input type="password" name="password" id="passwordInput" placeholder="ڕەمز (Password)" required>
            <button type="submit">چوونەژوورەوە ب ڕەمز</button>
        </form>
        <button type="button" id="bioBtn" class="bio-btn" onclick="loginWithBiometric()">🔒 چوونەژوورەوە ب فەیس ئایدی / پەنجەمۆر</button>
    </div>

    <script>
        document.addEventListener("DOMContentLoaded", async () => {
            let savedPass = localStorage.getItem("organic_saved_pass");
            let bioRegistered = localStorage.getItem("organic_bio_registered");
            if (savedPass) {
                document.getElementById("bioBtn").style.display = "block";
                if (bioRegistered === "true") { setTimeout(loginWithBiometric, 400); }
            }
        });
        document.getElementById("loginForm").addEventListener("submit", () => {
            let pass = document.getElementById("passwordInput").value;
            if(pass) {
                localStorage.setItem("organic_saved_pass", pass);
                localStorage.setItem("organic_bio_registered", "true");
            }
        });
        async function loginWithBiometric() {
            let savedPass = localStorage.getItem("organic_saved_pass");
            if (!savedPass) return;
            try {
                if (window.PublicKeyCredential && PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable) {
                    let available = await PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable();
                    if (available) {
                        const challenge = new Uint8Array([19, 21, 31, 41, 51, 61, 71, 81]);
                        await navigator.credentials.create({
                            publicKey: {
                                rp: { name: "Organic Juices Cashier" },
                                user: { id: new Uint8Array([1, 2, 3, 4, 5]), name: "cashier", displayName: "Organic Cashier" },
                                challenge: challenge,
                                pubKeyCredParams: [{ alg: -7, type: "public-key" }, { alg: -257, type: "public-key" }],
                                timeout: 60000,
                                authenticatorSelection: { authenticatorAttachment: "platform", userVerification: "required" }
                            }
                        });
                    }
                }
            } catch (e) {}
            let form = document.createElement("form");
            form.method = "POST";
            let input = document.createElement("input");
            input.type = "hidden"; input.name = "password"; input.value = savedPass;
            form.appendChild(input);
            document.body.appendChild(form);
            form.submit();
        }
    </script>
</body>
</html>
"""

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ku" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>کۆمپانییا ئورگانیک جویس</title>
    
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="ئۆرگانیک جویس">
    <link rel="apple-touch-icon" href="/logo.png">

    <style>
        body { 
            font-family: system-ui, -apple-system, sans-serif; 
            background-color: #ffffff; 
            margin: 0; 
            padding: 15px; 
            text-align: center; 
            color: #1a1a1a;
            position: relative;
        }
        body::before {
            content: "";
            background-image: url('/logo.png');
            background-repeat: no-repeat;
            background-position: center top 130px;
            background-size: 280px;
            opacity: 0.08;
            position: fixed;
            top: 0; left: 0; bottom: 0; right: 0;
            z-index: -1;
        }
        .brand-header { 
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px; 
            padding-bottom: 10px;
            border-bottom: 3px solid #2e7d32;
        }
        .brand-header h1 { margin: 0; font-size: 18px; font-weight: 900; color: #1b5e20; }
        .user-panel { display: flex; align-items: center; gap: 8px; font-size: 13px; }
        .nav-link { background-color: #2e7d32; color: white; padding: 6px 10px; border-radius: 4px; text-decoration: none; font-weight: bold; font-size: 12px; }
        .logout-btn { background-color: #c62828; color: white; padding: 6px 10px; border-radius: 4px; text-decoration: none; font-weight: bold; font-size: 12px; }
        
        .note-box { background: #f9fbe7; border: 1px solid #cddc39; border-radius: 8px; padding: 12px; margin-bottom: 20px; text-align: right; }
        .note-box textarea { width: 100%; height: 60px; padding: 8px; border: 1px solid #ccc; border-radius: 6px; font-family: inherit; font-size: 13px; box-sizing: border-box; resize: vertical; }
        .note-save-btn { background: #558b2f; color: white; border: none; padding: 6px 12px; border-radius: 4px; font-weight: bold; font-size: 12px; cursor: pointer; margin-top: 6px; }

        .section-title { text-align: right; margin: 25px 5px 10px 5px; color: #2e7d32; font-size: 18px; font-weight: bold; border-bottom: 2px solid #2e7d32; padding-bottom: 4px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); gap: 10px; margin-bottom: 10px; }
        .item-card { background: #ffffff; border-radius: 8px; padding: 10px 6px; box-shadow: 0 2px 5px rgba(0,0,0,0.08); display: flex; flex-direction: column; justify-content: space-between; border: 1px solid #e0e0e0; }
        .item-name { font-weight: bold; font-size: 13px; margin-bottom: 2px; color: #111; }
        .unit-tag { font-size: 11px; color: #558b2f; font-weight: 600; margin-bottom: 6px; }
        .btn-group { display: flex; gap: 3px; align-items: center; justify-content: center; }
        .qty-btn { background: #e0e0e0; border: none; font-weight: bold; width: 26px; height: 28px; border-radius: 4px; cursor: pointer; font-size: 14px; color: #333; }
        .qty-btn:active { background: #ccc; }
        .qty-input { width: 34px; padding: 4px 1px; text-align: center; border: 1px solid #ccc; border-radius: 4px; font-size: 13px; font-weight: bold; }
        .btn-add { background: #2e7d32; color: white; border: none; padding: 6px 4px; border-radius: 4px; font-weight: bold; font-size: 11px; cursor: pointer; flex: 1; }
        .btn-add.added { background: #388e3c; transform: scale(0.96); }
        .order-summary { background: #ffffff; border-radius: 10px; padding: 15px; margin-top: 25px; text-align: right; box-shadow: 0 4px 12px rgba(0,0,0,0.1); border: 2px solid #2e7d32; }
        .pdf-btn { background: #2c3e50; color: white; width: 100%; padding: 12px; border: none; border-radius: 6px; font-weight: bold; font-size: 15px; margin-top: 10px; cursor: pointer; }
        .clear-btn { background-color: #c62828; color: white; width: 100%; padding: 9px; border: none; border-radius: 6px; font-weight: bold; margin-top: 6px; cursor: pointer; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { border-bottom: 1px solid #eee; padding: 8px; text-align: right; font-size: 13px; }
        th { background-color: #f5f5f5; color: #2e7d32; }
    </style>
</head>
<body>
    <div class="brand-header">
        <h1>کۆمپانییا ئورگانیک جویس</h1>
        <div class="user-panel">
            <a href="/settings" class="nav-link">⚙️ سێتینگ (زێدەکرن و ژێبرن)</a>
            <a href="/logout" class="logout-btn">چوونەدەروون</a>
        </div>
    </div>

    <div class="note-box">
        <label for="noteInput" style="font-weight: bold; color: #33691e; font-size: 13px; display: block; margin-bottom: 5px;">📝 تێبینی (ل سەر فۆرماتێ دێ دیار بیت):</label>
        <textarea id="noteInput" placeholder="تێبینییا خۆ لێرە بنڤیسە...">{{ current_note }}</textarea>
        <button type="button" class="note-save-btn" onclick="saveNote()">تومارکرنا تێبینیێ</button>
    </div>

    {% for cat, items in all_items.items() %}
        <div class="section-title">🔸 {{ cat }}</div>
        <div class="grid">
            {% for item_name, unit in items %}
            <div class="item-card">
                <div>
                    <div class="item-name">{{ item_name }}</div>
                    <div class="unit-tag">({{ unit }})</div>
                </div>
                <form onsubmit="quickAddAjax(event, this)" class="btn-group">
                    <input type="hidden" name="item_name" value="{{ item_name }}">
                    <input type="hidden" name="unit" value="{{ unit }}">
                    <input type="hidden" name="category" value="{{ cat }}">
                    <button type="button" class="qty-btn" onclick="adjustQty(this, -1)">-</button>
                    <input type="number" name="quantity" value="1" step="any" class="qty-input">
                    <button type="button" class="qty-btn" onclick="adjustQty(this, 1)">+</button>
                    <button type="submit" class="btn-add">زێدەکه</button>
                </form>
            </div>
            {% endfor %}
        </div>
    {% endfor %}

    <div class="order-summary" id="orderSummaryContainer" style="display: {% if orders %}block{% else %}none{% endif %};">
        <h3 style="margin: 0 0 10px 0; color: #1b5e20;">📋 لیستا داواکری (قایمە):</h3>
        <table id="ordersTable">
            <thead>
                <tr>
                    <th>بابەت</th>
                    <th>بڕ</th>
                    <th>یەکە</th>
                </tr>
            </thead>
            <tbody id="ordersTableBody">
                {% for item in orders %}
                <tr>
                    <td><b>{{ item[1] }}</b></td>
                    <td>{{ item[2] }}</td>
                    <td>{{ item[3] }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        <button type="button" class="pdf-btn" onclick="openInvoicePage()">📄 ڤێکرنا قایمەی ب شێوەیەکێ خاوێن</button>
        <button type="button" class="clear-btn" onclick="clearOrdersAjax()">🗑️ پاککرنا قایمەی</button>
    </div>

    <script>
        function adjustQty(btn, amount) {
            let input = btn.parentElement.querySelector('.qty-input');
            let currentVal = parseFloat(input.value) || 1;
            let newVal = currentVal + amount;
            if (newVal < 0.1) newVal = 0.1;
            input.value = newVal;
        }

        async function saveNote() {
            let noteText = document.getElementById('noteInput').value;
            let formData = new FormData();
            formData.append('note', noteText);
            try {
                let response = await fetch('/save_note', { method: 'POST', body: formData });
                let data = await response.json();
                if(data.status === 'success') {
                    alert('تێبینی ب سەرکەفتیانە هاتە تومارکرن!');
                }
            } catch(e) { console.error(e); }
        }

        async function quickAddAjax(event, form) {
            event.preventDefault();
            let formData = new FormData(form);
            let btn = form.querySelector('.btn-add');
            try {
                let response = await fetch('/quick_add_ajax', { method: 'POST', body: formData });
                let data = await response.json();
                if (data.status === 'success') {
                    updateOrdersTable(data.orders);
                    btn.classList.add('added');
                    setTimeout(() => btn.classList.remove('added'), 300);
                }
            } catch (err) { console.error(err); }
        }

        async function clearOrdersAjax() {
            try {
                let response = await fetch('/clear_ajax');
                let data = await response.json();
                if (data.status === 'success') { updateOrdersTable([]); }
            } catch (err) { console.error(err); }
        }

        function updateOrdersTable(orders) {
            let container = document.getElementById('orderSummaryContainer');
            let tbody = document.getElementById('ordersTableBody');
            if (orders.length === 0) {
                container.style.display = 'none';
                tbody.innerHTML = '';
                return;
            }
            container.style.display = 'block';
            tbody.innerHTML = orders.map(item => `
                <tr>
                    <td><b>${item.item_name}</b></td>
                    <td>${item.quantity}</td>
                    <td>${item.unit}</td>
                </tr>
            `).join('');
        }

        function openInvoicePage() {
            window.open('/invoice_view', '_blank');
        }
    </script>
</body>
</html>
"""

INVOICE_TEMPLATE = """
<!DOCTYPE html>
<html lang="ku" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Organic_Juices_Qayma</title>
    <style>
        body {
            font-family: system-ui, -apple-system, sans-serif;
            background: #f0f0f0;
            color: #1a1a1a;
            margin: 0;
            padding: 20px;
            direction: rtl;
            text-align: right;
        }
        .invoice-container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border: 1px solid #dcdcdc;
            border-radius: 4px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            position: relative;
            overflow: hidden;
        }
        .watermark-logo {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 320px;
            opacity: 0.06;
            z-index: 0;
            pointer-events: none;
        }
        .invoice-container * {
            position: relative;
            z-index: 1;
        }
        .header-title {
            text-align: center;
            color: #2c3e50;
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .header-date {
            text-align: center;
            color: #555;
            font-size: 12px;
            margin-bottom: 15px;
        }
        .note-alert {
            text-align: left;
            color: #333;
            font-size: 13px;
            margin-bottom: 15px;
            font-weight: 500;
        }
        .category-section {
            margin-bottom: 20px;
        }
        .category-title {
            text-align: right;
            color: #2c3e50;
            font-size: 14px;
            font-weight: bold;
            margin-bottom: 5px;
            margin-top: 15px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 10px;
        }
        th, td {
            border: 1px solid #dcdcdc;
            padding: 8px 12px;
            font-size: 13px;
        }
        th {
            background-color: #f8f9fa;
            color: #333;
            font-weight: bold;
            text-align: right;
        }
        td:nth-child(2) {
            text-align: center;
            width: 90px;
        }
        td:nth-child(3) {
            text-align: right;
            width: 110px;
        }
        .btn-group {
            display: flex;
            gap: 10px;
            margin-top: 25px;
            max-width: 800px;
            margin-left: auto;
            margin-right: auto;
        }
        .action-btn {
            flex: 1;
            padding: 12px;
            font-size: 14px;
            font-weight: bold;
            border-radius: 6px;
            cursor: pointer;
            border: none;
            text-align: center;
            color: white;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .print-btn { background: #2c3e50; }
        .print-btn:hover { background: #1a252f; }
        .whatsapp-btn { background: #25d366; }
        .whatsapp-btn:hover { background: #1ebe57; }
        
        @media print {
            .btn-group { display: none; }
            body { background: white; padding: 0; }
            .invoice-container { border: none; box-shadow: none; padding: 0; max-width: 100%; }
        }
    </style>
</head>
<body>
    <div class="invoice-container" id="printableArea">
        <img src="/logo.png" class="watermark-logo" alt="Logo">

        <div class="header-title">کۆمپانییا ئورگانیک جویس - قایما داواکری</div>
        <div class="header-date">Date: {{ current_date }}</div>

        {% if user_note %}
        <div class="note-alert">
            تێبینی: {{ user_note }}
        </div>
        {% endif %}

        {% for cat_name, cat_items in categories.items() %}
        <div class="category-section">
            <div class="category-title">بەش: {{ cat_name }}</div>
            <table>
                <thead>
                    <tr>
                        <th>بابەت</th>
                        <th>بڕ</th>
                        <th>یەکە</th>
                    </tr>
                </thead>
                <tbody>
                    {% for item in cat_items %}
                    <tr>
                        <td>{{ item.item_name }}</td>
                        <td>{{ item.quantity }}</td>
                        <td>{{ item.unit }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% endfor %}
    </div>

    <div class="btn-group">
        <button class="action-btn print-btn" onclick="window.print()">🖨️ ڤێکرنا PDF / چاپکرن</button>
        <button class="action-btn whatsapp-btn" onclick="shareToWhatsApp()">💬 شێرکرن بۆ واتسئەپ</button>
    </div>

    <script>
        function shareToWhatsApp() {
            let text = "📋 *کۆمپانییا ئورگانیک جویس - قایما داواکری*\\n";
            text += "📅 دیرۆک: {{ current_date }}\\n";
            
            {% if user_note %}
            text += "📝 تێبینی: {{ user_note }}\\n";
            {% endif %}
            text += "----------------------------------\\n";

            {% for cat_name, cat_items in categories.items() %}
            text += "🔹 *بەش: {{ cat_name }}*\\n";
            {% for item in cat_items %}
            text += "▫️ " + "{{ item.item_name }}" + " : *" + "{{ item.quantity }}" + "* (" + "{{ item.unit }}" + ")\\n";
            {% endfor %}
            text += "\\n";
            {% endfor %}

            let encodedText = encodeURIComponent(text);
            window.open("https://wa.me/?text=" + encodedText, "_blank");
        }
    </script>
</body>
</html>
"""

SETTINGS_TEMPLATE = """
<!DOCTYPE html>
<html lang="ku" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>ڕێڤەبرنا بابەتان - سێتینگ</title>
    <style>
        body { font-family: system-ui, -apple-system, sans-serif; background-color: #f7f9f6; margin: 0; padding: 15px; color: #1a1a1a; direction: rtl; text-align: right; }
        .header { display: flex; justify-content: space-between; align-items: center; background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); margin-bottom: 20px; }
        .back-btn { background: #2e7d32; color: white; padding: 8px 15px; border-radius: 6px; text-decoration: none; font-weight: bold; font-size: 13px; }
        .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); margin-bottom: 20px; }
        h2, h3 { color: #1b5e20; margin-top: 0; }
        input, select { width: 100%; padding: 10px; margin: 8px 0 15px 0; border: 1px solid #ccc; border-radius: 6px; box-sizing: border-box; font-size: 14px; }
        button { background: #2e7d32; color: white; border: none; padding: 10px 15px; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 14px; width: 100%; }
        button:hover { background: #1b5e20; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { border-bottom: 1px solid #eee; padding: 10px; font-size: 13px; text-align: right; }
        th { background-color: #f5f5f5; color: #2e7d32; }
        .del-btn { background-color: #c62828; color: white; padding: 5px 10px; border-radius: 4px; text-decoration: none; font-weight: bold; font-size: 12px; display: inline-block; }
    </style>
</head>
<body>
    <div class="header">
        <h2 style="margin: 0;">⚙️ سێتینگ: زێدەکرن و ژێبرنا بابەتان</h2>
        <a href="/" class="back-btn">⬅️ ڤەڕەقین بۆ کاشێرێ</a>
    </div>

    <div class="card">
        <h3>➕ زێدەکرنا بابەتەکێ نوو</h3>
        <form method="POST" action="/add_item_setting">
            <label>بەش (Category):</label>
            <select name="category" required>
                <option value="فێقی">فێقی</option>
                <option value="مەعمەل">مەعمەل</option>
                <option value="مەغزەن">مەغزەن</option>
            </select>

            <label>ناڤێ بابەتی (نموونە: ڕەز):</label>
            <input type="text" name="item_name" placeholder="ناڤێ بابەتی بنڤیسە" required>

            <label>یەکە (Unit - نموونە: کیلو، دانە):</label>
            <input type="text" name="unit" placeholder="یەکە بنڤیسە" required>

            <button type="submit">تومارکرن و زێدەکرن</button>
        </form>
    </div>

    <div class="card">
        <h3>📋 لیستەیا هەمی بابەتێن هەی (بۆ ژێبرنێ)</h3>
        <table>
            <thead>
                <tr>
                    <th>بەش</th>
                    <th>ناڤێ بابەتی</th>
                    <th>یەکە</th>
                    <th>کردار</th>
                </tr>
            </thead>
            <tbody>
                {% for item in all_items_list %}
                <tr>
                    <td>{{ item[1] }}</td>
                    <td><b>{{ item[2] }}</b></td>
                    <td>{{ item[3] }}</td>
                    <td>
                        <a href="/delete_item_setting/{{ item[0] }}" class="del-btn" onclick="return confirm('تە مسۆگەر دڤێت ڤی بابەتی ژێببی؟')">ژێبرن 🗑️</a>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</body>
</html>
"""

def get_device_id():
    if 'device_id' not in session:
        session['device_id'] = os.urandom(8).hex()
    return session['device_id']

def get_note(device_id):
    conn = sqlite3.connect("clean_qayma.db")
    c = conn.cursor()
    c.execute("SELECT note_text FROM notes WHERE device_id = ?", (device_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else ""

def get_orders_list(device_id):
    conn = sqlite3.connect("clean_qayma.db")
    c = conn.cursor()
    c.execute("SELECT id, item_name, quantity, unit, category FROM orders WHERE device_id = ?", (device_id,))
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "item_name": r[1], "quantity": r[2], "unit": r[3], "category": r[4]} for r in rows]

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password != SHARED_PASSWORD:
            return render_template_string(LOGIN_TEMPLATE, error="ڕەمزی گشتی هەڵەیە!")
        session['authenticated'] = True
        get_device_id()
        return redirect(url_for('index'))
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/logout')
def logout():
    session.pop('authenticated', None)
    return redirect(url_for('login'))

@app.route('/')
def index():
    if not session.get('authenticated'):
        return redirect(url_for('login'))
    device_id = get_device_id()
    raw_orders = get_orders_list(device_id)
    tuple_orders = [(o["id"], o["item_name"], o["quantity"], o["unit"], o["category"]) for o in raw_orders]
    items_dict = get_all_items_dict()
    current_note = get_note(device_id)
    return render_template_string(HTML_TEMPLATE, all_items=items_dict, orders=tuple_orders, current_note=current_note)

@app.route('/save_note', methods=['POST'])
def save_note():
    if not session.get('authenticated'):
        return jsonify({"status": "unauthorized"}), 401
    device_id = get_device_id()
    note_text = request.form.get('note', '')
    conn = sqlite3.connect("clean_qayma.db")
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO notes (device_id, note_text) VALUES (?, ?)", (device_id, note_text))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

@app.route('/settings')
def settings_page():
    if not session.get('authenticated'):
        return redirect(url_for('login'))
    conn = sqlite3.connect("clean_qayma.db")
    c = conn.cursor()
    c.execute("SELECT id, category, item_name, unit FROM items ORDER BY category, id DESC")
    rows = c.fetchall()
    conn.close()
    return render_template_string(SETTINGS_TEMPLATE, all_items_list=rows)

@app.route('/add_item_setting', methods=['POST'])
def add_item_setting():
    if not session.get('authenticated'):
        return redirect(url_for('login'))
    category = request.form.get('category')
    item_name = request.form.get('item_name')
    unit = request.form.get('unit')
    
    if category and item_name and unit:
        conn = sqlite3.connect("clean_qayma.db")
        c = conn.cursor()
        c.execute("INSERT INTO items (category, item_name, unit) VALUES (?, ?, ?)", (category, item_name, unit))
        conn.commit()
        conn.close()
    return redirect(url_for('settings_page'))

@app.route('/delete_item_setting/<int:item_id>')
def delete_item_setting(item_id):
    if not session.get('authenticated'):
        return redirect(url_for('login'))
    conn = sqlite3.connect("clean_qayma.db")
    c = conn.cursor()
    c.execute("DELETE FROM items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('settings_page'))

@app.route('/logo.png')
def get_logo():
    return send_from_directory(os.getcwd(), 'logo.png')

@app.route('/quick_add_ajax', methods=['POST'])
def quick_add_ajax():
    if not session.get('authenticated'):
        return jsonify({"status": "unauthorized"}), 401
    device_id = get_device_id()
    conn = sqlite3.connect("clean_qayma.db")
    c = conn.cursor()
    c.execute("INSERT INTO orders (device_id, item_name, quantity, unit, category) VALUES (?, ?, ?, ?, ?)", 
              (device_id, request.form['item_name'], float(request.form['quantity']), request.form['unit'], request.form['category']))
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "orders": get_orders_list(device_id)})

@app.route('/clear_ajax')
def clear_ajax():
    if not session.get('authenticated'):
        return jsonify({"status": "unauthorized"}), 401
    device_id = get_device_id()
    conn = sqlite3.connect("clean_qayma.db")
    c = conn.cursor()
    c.execute("DELETE FROM orders WHERE device_id = ?", (device_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "orders": []})

@app.route('/invoice_view')
def invoice_view():
    if not session.get('authenticated'):
        return redirect(url_for('login'))
    
    device_id = get_device_id()
    orders = get_orders_list(device_id)
    user_note = get_note(device_id)
    
    categories = {}
    for item in orders:
        cat = item["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(item)
        
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M')
    return render_template_string(INVOICE_TEMPLATE, categories=categories, user_note=user_note, current_date=current_date)

if __name__ == "__main__":
    init_db()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))