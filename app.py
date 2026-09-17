import sqlite3
from flask import Flask, render_template_string, request, redirect, url_for, session, jsonify, Response

app = Flask(__name__)
app.secret_key = "organic_juices_secret_key"

# =========================================================
# DATABASE SETUP
# =========================================================

def get_db():
    conn = sqlite3.connect("organic_juices.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            item_name TEXT,
            unit TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT,
            item_name TEXT,
            quantity REAL,
            unit TEXT,
            category TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            device_id TEXT PRIMARY KEY,
            note TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# =========================================================
# HELPER FUNCTIONS
# =========================================================

def logged_in():
    return session.get("logged_in", False)

def get_device_id():
    if "device_id" not in session:
        import uuid
        session["device_id"] = str(uuid.uuid4())
    return session["device_id"]

def get_orders(device_id):
    conn = get_db()
    orders = conn.execute(
        "SELECT * FROM orders WHERE device_id = ?", (device_id,)
    ).fetchall()
    conn.close()
    return [dict(o) for o in orders]

def get_note(device_id):
    conn = get_db()
    row = conn.execute(
        "SELECT note FROM notes WHERE device_id = ?", (device_id,)
    ).fetchone()
    conn.close()
    return row["note"] if row else ""

def get_all_items():
    conn = get_db()
    items = conn.execute("SELECT * FROM items").fetchall()
    conn.close()
    return [dict(i) for i in items]


# =========================================================
# TEMPLATES (HTML / CSS / JS)
# =========================================================

LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="ku" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>چوونەژوورەوە - Organic Juices</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Tahoma, sans-serif; background: #f0f2f5; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .login-card { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); width: 100%; max-width: 400px; text-align: center; }
        h2 { color: #2e7d32; margin-bottom: 20px; }
        input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ccc; border-radius: 6px; box-sizing: border-box; }
        button { background: #2e7d32; color: white; border: none; padding: 12px; width: 100%; border-radius: 6px; cursor: pointer; font-size: 16px; font-weight: bold; }
        button:hover { background: #1b5e20; }
        .error { color: #d32f2f; margin-bottom: 10px; font-size: 14px; }
    </style>
</head>
<body>
    <div class="login-card">
        <h2>Organic Juices POS</h2>
        {% if error %}<div class="error">{{ error }}</div>{% endif %}
        <form method="POST">
            <input type="password" name="password" placeholder="وشەی تێپەڕ (Password)" required autofocus>
            <button type="submit">چوونەژوورەوە</button>
        </form>
    </div>
</body>
</html>
"""

POS_TEMPLATE = """
<!DOCTYPE html>
<html lang="ku" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>Organic Juices - سیستەمی کاشێر</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { box-sizing: border-box; }
        body { font-family: Tahoma, sans-serif; margin: 0; background: #f8f9fa; display: flex; height: 100vh; overflow: hidden; }
        .sidebar { width: 250px; background: #1e293b; color: white; display: flex; flex-direction: column; }
        .sidebar h1 { font-size: 18px; padding: 20px; margin: 0; background: #0f172a; text-align: center; }
        .sidebar a { color: #cbd5e1; text-decoration: none; padding: 15px 20px; display: block; border-bottom: 1px solid #334155; transition: 0.2s; }
        .sidebar a:hover { background: #334155; color: white; }
        
        .main-content { flex: 1; display: flex; height: 100vh; overflow: hidden; }
        .left-panel { flex: 2; padding: 20px; overflow-y: auto; border-left: 1px solid #e2e8f0; display: flex; flex-direction: column; }
        .right-panel { flex: 1; background: white; padding: 20px; display: flex; flex-direction: column; box-shadow: -2px 0 10px rgba(0,0,0,0.05); }

        .categories-bar { display: flex; gap: 10px; margin-bottom: 20px; overflow-x: auto; padding-bottom: 5px; }
        .cat-btn { background: #e2e8f0; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-weight: bold; white-space: nowrap; transition: 0.2s; }
        .cat-btn.active, .cat-btn:hover { background: #2563eb; color: white; }

        .items-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 15px; }
        .item-card { background: white; border: 1px solid #e2e8f0; border-radius: 10px; padding: 15px; text-align: center; cursor: pointer; box-shadow: 0 2px 5px rgba(0,0,0,0.02); transition: 0.2s; }
        .item-card:hover { transform: translateY(-3px); box-shadow: 0 4px 10px rgba(0,0,0,0.08); border-color: #2563eb; }
        .item-card h3 { margin: 0 0 10px 0; font-size: 16px; color: #1e293b; }
        .item-card span { font-size: 12px; color: #64748b; background: #f1f5f9; padding: 3px 8px; border-radius: 4px; }

        .order-header { font-size: 18px; font-weight: bold; margin-bottom: 15px; border-bottom: 2px solid #f1f5f9; padding-bottom: 10px; color: #1e293b; }
        .order-list { flex: 1; overflow-y: auto; margin-bottom: 15px; }
        .order-item { display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #f1f5f9; }
        .order-item-info { flex: 1; }
        .order-item-title { font-weight: bold; color: #1e293b; font-size: 14px; }
        .order-item-qty { font-size: 12px; color: #64748b; margin-top: 3px; }
        .delete-btn { background: #fee2e2; color: #dc2626; border: none; padding: 5px 10px; border-radius: 5px; cursor: pointer; font-size: 12px; }
        .delete-btn:hover { background: #fecaca; }

        .actions-panel { display: flex; flex-direction: column; gap: 10px; }
        .action-btn { padding: 12px; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 14px; text-align: center; text-decoration: none; }
        .btn-print { background: #10b981; color: white; }
        .btn-print:hover { background: #059669; }
        .btn-clear { background: #ef4444; color: white; }
        .btn-clear:hover { background: #dc2626; }
    </style>
</head>
<body>

    <div class="sidebar">
        <h1>Organic Juices</h1>
        <a href="{{ url_for('index') }}">📦 کاشێر (POS)</a>
        <a href="{{ url_for('settings') }}">⚙️ ڕێکخستنەکان</a>
        <a href="{{ url_for('logout') }}">🚪 چوونەدەرەوە</a>
    </div>

    <div class="main-content">
        <div class="left-panel">
            <div class="categories-bar" id="categoriesBar">
                <button class="cat-btn active" onclick="filterCategory('all', this)">هەمووی</button>
                {% for cat in categories %}
                <button class="cat-btn" onclick="filterCategory('{{ cat }}', this)">{{ cat }}</button>
                {% endfor %}
            </div>

            <div class="items-grid" id="itemsGrid">
                {% for item in items %}
                <div class="item-card" data-category="{{ item.category }}" onclick="addOrder('{{ item.item_name }}', '{{ item.unit }}', '{{ item.category }}')">
                    <h3>{{ item.item_name }}</h3>
                    <span>{{ item.unit }}</span>
                </div>
                {% endfor %}
            </div>
        </div>

        <div class="right-panel">
            <div class="order-header">لیستا داواکارییان</div>
            <div class="order-list" id="orderList">
                {% for o in orders %}
                <div class="order-item" id="order-row-{{ o.id }}">
                    <div class="order-item-info">
                        <div class="order-item-title">{{ o.item_name }}</div>
                        <div class="order-item-qty">{{ o.quantity }} {{ o.unit }}</div>
                    </div>
                    <button class="delete-btn" onclick="deleteOrder({{ o.id }})">سڕینەوە</button>
                </div>
                {% endfor %}
            </div>

            <div class="actions-panel">
                <a href="{{ url_for('download_pdf') }}" class="action-btn btn-print">🖨️ چاپکردن / دابەزاندنی قایمە (PDF)</a>
                <button class="action-btn btn-clear" onclick="clearOrders()">🗑️ پاقژکردنەوەی هەمووی</button>
            </div>
        </div>
    </div>

    <script>
        function filterCategory(category, btn) {
            document.querySelectorAll('.cat-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            document.querySelectorAll('.item-card').forEach(card => {
                if (category === 'all' || card.getAttribute('data-category') === category) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        }

        function addOrder(itemName, unit, category) {
            let qty = prompt(`بڕی بۆ (${itemName}):`, "1");
            if (qty === null || qty.trim() === "") return;
            qty = parseFloat(qty);
            if (isNaN(qty) || qty <= 0) {
                alert("تکایە بڕێکی دروست بنووسە!");
                return;
            }

            fetch('/add_order', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ item_name: itemName, quantity: qty, unit: unit, category: category })
            })
            .then(res => res.json())
            .then(data => {
                if (data.status === 'success') {
                    updateOrderList(data.orders);
                }
            });
        }

        function deleteOrder(orderId) {
            fetch(`/delete_order/${orderId}`, { method: 'POST' })
            .then(res => res.json())
            .then(data => {
                if (data.status === 'success') {
                    updateOrderList(data.orders);
                }
            });
        }

        function clearOrders() {
            if (!confirm("دڵنیای لە پاقژکردنەوەی هەموو داواکارییەکان؟")) return;
            fetch('/clear_ajax')
            .then(res => res.json())
            .then(data => {
                if (data.status === 'success') {
                    updateOrderList([]);
                }
            });
        }

        function updateOrderList(orders) {
            const listEl = document.getElementById('orderList');
            listEl.innerHTML = '';
            orders.forEach(o => {
                listEl.innerHTML += `
                    <div class="order-item" id="order-row-${o.id}">
                        <div class="order-item-info">
                            <div class="order-item-title">${o.item_name}</div>
                            <div class="order-item-qty">${o.quantity} ${o.unit}</div>
                        </div>
                        <button class="delete-btn" onclick="deleteOrder(${o.id})">سڕینەوە</button>
                    </div>
                `;
            });
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
    <title>ڕێکخستنەکان - Organic Juices</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Tahoma, sans-serif; margin: 0; background: #f8f9fa; display: flex; height: 100vh; overflow: hidden; }
        .sidebar { width: 250px; background: #1e293b; color: white; display: flex; flex-direction: column; }
        .sidebar h1 { font-size: 18px; padding: 20px; margin: 0; background: #0f172a; text-align: center; }
        .sidebar a { color: #cbd5e1; text-decoration: none; padding: 15px 20px; display: block; border-bottom: 1px solid #334155; }
        .sidebar a:hover { background: #334155; color: white; }
        
        .content { flex: 1; padding: 30px; overflow-y: auto; }
        h2 { color: #1e293b; margin-top: 0; }
        .card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); margin-bottom: 20px; }
        form input, form select { padding: 10px; margin-right: 10px; border: 1px solid #ccc; border-radius: 5px; }
        form button { padding: 10px 20px; background: #2563eb; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; }
        form button:hover { background: #1d4ed8; }
        
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { padding: 12px; border-bottom: 1px solid #e2e8f0; text-align: right; }
        th { background: #f1f5f9; color: #1e293b; }
        .btn-del { color: #dc2626; text-decoration: none; font-weight: bold; }
        .btn-del:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="sidebar">
        <h1>Organic Juices</h1>
        <a href="{{ url_for('index') }}">📦 کاشێر (POS)</a>
        <a href="{{ url_for('settings') }}">⚙️ ڕێکخستنەکان</a>
        <a href="{{ url_for('logout') }}">🚪 چوونەدەرەوە</a>
    </div>

    <div class="content">
        <h2>بەڕێوەبردنی کاڵاکان</h2>
        
        <div class="card">
            <h3>زیادکردنی بابەتی نوێ</h3>
            <form method="POST" action="{{ url_for('add_item_setting') }}">
                <select name="category" required>
                    <option value="">-- پۆل هەڵبژێرە --</option>
                    {% for cat in categories %}
                    <option value="{{ cat }}">{{ cat }}</option>
                    {% endfor %}
                </select>
                <input type="text" name="item_name" placeholder="ناوی بابەت" required>
                <input type="text" name="unit" placeholder="یوونیت (پەرداخ، شوشە...)" required>
                <button type="submit">زیادکردن</button>
            </form>
        </div>

        <div class="card">
            <h3>لیستی هەموو بابەتەکان</h3>
            <table>
                <tr>
                    <th>پۆل</th>
                    <th>ناوی بابەت</th>
                    <th>یوونیت</th>
                    <th>کردار</th>
                </tr>
                {% for item in items %}
                <tr>
                    <td>{{ item.category }}</td>
                    <td>{{ item.item_name }}</td>
                    <td>{{ item.unit }}</td>
                    <td><a href="{{ url_for('delete_item_setting', item_id=item.id) }}" class="btn-del" onclick="return confirm('دڵنیای لە سڕینەوەی ئەم بابەتە؟')">سڕینەوە</a></td>
                </tr>
                {% endfor %}
            </table>
        </div>
    </div>
</body>
</html>
"""

EDIT_TEMPLATE = """
<!DOCTYPE html>
<html lang="ku" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>دەستکاریکردنی بابەت</title>
    <style>
        body { font-family: Tahoma, sans-serif; background: #f8f9fa; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .card { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); width: 100%; max-width: 400px; }
        input, select { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ccc; border-radius: 5px; box-sizing: border-box; }
        button { background: #2563eb; color: white; border: none; padding: 10px; width: 100%; border-radius: 5px; cursor: pointer; font-weight: bold; }
    </style>
</head>
<body>
    <div class="card">
        <h3>دەستکاریکردنی بابەت</h3>
        <form method="POST">
            <select name="category" required>
                {% for cat in categories %}
                <option value="{{ cat }}" {% if cat == item.category %}selected{% endif %}>{{ cat }}</option>
                {% endfor %}
            </select>
            <input type="text" name="item_name" value="{{ item.item_name }}" required>
            <input type="text" name="unit" value="{{ item.unit }}" required>
            <button type="submit">پاشەکەوتکردن</button>
        </form>
    </div>
</body>
</html>
"""

# =========================================================
# ROUTES
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        password = request.form.get("password")
        if password == "1234":
            session["logged_in"] = True
            return redirect(url_for("index"))
        else:
            error = "وشەی تێپەڕ هەڵەیە!"
    return render_template_string(LOGIN_TEMPLATE, error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/")
def index():
    if not logged_in():
        return redirect(url_for("login"))

    device_id = get_device_id()
    conn = get_db()
    cats = conn.execute("SELECT name FROM categories").fetchall()
    
    if not cats:
        default_cats = ["میوە", "شەربەت", "ساردی", "شیرینەمەنی"]
        for c in default_cats:
            conn.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (c,))
        conn.commit()
        cats = conn.execute("SELECT name FROM categories").fetchall()

    conn.close()

    return render_template_string(
        POS_TEMPLATE,
        categories=[c["name"] for c in cats],
        items=get_all_items(),
        orders=get_orders(device_id)
    )

@app.route("/add_order", methods=["POST"])
def add_order():
    if not logged_in():
        return jsonify({"status": "unauthorized"}), 401

    try:
        data = request.get_json()
        item_name = data.get("item_name")
        quantity = data.get("quantity")
        unit = data.get("unit")
        category = data.get("category")

        device_id = get_device_id()

        conn = get_db()
        conn.execute("""
            INSERT INTO orders
            (device_id, item_name, quantity, unit, category)
            VALUES (?, ?, ?, ?, ?)
        """, (device_id, item_name, quantity, unit, category))
        
        conn.commit()
        conn.close()

        return jsonify({
            "status": "success",
            "orders": get_orders(device_id)
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400


# =========================================================
# DELETE ORDER
# =========================================================

@app.route("/delete_order/<int:order_id>", methods=["POST"])
def delete_order(order_id):
    if not logged_in():
        return jsonify({"status": "unauthorized"}), 401

    device_id = get_device_id()
    conn = get_db()
    
    conn.execute("""
        DELETE FROM orders
        WHERE id = ? AND device_id = ?
    """, (order_id, device_id))
    
    conn.commit()
    conn.close()

    return jsonify({
        "status": "success",
        "orders": get_orders(device_id)
    })


# =========================================================
# CLEAR ORDERS
# =========================================================

@app.route("/clear_ajax")
def clear_ajax():
    if not logged_in():
        return jsonify({"status": "unauthorized"}), 401

    device_id = get_device_id()
    conn = get_db()
    
    conn.execute("""
        DELETE FROM orders
        WHERE device_id = ?
    """, (device_id,))
    
    conn.commit()
    conn.close()

    return jsonify({"status": "success"})


# =========================================================
# SETTINGS ACTIONS
# =========================================================

@app.route("/settings")
def settings():
    if not logged_in():
        return redirect(url_for("login"))

    conn = get_db()
    cats = conn.execute("SELECT name FROM categories").fetchall()
    conn.close()

    return render_template_string(
        SETTINGS_TEMPLATE,
        categories=[c["name"] for c in cats],
        items=get_all_items()
    )


@app.route("/add_item_setting", methods=["POST"])
def add_item_setting():
    if not logged_in():
        return redirect(url_for("login"))

    category = request.form.get("category", "").strip()
    item_name = request.form.get("item_name", "").strip()
    unit = request.form.get("unit", "").strip()

    if category and item_name and unit:
        conn = get_db()
        conn.execute("""
            INSERT INTO items (category, item_name, unit)
            VALUES (?, ?, ?)
        """, (category, item_name, unit))
        conn.commit()
        conn.close()

    return redirect(url_for("settings"))


@app.route("/edit_item/<int:item_id>", methods=["GET", "POST"])
def edit_item(item_id):
    if not logged_in():
        return redirect(url_for("login"))

    conn = get_db()

    if request.method == "POST":
        category = request.form.get("category", "").strip()
        item_name = request.form.get("item_name", "").strip()
        unit = request.form.get("unit", "").strip()

        conn.execute("""
            UPDATE items
            SET category = ?, item_name = ?, unit = ?
            WHERE id = ?
        """, (category, item_name, unit, item_id))
        conn.commit()
        conn.close()

        return redirect(url_for("settings"))

    item = conn.execute(
        "SELECT * FROM items WHERE id = ?", (item_id,)
    ).fetchone()
    cats = conn.execute("SELECT name FROM categories").fetchall()
    conn.close()

    if not item:
        return "بابەت نەدۆزراوەتەوە", 404

    return render_template_string(
        EDIT_TEMPLATE,
        item=item,
        categories=[c["name"] for c in cats]
    )


@app.route("/delete_item_setting/<int:item_id>")
def delete_item_setting(item_id):
    if not logged_in():
        return redirect(url_for("login"))

    conn = get_db()
    conn.execute("DELETE FROM items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

    return redirect(url_for("settings"))


# =========================================================
# PDF EXPORT (HTML to PDF layout with Arabic/Kurdish support)
# =========================================================

@app.route("/download_pdf")
def download_pdf():
    if not logged_in():
        return redirect(url_for("login"))

    device_id = get_device_id()
    orders = get_orders(device_id)
    note = get_note(device_id)

    # لێرەدا دەستکاری ڕووکاری چاپکردن کرا بۆ ئەوەی ڕیزبەندی (ژمارە) تێدا بێت، 
    # لۆگۆی کۆمپانیا لە سەرەوە دەرکەوێت، و کێشەی تێکستی کوردی (پێچەوانەبوون) بە CSS ڕاستکراوەتەوە.
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ku" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>Organic Juices - قایمە</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;700&display=swap');
            body {{
                font-family: 'Vazirmatn', Tahoma, sans-serif;
                direction: rtl;
                text-align: right;
                padding: 20px;
                color: #333;
                background: #fff;
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
                border-bottom: 2px solid #2e7d32;
                padding-bottom: 15px;
            }}
            .logo-placeholder {{
                font-size: 24px;
                font-weight: bold;
                color: #2e7d32;
                margin-bottom: 5px;
            }}
            .sub-title {{
                font-size: 14px;
                color: #666;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 10px;
                text-align: center;
                font-size: 14px;
            }}
            th {{
                background-color: #2e7d32;
                color: white;
            }}
            tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
            .footer-note {{
                margin-top: 20px;
                font-size: 13px;
                color: #555;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="logo-placeholder">🌿 Organic Juices</div>
            <div class="sub-title">سیستەمی داواکاری و قایمە</div>
        </div>

        <table>
            <thead>
                <tr>
                    <th style="width: 10%;">ژمارە</th>
                    <th style="width: 30%;">ناوی بابەت</th>
                    <th style="width: 20%;">بڕ</th>
                    <th style="width: 20%;">یوونیت</th>
                    <th style="width: 20%;">پۆل</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for index, o in enumerate(orders, start=1):
        html_content += f"""
                <tr>
                    <td>{index}</td>
                    <td>{o['item_name']}</td>
                    <td>{o['quantity']}</td>
                    <td>{o['unit']}</td>
                    <td>{o['category']}</td>
                </tr>
        """
        
    html_content += f"""
            </tbody>
        </table>
        
        <div class="footer-note">
            <strong>تێبینی:</strong> {note if note else 'هیچ تێبینیەک نیە'}
        </div>
        
        <script>
            window.onload = function() {{
                window.print();
            }}
        </script>
    </body>
    </html>
    """

    return Response(
        html_content,
        mimetype="text/html",
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)