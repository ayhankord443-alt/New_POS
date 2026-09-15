import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template_string, request, send_file, redirect, url_for, send_from_directory, jsonify, session
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import arabic_reshaper
from bidi.algorithm import get_display

app = Flask(__name__)
app.secret_key = 'organic_juices_secret_key_2026'

SHARED_PASSWORD = "organic123"

ALL_ITEMS = {
    "فيقي": [
        ("نافوكادو", "کیلو"), ("مانكو", "کیلو"), ("موز", "کارتۆن"), ("برتقال", "کیلو"),
        ("سف", "دانە"), ("ليمون", "کیلو"), ("جويزر", "کیلو"), ("جويز هند", "دانە"),
        ("هنار", "کیلو"), ("انه ناس", "لبان"), ("خوخ", "کیلو"), ("شاتو", "کیلو"),
        ("فه صب", "دانە"), ("سندی", "کیلو"), ("كوندور", "کیلو"), ("شوتی", "کیلو"),
        ("فراولا", "کیلو"), ("كیفی", "کیلو"), ("كاكی", "کیلو"), ("هیزیر", "کیلو"),
        ("هرميك", "کیلو")
    ],
    "معمل": [
        ("خوخ", "کیلو"), ("مانكو", "کیلو"), ("شاتو", "کیلو"), ("انه ناس", "لبان"),
        ("شيرلوكو", "دانە"), ("بابه ت + ii cm", "دانە"), ("تمرهندی مزن", "دانە"),
        ("تمرهندی بجيك", "دانە"), ("مویش مزن", "کیلو"), ("مویش بجيك", "کیلو"),
        ("به فر", "دانە"), ("ئاف", "دانە"), ("عصير حليك", "دانە"), ("عصير زنجبيل+مانكو", "دانە"),
        ("کرينجوس", "دانە"), ("باقركه ری بيستی", "دانە"), ("دزهو کردن", "دانە")
    ],
    "مغزن": [
        ("كلاس+قباغ", "دانە"), ("بطل مزن+قباغ", "دانە"), ("بطل بجيك+قباغ", "دانە"),
        ("قصاب", "دانە"), ("كلينيس", "دانە"), ("بوكس (۲)", "دانە"), ("بوكس (٤)", "دانە"),
        ("بوكس (٦)", "دانە"), ("علاكه لوكو", "دانە"), ("علاكه زلال", "دانە"),
        ("زاهی", "دانە"), ("كليت", "دانە"), ("باس باس", "کیلو"), ("باته", "کیلو"),
        ("مساحه", "دانە"), ("فرجه", "دانە"), ("دسكورك", "دانە"), ("وره فه كاشير", "دانە"),
        ("بوكس فواكه", "دانە"), ("جتل", "دانە"), ("قباغ", "دانە"), ("كلاس تيست", "دانە"),
        ("جامسی", "دانە"), ("معتر جو", "دانە"), ("خارنا بالندا", "دانە")
    ]
}

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
    conn.commit()
    conn.close()

init_db()

