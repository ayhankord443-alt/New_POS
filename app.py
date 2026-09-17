import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template_string, request, send_file, redirect, url_for, send_from_directory, jsonify, session

app = Flask(__name__)
app.secret_key = 'organic_juices_secret_key_2026'

SHARED_PASSWORD = "organic123"

def init_db():
    try:
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
    except Exception as e:
        print("DB Error:", e)

init_db()

def get_all_items_dict():
    try:
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
    except:
        return {}

def reshape_text(text):
    if not text:
        return ""
    try:
        import arabic_reshaper
        from bidi.algorithm import get_display
        reshaped = arabic_reshaper.reshape(str(text))
        return get_display(reshaped)
    except:
        return str(text)

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
        .error { color: #c62828; margin-bottom: 10px; font-size: 14px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="card">
        <h2>ئۆرگانیک جویس</h2>
        <p style="color: #555; margin-top: 0; font-size: 13px;">ڕەمزی گشتی بنڤیسە دا بچی ژوورەوە</p>
        {% if error %}<div class="error">{{ error }}</div>{% endif %}
        <form method="POST">
            <input type="password" name="password" placeholder="ڕەمز (Password)" required>
            <button type="submit">چوونەژوورەوە</button>
        </form>
    </div>
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
            background-position: center 180px;
            background-size: 260px;
            opacity: 0.12;
            position: fixed;
            top: 0; left: 0; bottom: 0; right: 0;
            z-index: -1;
            pointer-events: none;
        }
        .brand-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; padding: 10px; border-bottom: 3px solid #2e7d32; background: rgba(255,255,255,0.9); border-radius: 8px; }
        .brand-header h1 { margin: 0; font-size: 18px; font-weight: 900; color: #1b5e20; }
        .user-panel { display: flex; align-items: center; gap: 8px; font-size: 13px; }
        .nav-link { background-color: #2e7d32; color: white; padding: 6px 10px; border-radius: 4px; text-decoration: none; font-weight: bold; font-size: 12px; }
        .logout-btn { background-color: #c62828; color: white; padding: 6px 10px; border-radius: 4px; text-decoration: none; font-weight: bold; font-size: 12px; }
        .note-box { background: rgba(249, 251, 231, 0.95); border: 1px solid #cddc39; border-radius: 8px; padding: 12px; margin-bottom: 20px; text-align: right; }
        .note-box textarea { width: 100%; height: 60px; padding: 8px; border: 1px solid #ccc; border-radius: 6px; font-size: 13px; box-sizing: border-box; }
        .note-save-btn { background: #558b2f; color: white; border: none; padding: 6px 12px; border-radius: 4px; font-weight: bold; font-size: 12px; cursor: pointer; margin-top: 6px; }
        .section-title { text-align: right; margin: 25px 5px 10px 5px; color: #2e7d32; font-size: 18px; font-weight: bold; border-bottom: 2px solid #2e7d32; padding: 4px 5px; background: rgba(255,255,255,0.8); border-radius: 4px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); gap: 10px; margin-bottom: 10px; }
        .item-card { background: rgba(255,255,255,0.95); border-radius: 8px; padding: 10px 6px; box-shadow: 0 2px 5px rgba(0,0,0,0.08); display: flex; flex-direction: column; justify-content: space-between; border: 1px solid #e0e0e0; }
        .item-name { font-weight: bold; font-size: 13px; margin-bottom: 2px; color: #111; }
        .unit-tag { font-size: 11px; color: #558b2f; font-weight: 600; margin-bottom: 6px; }
        .btn-group { display: flex; gap: 3px; align-items: center; justify-content: center; }
        .qty-btn { background: #e0e0e0; border: none; font-weight: bold; width: 26px; height: 28px; border-radius: 4px; cursor: pointer; font-size: 14px; color: #333; }
        .qty-input { width: 34px; padding: 4px 1px; text-align: center; border: 1px solid #ccc; border-radius: 4px; font-size: 13px; font-weight: bold; }
        .btn-add { background: #2e7d32; color: white; border: none; padding: 6px 4px; border-radius: 4px; font-weight: bold; font-size: 11px; cursor: pointer; flex: 1; }
        .order-summary { background: rgba(255,255,255,0.98); border-radius: 10px; padding: 15px; margin-top: 25px; text-align: right; box-shadow: 0 4px 12px rgba(0,0,0,0.1); border: 2px solid #2e7d32; }
        .pdf-btn { background: #1b5e20; color: white; width: 100%; padding: 12px; border: none; border-radius: 6px; font-weight: bold; font-size: 15px; margin-top: 10px; cursor: pointer; }
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
            <a href="/settings" class="nav-link">⚙️ سێتینگ</a>
            <a href="/logout" class="logout-btn">چوونەدەروون</a>
        </div>
    </div>

    <div class="note-box">
        <label style="font-weight: bold; color: #33691e; font-size: 13px; display: block; margin-bottom: 5px;">📝 تێبینی:</label>
        <textarea id="noteInput">{{ current_note }}</textarea>
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
        <h3 style="margin: 0 0 10px 0; color: #1b5e20;">📋 لیستا داواکری:</h3>
        <table>
            <thead>
                <tr>
                    <th>بەش</th>
                    <th>بابەت</th>
                    <th>بڕ</th>
                    <th>یەکە</th>
                </tr>
            </thead>
            <tbody id="ordersTableBody">
                {% for item in orders %}
                <tr>
                    <td>{{ item[4] }}</td>
                    <td><b>{{ item[1] }}</b></td>
                    <td>{{ item[2] }}</td>
                    <td>{{ item[3] }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        <button type="button" class="pdf-btn" onclick="shareInvoicePDF()">📄 داگرتنا PDF</button>
        <button type="button" class="clear-btn" onclick="clearOrdersAjax()">🗑️ پاککرنا قایمەی</button>
    </div>

    <script>
        function adjustQty(btn, amount) {
            let input = btn.parentElement.querySelector('.qty-input');
            let val = parseFloat(input.value) || 1;
            input.value = Math.max(0.1, val + amount);
        }
        async function saveNote() {
            let note = document.getElementById('noteInput').value;
            let fd = new FormData(); fd.append('note', note);
            await fetch('/save_note', { method: 'POST', body: fd });
            alert('تێبینی هاتە تومارکرن!');
        }
        async function quickAddAjax(e, form) {
            e.preventDefault();
            let res = await fetch('/quick_add_ajax', { method: 'POST', body: new FormData(form) });
            let data = await res.json();
            if(data.status === 'success') updateOrdersTable(data.orders);
        }
        async function clearOrdersAjax() {
            let res = await fetch('/clear_ajax');
            let data = await res.json();
            if(data.status === 'success') updateOrdersTable([]);
        }
        function updateOrdersTable(orders) {
            let container = document.getElementById('orderSummaryContainer');
            let tbody = document.getElementById('ordersTableBody');
            if (orders.length === 0) { container.style.display = 'none'; tbody.innerHTML = ''; return; }
            container.style.display = 'block';
            tbody.innerHTML = orders.map(i => `<tr><td>${i.category}</td><td><b>${i.item_name}</b></td><td>${i.quantity}</td><td>${i.unit}</td></tr>`).join('');
        }
        async function shareInvoicePDF() {
            window.location.href = '/download_pdf';
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
    <title>سێتینگ</title>
    <style>
        body { font-family: system-ui; background: #f7f9f6; padding: 15px; direction: rtl; text-align: right; }
        .header { display: flex; justify-content: space-between; background: white; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
        .card { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        input, select { width: 100%; padding: 10px; margin: 8px 0 15px 0; border: 1px solid #ccc; border-radius: 6px; }
        button { background: #2e7d32; color: white; border: none; padding: 10px; border-radius: 6px; font-weight: bold; width: 100%; cursor: pointer; }
        table { width: 100%; border-collapse: collapse; }
        th, td { border-bottom: 1px solid #eee; padding: 10px; text-align: right; }
        th { background: #f5f5f5; color: #2e7d32; }
        .del-btn { background: #c62828; color: white; padding: 5px 10px; border-radius: 4px; text-decoration: none; font-size: 12px; }
    </style>
</head>
<body>
    <div class="header">
        <h2 style="margin:0; color:#1b5e20;">⚙️ سێتینگ</h2>
        <a href="/" style="background:#2e7d32; color:white; padding:8px 15px; border-radius:6px; text-decoration:none;">⬅️ ڤەڕەقین</a>
    </div>
    <div class="card">
        <h3>➕ زێدەکرنا بابەتەکێ نوو</h3>
        <form method="POST" action="/add_item_setting">
            <label>بەش:</label>
            <select name="category"><option value="فێقی">فێقی</option><option value="مەعمەل">مەعمەل</option><option value="مەغزەن">مەغزەن</option></select>
            <label>ناڤێ بابەتی:</label><input type="text" name="item_name" required>
            <label>یەکە:</label><input type="text" name="unit" required>
            <button type="submit">تومارکرن</button>
        </form>
    </div>
    <div class="card">
        <h3>📋 لیستەیا بابەتان</h3>
        <table>
            <tr><th>بەش</th><th>ناڤ</th><th>یەکە</th><th>کردار</th></tr>
            {% for item in all_items_list %}
            <tr><td>{{ item[1] }}</td><td><b>{{ item[2] }}</b></td><td>{{ item[3] }}</td><td><a href="/delete_item_setting/{{ item[0] }}" class="del-btn">ژێبرن</a></td></tr>
            {% endfor %}
        </table>
    </div>
</body>
</html>
"""

class NumberedCanvas(canvas.Canvas if 'canvas' in globals() else object):
    pass

# Safe Canvas for Watermark Logo in PDF
from reportlab.pdfgen import canvas as rl_canvas
class WatermarkCanvas(rl_canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []
    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()
    def save(self):
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_watermark()
            super().showPage()
        super().save()
    def draw_watermark(self):
        try:
            logo_path = os.path.join(os.getcwd(), 'logo.png')
            if os.path.exists(logo_path):
                self.saveState()
                if hasattr(self, 'setFillAlpha'):
                    self.setFillAlpha(0.15)
                self.drawImage(logo_path, 147, 270, width=300, height=300, preserveAspectRatio=True, mask='auto')
                self.restoreState()
        except:
            pass

def get_device_id():
    if 'device_id' not in session:
        session['device_id'] = os.urandom(8).hex()
    return session['device_id']

def get_note(device_id):
    try:
        conn = sqlite3.connect("clean_qayma.db")
        c = conn.cursor()
        c.execute("SELECT note_text FROM notes WHERE device_id = ?", (device_id,))
        row = c.fetchone()
        conn.close()
        return row[0] if row else ""
    except: return ""

def get_orders_list(device_id):
    try:
        conn = sqlite3.connect("clean_qayma.db")
        c = conn.cursor()
        c.execute("SELECT id, item_name, quantity, unit, category FROM orders WHERE device_id = ?", (device_id,))
        rows = c.fetchall()
        conn.close()
        return [{"id": r[0], "item_name": r[1], "quantity": r[2], "unit": r[3], "category": r[4]} for r in rows]
    except: return []

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form.get('password') != SHARED_PASSWORD:
            error = "ڕەمز هەڵەیە!"
        else:
            session['authenticated'] = True
            get_device_id()
            return redirect(url_for('index'))
    return render_template_string(LOGIN_TEMPLATE, error=error)

@app.route('/logout')
def logout():
    session.pop('authenticated', None)
    return redirect(url_for('login'))

@app.route('/')
def index():
    if not session.get('authenticated'): return redirect(url_for('login'))
    device_id = get_device_id()
    raw_orders = get_orders_list(device_id)
    tuple_orders = [(o["id"], o["item_name"], o["quantity"], o["unit"], o["category"]) for o in raw_orders]
    return render_template_string(HTML_TEMPLATE, all_items=get_all_items_dict(), orders=tuple_orders, current_note=get_note(device_id))

@app.route('/save_note', methods=['POST'])
def save_note():
    if not session.get('authenticated'): return jsonify({"status": "unauthorized"}), 401
    try:
        conn = sqlite3.connect("clean_qayma.db")
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO notes (device_id, note_text) VALUES (?, ?)", (get_device_id(), request.form.get('note', '')))
        conn.commit(); conn.close()
        return jsonify({"status": "success"})
    except Exception as e: return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/settings')
def settings_page():
    if not session.get('authenticated'): return redirect(url_for('login'))
    try:
        conn = sqlite3.connect("clean_qayma.db")
        c = conn.cursor()
        c.execute("SELECT id, category, item_name, unit FROM items ORDER BY category, id DESC")
        rows = c.fetchall(); conn.close()
    except: rows = []
    return render_template_string(SETTINGS_TEMPLATE, all_items_list=rows)

@app.route('/add_item_setting', methods=['POST'])
def add_item_setting():
    if not session.get('authenticated'): return redirect(url_for('login'))
    try:
        conn = sqlite3.connect("clean_qayma.db")
        c = conn.cursor()
        c.execute("INSERT INTO items (category, item_name, unit) VALUES (?, ?, ?)", 
                  (request.form.get('category'), request.form.get('item_name'), request.form.get('unit')))
        conn.commit(); conn.close()
    except: pass
    return redirect(url_for('settings_page'))

@app.route('/delete_item_setting/<int:item_id>')
def delete_item_setting(item_id):
    if not session.get('authenticated'): return redirect(url_for('login'))
    try:
        conn = sqlite3.connect("clean_qayma.db")
        c = conn.cursor()
        c.execute("DELETE FROM items WHERE id = ?", (item_id,))
        conn.commit(); conn.close()
    except: pass
    return redirect(url_for('settings_page'))

@app.route('/logo.png')
def get_logo():
    try:
        return send_from_directory(os.getcwd(), 'logo.png')
    except:
        return "", 404

@app.route('/quick_add_ajax', methods=['POST'])
def quick_add_ajax():
    if not session.get('authenticated'): return jsonify({"status": "unauthorized"}}, 401
    device_id = get_device_id()
    try:
        conn = sqlite3.connect("clean_qayma.db")
        c = conn.cursor()
        c.execute("INSERT INTO orders (device_id, item_name, quantity, unit, category) VALUES (?, ?, ?, ?, ?)", 
                  (device_id, request.form['item_name'], float(request.form['quantity']), request.form['unit'], request.form['category']))
        conn.commit(); conn.close()
        return jsonify({"status": "success", "orders": get_orders_list(device_id)})
    except Exception as e: return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/clear_ajax')
def clear_ajax():
    if not session.get('authenticated'): return jsonify({"status": "unauthorized"}}, 401
    device_id = get_device_id()
    try:
        conn = sqlite3.connect("clean_qayma.db")
        c = conn.cursor()
        c.execute("DELETE FROM orders WHERE device_id = ?", (device_id,))
        conn.commit(); conn.close()
        return jsonify({"status": "success", "orders": []})
    except Exception as e: return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/download_pdf')
def download_pdf():
    if not session.get('authenticated'): return redirect(url_for('login'))
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        
        device_id = get_device_id()
        items_dict = get_all_items_dict()
        user_note = get_note(device_id)
        
        font_name = 'Helvetica'
        for font_path in [os.path.join(os.getcwd(), 'Amiri', 'Amiri-Regular.ttf'), "C:\\Windows\\Fonts\\arial.ttf"]:
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont('ArabicFont', font_path))
                    font_name = 'ArabicFont'
                    break
                except: pass

        pdf_filename = "Organic_Juices_Qayma.pdf"
        doc = SimpleDocTemplate(pdf_filename, pagesize=A4, rightMargin=15, leftMargin=15, topMargin=20, bottomMargin=20)
        story = []
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle('T', parent=styles['Heading1'], alignment=1, fontSize=18, fontName=font_name, textColor=colors.HexColor('#1b5e20'))
        subtitle_style = ParagraphStyle('ST', parent=styles['Normal'], alignment=1, fontSize=10, fontName=font_name, textColor=colors.HexColor('#33691e'))
        note_style = ParagraphStyle('NS', parent=styles['Normal'], alignment=2, fontSize=10, fontName=font_name, textColor=colors.HexColor('#b71c1c'))
        header_cell_style = ParagraphStyle('HCS', parent=styles['Normal'], alignment=1, fontSize=10, fontName=font_name, textColor=colors.HexColor('#1b5e20'))
        
        story.append(Paragraph(f"<b>{reshape_text('کۆمپانییا ئورگانیک جویس')}</b>", title_style))
        story.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", subtitle_style))
        
        if user_note:
            story.append(Spacer(1, 6))
            story.append(Paragraph(f"<b>{reshape_text('تێبینی: ')}{reshape_text(user_note)}</b>", note_style))
            
        story.append(Spacer(1, 10))
        
        categories = ["فێقی", "مەعمەل", "مەغزەن"]
        table_headers = [Paragraph(f"<b>{reshape_text(cat)}</b>", header_cell_style) for cat in categories]
        max_rows = max([len(items_dict.get(cat, [])) for cat in categories]) if categories else 0
        table_data = [table_headers]
        
        for i in range(max_rows):
            row = []
            for cat in categories:
                items_in_cat = items_dict.get(cat, [])
                if i < len(items_in_cat):
                    item_name, unit = items_in_cat[i]
                    name_para = Paragraph(f"<b>{reshape_text(item_name)}</b>", ParagraphStyle('NP', fontName=font_name, fontSize=9, alignment=2))
                    unit_para = Paragraph(f"<font color='#555'>({reshape_text(unit)}) ✓</font>", ParagraphStyle('UP', fontName=font_name, fontSize=8, alignment=0))
                    
                    cell_table = Table([[name_para, unit_para]], colWidths=[130, 50])
                    cell_table.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('LEFTPADDING', (0,0), (-1,-1), 0), ('RIGHTPADDING', (0,0), (-1,-1), 0), ('BOTTOMPADDING', (0,0), (-1,-1), 0), ('TOPPADDING', (0,0), (-1,-1), 0)]))
                    row.append(cell_table)
                else:
                    row.append(Paragraph("", header_cell_style))
            table_data.append(row)
            
        col_width = 560 / 3
        t = Table(table_data, colWidths=[col_width, col_width, col_width])
        t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f5f5f5')), ('ALIGN', (0,0), (-1,-1), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'TOP'), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cccccc')), ('BOTTOMPADDING', (0,0), (-1,-1), 3), ('TOPPADDING', (0,0), (-1,-1), 3), ('LEFTPADDING', (0,0), (-1,-1), 4), ('RIGHTPADDING', (0,0), (-1,-1), 4)]))
        
        story.append(t)
        doc.build(story, canvasmaker=WatermarkCanvas)
        return send_file(pdf_filename, as_attachment=True)
    except Exception as e:
        return f"PDF Error: {str(e)}", 500

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)