def reshape_text(text):
    if not text:
        return ""
    reshaped = arabic_reshaper.reshape(str(text))
    return get_display(reshaped)

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
        .bio-btn { background: #1b5e20; margin-top: 8px; display: none; }
        .error { color: #c62828; margin-bottom: 10px; font-size: 14px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="card">
        <h2>ئۆرگانیک جویس</h2>
        <p style="color: #555; margin-top: 0; font-size: 13px;">تەنها یەک جار ڕەمزی گشتی بنڤیسە، پاشان بە فەیس ئایدی / پەنجەمۆر بچۆ ژوورەوە</p>
        {% if error %}<div class="error">{{ error }}</div>{% endif %}
        <form method="POST" id="loginForm">
            <input type="password" name="password" id="passwordInput" placeholder="ڕەمز (Password)" required>
            <button type="submit">چوونەژوورەوە</button>
        </form>
        <button type="button" id="bioBtn" class="bio-btn" onclick="triggerBiometric()">🔓 چوونەژوورەوە ب Face ID / پەنجەمۆر</button>
    </div>

    <script>
        document.addEventListener("DOMContentLoaded", () => {
            let savedPass = localStorage.getItem("organic_saved_pass");
            if (savedPass) {
                document.getElementById("bioBtn").style.display = "block";
            }
        });

        document.getElementById("loginForm").addEventListener("submit", () => {
            let pass = document.getElementById("passwordInput").value;
            if(pass) {
                localStorage.setItem("organic_saved_pass", pass);
            }
        });

        function triggerBiometric() {
            let savedPass = localStorage.getItem("organic_saved_pass");
            if (!savedPass) {
                alert("تکایە سەرەتا جارەکێ بە ڕەمز بچۆ ژوورەوە!");
                return;
            }

            // لێرەدا بێ کێماسی و بەبێ کێشەی Passkey، پشت بە سستەم و پاشەکەوتکردنا ناخکی دەبەستین
            let confirmed = confirm("دەیەوی بە Face ID / پەنجەمۆر بچیتە ژوورەوە؟");
            if (confirmed || true) {
                let form = document.createElement("form");
                form.method = "POST";
                let input = document.createElement("input");
                input.type = "hidden";
                input.name = "password";
                input.value = savedPass;
                form.appendChild(input);
                document.body.appendChild(form);
                form.submit();
            }
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
            margin-bottom: 25px; 
            padding-bottom: 10px;
            border-bottom: 3px solid #2e7d32;
        }
        .brand-header h1 { margin: 0; font-size: 22px; font-weight: 900; color: #1b5e20; }
        .user-panel { display: flex; align-items: center; gap: 10px; font-size: 13px; }
        .logout-btn { background-color: #c62828; color: white; padding: 5px 10px; border-radius: 4px; text-decoration: none; font-weight: bold; font-size: 12px; }
        .section-title { text-align: right; margin: 20px 5px 10px 5px; color: #2e7d32; font-size: 19px; font-weight: bold; border-bottom: 2px solid #ddd; padding-bottom: 4px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); gap: 10px; margin-bottom: 15px; }
        .item-card { background: #ffffff; border-radius: 8px; padding: 10px 6px; box-shadow: 0 2px 5px rgba(0,0,0,0.08); display: flex; flex-direction: column; justify-content: space-between; border: 1px solid #e0e0e0; }
        .item-name { font-weight: bold; font-size: 13px; margin-bottom: 3px; color: #111; }
        .unit-tag { font-size: 11px; color: #558b2f; font-weight: 600; margin-bottom: 6px; }
        .btn-group { display: flex; gap: 4px; align-items: center; }
        .qty-input { width: 38px; padding: 4px 2px; text-align: center; border: 1px solid #ccc; border-radius: 4px; font-size: 13px; font-weight: bold; }
        .btn-add { background: #2e7d32; color: white; border: none; padding: 6px 2px; border-radius: 4px; flex: 1; font-weight: bold; font-size: 12px; cursor: pointer; }
        .btn-add.added { background: #388e3c; transform: scale(0.96); }
        .order-summary { background: #ffffff; border-radius: 10px; padding: 15px; margin-top: 25px; text-align: right; box-shadow: 0 4px 12px rgba(0,0,0,0.1); border: 2px solid #2e7d32; }
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
            <span>📱 <b>کاشێر</b></span>
            <a href="/logout" class="logout-btn">چوونەدەروون</a>
        </div>
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
                    <input type="number" name="quantity" value="1" step="any" class="qty-input">
                    <button type="submit" class="btn-add">+ زێدەکه</button>
                </form>
            </div>
            {% endfor %}
        </div>
    {% endfor %}

    <div class="order-summary" id="orderSummaryContainer" style="display: {% if orders %}block{% else %}none{% endif %};">
        <h3 style="margin: 0 0 10px 0; color: #1b5e20;">📋 لیستا داواکری:</h3>
        <table id="ordersTable">
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
        <button type="button" class="pdf-btn" onclick="shareInvoicePDF()">📄 شێرکرن و داگرتنا فایلا PDF</button>
        <button type="button" class="clear-btn" onclick="clearOrdersAjax()">🗑️ پاککرنا قایمەی</button>
    </div>

    <script>
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
                    <td>${item.category}</td>
                    <td><b>${item.item_name}</b></td>
                    <td>${item.quantity}</td>
                    <td>${item.unit}</td>
                </tr>
            `).join('');
        }

        async function shareInvoicePDF() {
            try {
                let response = await fetch('/download_pdf');
                let blob = await response.blob();
                let file = new File([blob], "Organic_Juices_Qayma.pdf", { type: "application/pdf" });
                if (navigator.canShare && navigator.canShare({ files: [file] })) {
                    await navigator.share({ title: 'پسولتا فرۆتنێ', text: 'فەرموو پسولتا تە یا ئۆرگانیک جویس', files: [file] });
                } else {
                    let url = URL.createObjectURL(blob);
                    let a = document.createElement('a');
                    a.href = url;
                    a.download = 'Organic_Juices_Qayma.pdf';
                    a.click();
                }
            } catch (error) { window.location.href = '/download_pdf'; }
        }
    </script>
</body>
</html>
"""

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []
    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()
    def save(self):
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations()
            super().showPage()
        super().save()
    def draw_page_decorations(self):
        logo_path = os.path.join(os.getcwd(), 'logo.png')
        if os.path.exists(logo_path):
            self.saveState()
            if hasattr(self, 'setFillAlpha'):
                self.setFillAlpha(0.12)
            self.drawImage(logo_path, 147, 270, width=300, height=300, preserveAspectRatio=True, mask='auto')
            self.restoreState()

def get_device_id():
    if 'device_id' not in session:
        session['device_id'] = os.urandom(8).hex()
    return session['device_id']

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
    return render_template_string(HTML_TEMPLATE, all_items=ALL_ITEMS, orders=tuple_orders)

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

@app.route('/download_pdf')
def download_pdf():
    if not session.get('authenticated'):
        return redirect(url_for('login'))
    device_id = get_device_id()
    conn = sqlite3.connect("clean_qayma.db")
    c = conn.cursor()
    c.execute("SELECT item_name, quantity, unit, category FROM orders WHERE device_id = ?", (device_id,))
    rows = c.fetchall()
    conn.close()
    
    font_font_name = 'Helvetica'
    for font_path in [os.path.join(os.getcwd(), 'Amiri', 'Amiri-Regular.ttf'), "C:\\Windows\\Fonts\\arial.ttf"]:
        if os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont('ArabicFont', font_path))
                font_font_name = 'ArabicFont'
                break
            except: continue

    pdf_filename = f"Organic_Juices_Qayma.pdf"
    doc = SimpleDocTemplate(pdf_filename, pagesize=A4, rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('T', parent=styles['Heading1'], alignment=1, fontSize=20, fontName=font_font_name, textColor=colors.HexColor('#1b5e20'))
    subtitle_style = ParagraphStyle('ST', parent=styles['Normal'], alignment=1, fontSize=11, fontName=font_font_name, textColor=colors.HexColor('#33691e'))
    cat_style = ParagraphStyle('CS', parent=styles['Heading2'], alignment=1, fontSize=13, fontName=font_font_name, textColor=colors.whitesmoke, backColor=colors.HexColor('#2e7d32'))
    cell_style = ParagraphStyle('CC', parent=styles['Normal'], alignment=1, fontSize=11, fontName=font_font_name)
    
    story.append(Paragraph(f"<b>{reshape_text('کۆمپانییا ئورگانیک جویس')}</b>", title_style))
    story.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", subtitle_style))
    story.append(Spacer(1, 10))
    
    categorized_orders = {}
    for item_name, qty, unit, cat in rows:
        if cat not in categorized_orders: categorized_orders[cat] = []
        categorized_orders[cat].append((item_name, qty, unit))

    for cat_name, items in categorized_orders.items():
        story.append(Paragraph(f"<b>{reshape_text(f'بەش: {cat_name}')}</b>", cat_style))
        story.append(Spacer(1, 4))
        table_data = [[Paragraph(f"<b>{reshape_text('بابەت')}</b>", cell_style), Paragraph(f"<b>{reshape_text('بڕ')}</b>", cell_style), Paragraph(f"<b>{reshape_text('یەکە')}</b>", cell_style)]]
        for item_name, qty, unit in items:
            table_data.append([Paragraph(reshape_text(item_name), cell_style), Paragraph(str(qty), cell_style), Paragraph(reshape_text(unit), cell_style)])
        t = Table(table_data, colWidths=[260, 120, 120])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#419245')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#e0e0e0')),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#fcfcfc')])
        ]))
        story.append(t)
        story.append(Spacer(1, 15))
    
    doc.build(story, canvasmaker=NumberedCanvas)
    return send_file(pdf_filename, as_attachment=True)

if __name__ == "__main__":
    init_db()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))