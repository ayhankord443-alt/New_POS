import os
import sqlite3
import secrets
from datetime import datetime
from flask import (
    Flask, render_template_string, request, send_file,
    redirect, url_for, jsonify, session
)

# =========================================================
# ORGANIC JUICES - PROFESSIONAL QAYMA SYSTEM
# =========================================================

app = Flask(__name__)

# لە production ـدا ئەمە لە ENV دابنێ
app.secret_key = os.environ.get(
    "SECRET_KEY",
    "organic_juices_secret_key_2026"
)

DB_NAME = "clean_qayma.db"
SHARED_PASSWORD = os.environ.get("ORGANIC_PASSWORD", "organic123")


# =========================================================
# DATABASE
# =========================================================

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT NOT NULL,
            item_name TEXT NOT NULL,
            quantity REAL NOT NULL,
            unit TEXT NOT NULL,
            category TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            item_name TEXT NOT NULL,
            unit TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            device_id TEXT PRIMARY KEY,
            note_text TEXT DEFAULT ''
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS company_info (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            location TEXT NOT NULL DEFAULT 'پارکا شەهیدا',
            phone TEXT NOT NULL DEFAULT '07500113334'
        )
    """)

    c.execute("""
        INSERT OR IGNORE INTO company_info (id, location, phone)
        VALUES (1, 'پارکا شەهیدا', '07500113334')
    """)

    # -----------------------------------------------------
    # Categories
    # -----------------------------------------------------

    categories = ["فێقی", "مەعمەل", "مەغزەن"]

    for cat in categories:
        c.execute(
            "INSERT OR IGNORE INTO categories (name) VALUES (?)",
            (cat,)
        )

    # -----------------------------------------------------
    # Default Items
    # -----------------------------------------------------

    c.execute("SELECT COUNT(*) FROM items")

    if c.fetchone()[0] == 0:

        default_items = [

            # =========================
            # فێقی
            # =========================

            ("فێقی", "نافوكادو", "کیلو"),
            ("فێقی", "مانكو", "کیلو"),
            ("فێقی", "موز", "کارتۆن"),
            ("فێقی", "برتقال", "کیلو"),
            ("فێقی", "سف", "دانە"),
            ("فێقی", "ليمون", "کیلو"),
            ("فێقی", "جويزر", "کیلو"),
            ("فێقی", "جويز هند", "دانە"),
            ("فێقی", "هنار", "کیلو"),
            ("فێقی", "انه ناس", "لبان"),
            ("فێقی", "خوخ", "کیلو"),
            ("فێقی", "شاتو", "کیلو"),
            ("فێقی", "فه صب", "دانە"),
            ("فێقی", "سندی", "کیلو"),
            ("فێقی", "كوندور", "کیلو"),
            ("فێقی", "شوتی", "کیلو"),
            ("فێقی", "فراولا", "کیلو"),
            ("فێقی", "كیفی", "کیلو"),
            ("فێقی", "كاكی", "کیلو"),
            ("فێقی", "هیزیر", "کیلو"),
            ("فێقی", "هرميك", "کیلو"),

            # =========================
            # مەعمەل
            # =========================

            ("مەعمەل", "خوخ", "کیلو"),
            ("مەعمەل", "مانكو", "کیلو"),
            ("مەعمەل", "شاتو", "کیلو"),
            ("مەعمەل", "انه ناس", "لبان"),
            ("مەعمەل", "شيرلوكو", "دانە"),
            ("مەعمەل", "بابه t + ii cm", "دانە"),
            ("مەعمەل", "تمرهندی مزن", "دانە"),
            ("مەعمەل", "تمرهندی بجيك", "دانە"),
            ("مەعمەل", "مویش مزن", "کیلو"),
            ("مەعمەل", "مویش بجيك", "کیلو"),
            ("مەعمەل", "به فر", "دانە"),
            ("مەعمەل", "ئاف", "دانە"),
            ("مەعمەل", "عصير حليك", "دانە"),
            ("مەعمەل", "عصير زنجبيل+مانكو", "دانە"),
            ("مەعمەل", "کرينجوس", "دانە"),
            ("مەعمەل", "باقركه ری بيستی", "دانە"),
            ("مەعمەل", "دزهو کردن", "دانە"),

            # =========================
            # مەغزەن
            # =========================

            ("مەغزەن", "كلاس+قباغ", "دانە"),
            ("مەغزەن", "بطل مزن+قباغ", "دانە"),
            ("مەغزەن", "بطل بجيك+قباغ", "دانە"),
            ("مەغزەن", "قصاب", "دانە"),
            ("مەغزەن", "كلينيس", "دانە"),
            ("مەغزەن", "بوكس (۲)", "دانە"),
            ("مەغزەن", "بوكس (٤)", "دانە"),
            ("مەغزەن", "بوكس (٦)", "دانە"),
            ("مەغزەن", "علاكه لوكو", "دانە"),
            ("مەغزەن", "علاكه زلال", "دانە"),
            ("مەغزەن", "زاهی", "دانە"),
            ("مەغزەن", "كليت", "دانە"),
            ("مەغزەن", "باس باس", "کیلو"),
            ("مەغزەن", "باته", "کیلو"),
            ("مەغزەن", "مساحه", "دانە"),
            ("مەغزەن", "فرجه", "دانە"),
            ("مەغزەن", "دسكورك", "دانە"),
            ("مەغزەن", "وره فه كاشير", "دانە"),
            ("مەغزەن", "بوكس فواكه", "دانە"),
            ("مەغزەن", "جتل", "دانە"),
            ("مەغزەن", "قباغ", "دانە"),
            ("مەغزەن", "كلاس تيست", "دانە"),
            ("مەغزەن", "جامسی", "دانە"),
            ("مەغزەن", "معتر جو", "دانە"),
            ("مەغزەن", "خارنا بالندا", "دانە"),
        ]

        c.executemany("""
            INSERT INTO items
            (category, item_name, unit)
            VALUES (?, ?, ?)
        """, default_items)

    conn.commit()
    conn.close()


init_db()


# =========================================================
# HELPERS
# =========================================================

def get_device_id():

    if "device_id" not in session:
        session["device_id"] = secrets.token_hex(16)

    return session["device_id"]


def logged_in():
    return session.get("authenticated") is True


def get_note(device_id):

    conn = get_db()

    row = conn.execute("""
        SELECT note_text
        FROM notes
        WHERE device_id = ?
    """, (device_id,)).fetchone()

    conn.close()

    return row["note_text"] if row else ""


def get_orders(device_id):

    conn = get_db()

    rows = conn.execute("""
        SELECT id, item_name, quantity, unit, category, created_at
        FROM orders
        WHERE device_id = ?
        ORDER BY id ASC
    """, (device_id,)).fetchall()

    conn.close()

    return [
        {
            "id": r["id"],
            "item_name": r["item_name"],
            "quantity": r["quantity"],
            "unit": r["unit"],
            "category": r["category"],
            "created_at": r["created_at"]
        }
        for r in rows
    ]


def get_items(search=""):

    conn = get_db()

    if search:
        rows = conn.execute("""
            SELECT id, category, item_name, unit
            FROM items
            WHERE item_name LIKE ?
               OR category LIKE ?
            ORDER BY category, id
        """, (
            f"%{search}%",
            f"%{search}%"
        )).fetchall()

    else:
        rows = conn.execute("""
            SELECT id, category, item_name, unit
            FROM items
            ORDER BY category, id
        """).fetchall()

    conn.close()

    result = {}

    for r in rows:

        if r["category"] not in result:
            result[r["category"]] = []

        result[r["category"]].append({
            "id": r["id"],
            "name": r["item_name"],
            "unit": r["unit"]
        })

    return result


def get_all_items():

    conn = get_db()

    rows = conn.execute("""
        SELECT id, category, item_name, unit
        FROM items
        ORDER BY category, id DESC
    """).fetchall()

    conn.close()

    return rows


# =========================================================
# LOGIN PAGE
# =========================================================

LOGIN_TEMPLATE = """

<!DOCTYPE html>
<html lang="ku" dir="rtl">

<head>

<meta charset="UTF-8">
<meta name="viewport"
content="width=device-width,initial-scale=1">

<title>Organic Juices</title>

<style>

*{
    box-sizing:border-box;
}

body{
    margin:0;
    min-height:100vh;
    display:flex;
    align-items:center;
    justify-content:center;
    font-family:system-ui,-apple-system,sans-serif;
    background:
        radial-gradient(circle at top,#e8f5e9,#f8faf8 55%);
}

.login-card{
    width:min(420px,92%);
    background:white;
    padding:35px 28px;
    border-radius:24px;
    box-shadow:0 15px 45px rgba(0,0,0,.10);
    text-align:center;
    border:1px solid #e8eee8;
}

.logo{
    width:95px;
    height:95px;
    object-fit:contain;
    margin-bottom:10px;
}

h1{
    color:#176b2c;
    margin:5px 0;
}

.subtitle{
    color:#777;
    font-size:13px;
    margin-bottom:25px;
}

input{
    width:100%;
    padding:14px;
    border:1px solid #d5ddd5;
    border-radius:12px;
    font-size:16px;
    outline:none;
}

input:focus{
    border-color:#2e7d32;
}

button{
    width:100%;
    margin-top:15px;
    padding:14px;
    border:0;
    border-radius:12px;
    background:#218838;
    color:white;
    font-size:16px;
    font-weight:bold;
    cursor:pointer;
}

.error{
    background:#ffebee;
    color:#c62828;
    padding:10px;
    border-radius:10px;
    margin-bottom:12px;
}

</style>

</head>

<body>

<div class="login-card">

<img src="/logo.png"
class="logo"
onerror="this.style.display='none'">

<h1>ئۆرگانیک جویس</h1>

<div class="subtitle">
سیستەمی قایمەی کۆمپانیا
</div>

{% if error %}
<div class="error">{{ error }}</div>
{% endif %}

<form method="POST">

<input
type="password"
name="password"
placeholder="ڕەمزی چوونەژوورەوە"
required
autofocus>

<button>
🔐 چوونەژوورەوە
</button>

</form>

</div>

</body>
</html>

"""


# =========================================================
# MAIN PAGE
# =========================================================

HTML_TEMPLATE = """

<!DOCTYPE html>

<html lang="ku" dir="rtl">

<head>

<meta charset="UTF-8">

<meta name="viewport"
content="width=device-width,initial-scale=1">

<title>قایمە | Organic Juices</title>

<style>

*{
    box-sizing:border-box;
}

body{
    margin:0;
    padding:12px;
    font-family:system-ui,-apple-system,sans-serif;
    background:#f5f8f5;
    color:#172017;
}

body:before{
    content:"";
    position:fixed;
    inset:0;
    background:url('/logo.png') center/280px no-repeat;
    opacity:.035;
    pointer-events:none;
    z-index:-1;
}

/* HEADER */

.header{
    max-width:1200px;
    margin:auto;
    background:white;
    padding:14px 18px;
    border-radius:18px;
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:10px;
    box-shadow:0 4px 18px rgba(0,0,0,.06);
    border-bottom:3px solid #218838;
}

.brand{
    display:flex;
    align-items:center;
    gap:10px;
}

.brand img{
    width:45px;
    height:45px;
    object-fit:contain;
}

.brand h1{
    margin:0;
    color:#176b2c;
    font-size:19px;
}

.actions{
    display:flex;
    gap:7px;
}

.action{
    text-decoration:none;
    padding:9px 12px;
    border-radius:9px;
    font-size:12px;
    font-weight:bold;
    color:white;
}

.settings{
    background:#2e7d32;
}

.logout{
    background:#c62828;
}

/* SEARCH */

.search-box{
    max-width:1200px;
    margin:14px auto;
    background:white;
    padding:12px;
    border-radius:15px;
    box-shadow:0 3px 15px rgba(0,0,0,.05);
}

.search-box input{
    width:100%;
    padding:13px;
    border:1px solid #ddd;
    border-radius:10px;
    font-size:14px;
}

/* NOTE */

.note{
    max-width:1200px;
    margin:14px auto;
    background:#fffde7;
    border:1px solid #dce775;
    padding:13px;
    border-radius:15px;
}

.note textarea{
    width:100%;
    height:65px;
    border:1px solid #ddd;
    border-radius:10px;
    padding:10px;
    resize:vertical;
}

.note button{
    margin-top:7px;
    background:#689f38;
    color:white;
    border:0;
    border-radius:8px;
    padding:8px 14px;
    font-weight:bold;
}

/* CONTENT */

.content{
    max-width:1200px;
    margin:auto;
}

.category{
    margin-top:22px;
}

.category-title{
    color:#176b2c;
    font-size:18px;
    font-weight:900;
    border-right:5px solid #2e7d32;
    padding:7px 10px;
    background:white;
    border-radius:8px;
    margin-bottom:10px;
}

/* ITEMS */

.grid{
    display:grid;
    grid-template-columns:
        repeat(auto-fill,minmax(145px,1fr));
    gap:10px;
}

.item{
    background:white;
    border:1px solid #e2e8e2;
    border-radius:14px;
    padding:11px;
    box-shadow:0 3px 10px rgba(0,0,0,.04);
    transition:.15s;
}

.item:hover{
    transform:translateY(-2px);
    box-shadow:0 6px 18px rgba(0,0,0,.08);
}

.item-name{
    font-size:14px;
    font-weight:900;
    min-height:35px;
}

.unit{
    font-size:11px;
    color:#689f38;
    margin-bottom:8px;
}

.controls{
    display:flex;
    gap:4px;
}

.qty{
    width:42px;
    text-align:center;
    border:1px solid #ccc;
    border-radius:7px;
    font-weight:bold;
}

.small-btn{
    width:29px;
    border:0;
    border-radius:7px;
    background:#eeeeee;
    font-weight:bold;
}

.add{
    flex:1;
    border:0;
    border-radius:7px;
    background:#218838;
    color:white;
    font-weight:bold;
    cursor:pointer;
}

/* SUMMARY */

.summary{
    max-width:1200px;
    margin:25px auto;
    background:white;
    border:2px solid #218838;
    border-radius:18px;
    padding:15px;
    box-shadow:0 7px 25px rgba(0,0,0,.08);
}

.summary-header{
    display:flex;
    justify-content:space-between;
    align-items:center;
    gap:10px;
}

.summary h2{
    color:#176b2c;
    margin:0;
}

.count{
    background:#e8f5e9;
    color:#176b2c;
    padding:6px 10px;
    border-radius:20px;
    font-weight:bold;
    font-size:12px;
}

.table-wrap{
    overflow-x:auto;
}

table{
    width:100%;
    border-collapse:collapse;
    margin-top:12px;
}

th,td{
    padding:10px;
    border-bottom:1px solid #eee;
    text-align:right;
    font-size:13px;
}

th{
    background:#f1f8f2;
    color:#176b2c;
}

.delete-order{
    border:0;
    background:#ffebee;
    color:#c62828;
    border-radius:6px;
    padding:5px 8px;
    cursor:pointer;
}

.pdf{
    width:100%;
    padding:13px;
    margin-top:12px;
    border:0;
    border-radius:10px;
    background:#176b2c;
    color:white;
    font-size:15px;
    font-weight:bold;
}

.clear{
    width:100%;
    padding:11px;
    margin-top:7px;
    border:0;
    border-radius:10px;
    background:#c62828;
    color:white;
    font-weight:bold;
}

/* MOBILE */

@media(max-width:600px){

    body{
        padding:7px;
    }

    .header{
        padding:10px;
    }

    .brand h1{
        font-size:15px;
    }

    .brand img{
        width:38px;
        height:38px;
    }

    .action{
        padding:7px;
        font-size:10px;
    }

    .grid{
        grid-template-columns:
            repeat(2,minmax(0,1fr));
        gap:7px;
    }

    .item{
        padding:8px;
    }

    .item-name{
        font-size:12px;
    }

    .qty{
        width:34px;
    }

    .small-btn{
        width:25px;
    }

    .add{
        font-size:10px;
    }

    th,td{
        padding:7px 5px;
        font-size:11px;
    }
}

</style>

</head>

<body>

<!-- HEADER -->

<header class="header">

<div class="brand">

<img src="/logo.png"
onerror="this.style.display='none'">

<h1>کۆمپانییا ئۆرگانیک جویس</h1>

</div>

<div class="actions">

<a class="action settings"
href="/settings">
⚙️ سێتینگ
</a>

<a class="action logout"
href="/logout">
خروج
</a>

</div>

</header>


<!-- SEARCH -->

<div class="search-box">

<input
id="search"
type="search"
placeholder="🔎 گەڕان بۆ بابەت..."
value="{{ search }}"
oninput="searchItems()">

</div>


<!-- NOTE -->

<div class="note">

<strong>📝 تێبینی قایمە</strong>

<textarea
id="noteInput"
placeholder="تێبینی خۆت لێرە بنووسە..."
>{{ current_note }}</textarea>

<button onclick="saveNote()">
💾 تومارکردنی تێبینی
</button>

</div>


<div class="content">

{% for category, items in all_items.items() %}

<section
class="category"
data-category="{{ category }}">

<div class="category-title">
🔸 {{ category }}
</div>

<div class="grid">

{% for item in items %}

<div
class="item"
data-name="{{ item.name|lower }}">

<div class="item-name">
{{ item.name }}
</div>

<div class="unit">
یەکە: {{ item.unit }}
</div>

<div class="controls">

<button
class="small-btn"
onclick="changeQty(this,-1)">
−
</button>

<input
class="qty"
type="number"
value="1"
min="0.1"
step="0.1">

<button
class="small-btn"
onclick="changeQty(this,1)">
+
</button>

<button
class="add"
data-id="{{ item.id }}"
data-name="{{ item.name }}"
data-unit="{{ item.unit }}"
data-category="{{ category }}"
onclick="addItem(this)">
زێدە
</button>

</div>

</div>

{% endfor %}

</div>

</section>

{% endfor %}

</div>


<!-- SUMMARY -->

<div
class="summary"
id="summary"
style="{% if orders %}{% else %}display:none{% endif %}">

<div class="summary-header">

<h2>📋 قایمە</h2>

<span class="count"
id="orderCount">
{{ orders|length }} بابەت
</span>

</div>

<div class="table-wrap">

<table>

<thead>

<tr>
<th>بەش</th>
<th>بابەت</th>
<th>بڕ</th>
<th>یەکە</th>
<th>کردار</th>
</tr>

</thead>

<tbody id="ordersBody">

{% for order in orders %}

<tr>

<td>{{ order.category }}</td>

<td><b>{{ order.item_name }}</b></td>

<td>{{ order.quantity }}</td>

<td>{{ order.unit }}</td>

<td>
<button
class="delete-order"
onclick="deleteOrder({{ order.id }})">
🗑️
</button>
</td>

</tr>

{% endfor %}

</tbody>

</table>

</div>

<button
class="pdf"
onclick="downloadPDF()">

📄 دروستکردنی PDF

</button>

<button
class="clear"
onclick="clearOrders()">

🗑️ پاککردنی هەموو قایمە

</button>

</div>


<script>

function changeQty(button, amount){

    const input =
        button.parentElement.querySelector(".qty");

    let value =
        parseFloat(input.value) || 1;

    value += amount;

    if(value < 0.1)
        value = 0.1;

    input.value =
        Number(value.toFixed(2));
}


async function addItem(button){

    const controls =
        button.parentElement;

    const quantity =
        controls.querySelector(".qty").value;

    const form =
        new FormData();

    form.append(
        "item_name",
        button.dataset.name
    );

    form.append(
        "unit",
        button.dataset.unit
    );

    form.append(
        "category",
        button.dataset.category
    );

    form.append(
        "quantity",
        quantity
    );

    button.disabled = true;
    button.innerText = "✓";

    try{

        const response =
            await fetch(
                "/quick_add_ajax",
                {
                    method:"POST",
                    body:form
                }
            );

        const data =
            await response.json();

        if(data.status === "success"){

            updateOrders(data.orders);

            controls.querySelector(".qty").value = 1;

        }else{

            alert(data.message || "هەڵەیەک ڕوویدا");

        }

    }catch(error){

        alert("پەیوەندی بە سێرڤەرەوە نەکرا");

    }

    setTimeout(()=>{
        button.disabled=false;
        button.innerText="زێدە";
    },400);

}


function updateOrders(orders){

    const summary =
        document.getElementById("summary");

    const body =
        document.getElementById("ordersBody");

    const count =
        document.getElementById("orderCount");

    if(!orders.length){

        summary.style.display="none";
        body.innerHTML="";
        count.innerText="0 بابەت";

        return;
    }

    summary.style.display="block";

    count.innerText =
        orders.length + " بابەت";

    body.innerHTML =
        orders.map(o => `

        <tr>

        <td>${escapeHTML(o.category)}</td>

        <td><b>${escapeHTML(o.item_name)}</b></td>

        <td>${o.quantity}</td>

        <td>${escapeHTML(o.unit)}</td>

        <td>

        <button
        class="delete-order"
        onclick="deleteOrder(${o.id})">

        🗑️

        </button>

        </td>

        </tr>

        `).join("");

}


async function deleteOrder(id){

    if(!confirm("ئەم بابەتە لە قایمە بسڕینەوە؟"))
        return;

    const response =
        await fetch(
            "/delete_order/" + id,
            {
                method:"POST"
            }
        );

    const data =
        await response.json();

    if(data.status === "success")
        updateOrders(data.orders);

}


async function clearOrders(){

    if(!confirm(
        "دڵنیایت دەتەوێت هەموو قایمە پاک بکەیتەوە؟"
    ))
        return;

    const response =
        await fetch("/clear_ajax");

    const data =
        await response.json();

    if(data.status === "success")
        updateOrders([]);

}


async function saveNote(){

    const note =
        document.getElementById(
            "noteInput"
        ).value;

    const form =
        new FormData();

    form.append("note",note);

    const response =
        await fetch(
            "/save_note",
            {
                method:"POST",
                body:form
            }
        );

    const data =
        await response.json();

    if(data.status === "success")
        alert("✓ تێبینی بە سەرکەوتوویی هەڵگیرا");

}


function searchItems(){

    const value =
        document
        .getElementById("search")
        .value
        .toLowerCase()
        .trim();

    document
    .querySelectorAll(".category")
    .forEach(category => {

        let visible = 0;

        category
        .querySelectorAll(".item")
        .forEach(item => {

            const name =
                item.dataset.name;

            const show =
                !value ||
                name.includes(value);

            item.style.display =
                show ? "" : "none";

            if(show)
                visible++;

        });

        category.style.display =
            visible ? "" : "none";

    });

}


function downloadPDF(){

    window.location.href =
        "/download_pdf";

}


function escapeHTML(value){

    return String(value)
        .replaceAll("&","&amp;")
        .replaceAll("<","&lt;")
        .replaceAll(">","&gt;")
        .replaceAll('"',"&quot;")
        .replaceAll("'","&#039;");

}

</script>

</body>
</html>

"""


def get_company_info():
    conn = get_db()
    row = conn.execute("SELECT location, phone FROM company_info WHERE id = 1").fetchone()
    conn.close()
    if row:
        return row["location"], row["phone"]
    return "پارکا شەهیدا", "07500113334"


# =========================================================
# SETTINGS
# =========================================================

SETTINGS_TEMPLATE = """

<!DOCTYPE html>

<html lang="ku" dir="rtl">

<head>

<meta charset="UTF-8">

<meta name="viewport"
content="width=device-width,initial-scale=1">

<title>سێتینگ | Organic Juices</title>

<style>

*{
    box-sizing:border-box;
}

body{
    margin:0;
    padding:15px;
    background:#f5f8f5;
    font-family:system-ui;
}

.container{
    max-width:1100px;
    margin:auto;
}

.header,
.card{
    background:white;
    border-radius:16px;
    padding:18px;
    margin-bottom:15px;
    box-shadow:0 4px 18px rgba(0,0,0,.05);
}

.header{
    display:flex;
    justify-content:space-between;
    align-items:center;
}

h2,h3{
    color:#176b2c;
}

input,select{
    width:100%;
    padding:12px;
    margin:6px 0 12px;
    border:1px solid #ccc;
    border-radius:9px;
}

button{
    width:100%;
    padding:11px;
    border:0;
    border-radius:9px;
    background:#218838;
    color:white;
    font-weight:bold;
    cursor:pointer;
}

.back{
    text-decoration:none;
    background:#218838;
    color:white;
    padding:9px 13px;
    border-radius:9px;
}

.table-wrap{
    overflow:auto;
}

table{
    width:100%;
    border-collapse:collapse;
}

th,td{
    padding:10px;
    border-bottom:1px solid #eee;
    text-align:right;
    white-space:nowrap;
}

th{
    color:#176b2c;
    background:#f1f8f2;
}

.actions{
    display:flex;
    gap:5px;
}

.edit{
    background:#1565c0;
    color:white;
    padding:6px 9px;
    border-radius:6px;
    text-decoration:none;
    font-size:12px;
}

.delete{
    background:#c62828;
    color:white;
    padding:6px 9px;
    border-radius:6px;
    text-decoration:none;
    font-size:12px;
}

</style>

</head>

<body>

<div class="container">

<div class="header">

<h2>⚙️ سێتینگی سیستەم</h2>

<a class="back" href="/">
⬅️ گەڕانەوە
</a>

</div>


<div class="card">

<h3>➕ زیادکردنی بابەتی نوێ</h3>

<form method="POST"
action="/add_item_setting">

<label>بەش</label>

<select name="category">

{% for cat in categories %}

<option value="{{ cat }}">
{{ cat }}
</option>

{% endfor %}

</select>

<label>ناوی بابەت</label>

<input
name="item_name"
placeholder="ناوی بابەت"
required>

<label>یەکە</label>

<input
name="unit"
placeholder="کیلو / دانە / کارتۆن..."
required>

<button>
💾 تومارکردن
</button>

</form>

</div>


<div class="card">

<h3>
📋 لیستی هەموو بابەتەکان
</h3>

<div class="table-wrap">

<table>

<thead>

<tr>

<th>#</th>
<th>بەش</th>
<th>ناو</th>
<th>یەکە</th>
<th>کردار</th>

</tr>

</thead>

<tbody>

{% for item in items %}

<tr>

<td>{{ item.id }}</td>

<td>{{ item.category }}</td>

<td><b>{{ item.item_name }}</b></td>

<td>{{ item.unit }}</td>

<td>

<div class="actions">

<a
class="edit"
href="/edit_item/{{ item.id }}">
✏️ Edit
</a>

<a
class="delete"
href="/delete_item_setting/{{ item.id }}"
onclick="return confirm('دڵنیایت؟')">
🗑️ Delete
</a>

</div>

</td>

</tr>

{% endfor %}

</tbody>

</table>

</div>

</div>

</div>

</body>
</html>

"""


# =========================================================
# EDIT ITEM
# =========================================================

EDIT_TEMPLATE = """

<!DOCTYPE html>

<html lang="ku" dir="rtl">

<head>

<meta charset="UTF-8">

<meta name="viewport"
content="width=device-width,initial-scale=1">

<title>Edit Item</title>

<style>

body{
    margin:0;
    padding:20px;
    background:#f5f8f5;
    font-family:system-ui;
}

.card{
    max-width:500px;
    margin:30px auto;
    background:white;
    padding:25px;
    border-radius:18px;
    box-shadow:0 8px 30px rgba(0,0,0,.08);
}

h2{
    color:#176b2c;
}

input,select{
    width:100%;
    padding:12px;
    margin:7px 0 15px;
    border:1px solid #ccc;
    border-radius:9px;
    box-sizing:border-box;
}

button{
    width:100%;
    padding:13px;
    border:0;
    border-radius:9px;
    background:#218838;
    color:white;
    font-weight:bold;
}

.back{
    display:block;
    text-align:center;
    margin-top:12px;
    color:#176b2c;
}

</style>

</head>

<body>

<div class="card">

<h2>✏️ دەستکاریکردنی بابەت</h2>

<form method="POST">

<label>بەش</label>

<select name="category">

{% for cat in categories %}

<option
value="{{ cat }}"
{% if item.category == cat %}
selected
{% endif %}>

{{ cat }}

</option>

{% endfor %}

</select>

<label>ناوی بابەت</label>

<input
name="item_name"
value="{{ item.item_name }}"
required>

<label>یەکە</label>

<input
name="unit"
value="{{ item.unit }}"
required>

<button>
💾 پاشەکەوتکردن
</button>

</form>

<a class="back" href="/settings">
⬅️ گەڕانەوە بۆ سێتینگ
</a>

</div>

</body>
</html>

"""


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    error = None

    if request.method == "POST":

        password = request.form.get("password", "")

        if secrets.compare_digest(
            password,
            SHARED_PASSWORD
        ):

            session.clear()

            session["authenticated"] = True

            session["device_id"] = secrets.token_hex(16)

            return redirect(url_for("index"))

        error = "❌ ڕەمز هەڵەیە"

    return render_template_string(
        LOGIN_TEMPLATE,
        error=error
    )


@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


# =========================================================
# MAIN
# =========================================================

@app.route("/")
def index():

    if not logged_in():
        return redirect(url_for("login"))

    search = request.args.get("search", "").strip()

    device_id = get_device_id()

    return render_template_string(
        HTML_TEMPLATE,
        all_items=get_items(search),
        orders=get_orders(device_id),
        current_note=get_note(device_id),
        search=search
    )


# =========================================================
# NOTE
# =========================================================

@app.route("/save_note", methods=["POST"])
def save_note():

    if not logged_in():
        return jsonify({
            "status": "unauthorized"
        }), 401

    device_id = get_device_id()

    note = request.form.get(
        "note",
        ""
    ).strip()

    conn = get_db()

    conn.execute("""
        INSERT OR REPLACE INTO notes
        (device_id, note_text)
        VALUES (?, ?)
    """, (
        device_id,
        note
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "status": "success"
    })


# =========================================================
# ADD ORDER
# =========================================================

@app.route("/quick_add_ajax", methods=["POST"])
def quick_add_ajax():

    if not logged_in():
        return jsonify({
            "status": "unauthorized"
        }), 401

    try:

        item_name = request.form.get(
            "item_name",
            ""
        ).strip()

        unit = request.form.get(
            "unit",
            ""
        ).strip()

        category = request.form.get(
            "category",
            ""
        ).strip()

        quantity = float(
            request.form.get(
                "quantity",
                0
            )
        )

        if not item_name:
            raise ValueError("ناوی بابەت بەتاڵە")

        if quantity <= 0:
            raise ValueError("بڕ دەبێت لە سفر گەورەتر بێت")

        device_id = get_device_id()

        conn = get_db()

        conn.execute("""
            INSERT INTO orders
            (
                device_id,
                item_name,
                quantity,
                unit,
                category
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            device_id,
            item_name,
            quantity,
            unit,
            category
        ))

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
# DELETE SINGLE ORDER
# =========================================================

@app.route(
    "/delete_order/<int:order_id>",
    methods=["POST"]
)
def delete_order(order_id):

    if not logged_in():
        return jsonify({
            "status": "unauthorized"
        }), 401

    device_id = get_device_id()

    conn = get_db()

    conn.execute("""
        DELETE FROM orders
        WHERE id = ?
        AND device_id = ?
    """, (
        order_id,
        device_id
    ))

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
        return jsonify({
            "status": "unauthorized"
        }), 401

    device_id = get_device_id()

    conn = get_db()

    conn.execute("""
        DELETE FROM orders
        WHERE device_id = ?
    """, (
        device_id,
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "status": "success",
        "orders": []
    })


# =========================================================
# SETTINGS
# =========================================================

@app.route("/settings")
def settings_page():

    if not logged_in():
        return redirect(url_for("login"))

    conn = get_db()

    categories = [
        r["name"]
        for r in conn.execute("""
            SELECT name
            FROM categories
            ORDER BY id
        """).fetchall()
    ]

    conn.close()

    location, phone = get_company_info()

    return render_template_string(
        SETTINGS_TEMPLATE,
        items=get_all_items(),
        categories=categories,
        location=location,
        phone=phone
    )


@app.route("/save_company_info", methods=["POST"])
def save_company_info():

    if not logged_in():
        return redirect(url_for("login"))

    location = request.form.get("location", "").strip() or "پارکا شەهیدا"
    phone = request.form.get("phone", "").strip() or "07500113334"

    conn = get_db()
    conn.execute("""
        UPDATE company_info
        SET location = ?, phone = ?
        WHERE id = 1
    """, (location, phone))
    conn.commit()
    conn.close()

    return redirect(url_for("settings_page"))


# =========================================================
# ADD ITEM
# =========================================================

@app.route(
    "/add_item_setting",
    methods=["POST"]
)
def add_item_setting():

    if not logged_in():
        return redirect(url_for("login"))

    category = request.form.get(
        "category",
        ""
    ).strip()

    item_name = request.form.get(
        "item_name",
        ""
    ).strip()

    unit = request.form.get(
        "unit",
        ""
    ).strip()

    if not item_name or not unit:
        return redirect(
            url_for("settings_page")
        )

    conn = get_db()

    # جلوگیری لە دووبارەکردنەوەی هەمان بابەت
    exists = conn.execute("""
        SELECT id
        FROM items
        WHERE category = ?
        AND item_name = ?
    """, (
        category,
        item_name
    )).fetchone()

    if not exists:

        conn.execute("""
            INSERT INTO items
            (category, item_name, unit)
            VALUES (?, ?, ?)
        """, (
            category,
            item_name,
            unit
        ))

        conn.commit()

    conn.close()

    return redirect(
        url_for("settings_page")
    )


# =========================================================
# EDIT ITEM
# =========================================================

@app.route(
    "/edit_item/<int:item_id>",
    methods=["GET", "POST"]
)
def edit_item(item_id):

    if not logged_in():
        return redirect(url_for("login"))

    conn = get_db()

    item = conn.execute("""
        SELECT *
        FROM items
        WHERE id = ?
    """, (
        item_id,
    )).fetchone()

    categories = [
        r["name"]
        for r in conn.execute("""
            SELECT name
            FROM categories
            ORDER BY id
        """).fetchall()
    ]

    if not item:

        conn.close()

        return redirect(
            url_for("settings_page")
        )

    if request.method == "POST":

        category = request.form.get(
            "category",
            ""
        ).strip()

        item_name = request.form.get(
            "item_name",
            ""
        ).strip()

        unit = request.form.get(
            "unit",
            ""
        ).strip()

        conn.execute("""
            UPDATE items
            SET category = ?,
                item_name = ?,
                unit = ?
            WHERE id = ?
        """, (
            category,
            item_name,
            unit,
            item_id
        ))

        conn.commit()
        conn.close()

        return redirect(
            url_for("settings_page")
        )

    conn.close()

    return render_template_string(
        EDIT_TEMPLATE,
        item=item,
        categories=categories
    )


# =========================================================
# DELETE ITEM
# =========================================================

@app.route(
    "/delete_item_setting/<int:item_id>"
)
def delete_item_setting(item_id):

    if not logged_in():
        return redirect(url_for("login"))

    conn = get_db()

    conn.execute("""
        DELETE FROM items
        WHERE id = ?
    """, (
        item_id,
    ))

    conn.commit()
    conn.close()

    return redirect(
        url_for("settings_page")
    )


# =========================================================
# LOGO
# =========================================================

@app.route("/logo.png")
def logo():

    logo_path = os.path.join(
        os.getcwd(),
        "logo.png"
    )

    if os.path.exists(logo_path):
        return send_file(
            logo_path,
            mimetype="image/png"
        )

    return "", 404


# =========================================================
# PDF
# =========================================================

@app.route("/download_pdf")
def download_pdf():

    if not logged_in():
        return redirect(url_for("login"))

    try:

        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import (
            getSampleStyleSheet,
            ParagraphStyle
        )
        from reportlab.lib.enums import TA_CENTER, TA_RIGHT
        from reportlab.platypus import (
            SimpleDocTemplate,
            Paragraph,
            Spacer,
            Table,
            TableStyle
        )
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont

        device_id = get_device_id()

        orders = get_orders(device_id)

        note = get_note(device_id)
        location, phone = get_company_info()

        # -------------------------------------------------
        # Font
        # -------------------------------------------------

        font_name = "Helvetica"

        font_candidates = [

            os.path.join(
                os.getcwd(),
                "Amiri",
                "Amiri-Regular.ttf"
            ),

            os.path.join(
                os.getcwd(),
                "Amiri-Regular.ttf"
            ),

            "C:\\Windows\\Fonts\\arial.ttf"

        ]

        for path in font_candidates:

            if os.path.exists(path):

                try:

                    pdfmetrics.registerFont(
                        TTFont(
                            "OrganicArabic",
                            path
                        )
                    )

                    font_name = "OrganicArabic"

                    break

                except:
                    pass

        # -------------------------------------------------
        # PDF
        # -------------------------------------------------

        filename = (
            "Organic_Juices_Qayma_"
            + datetime.now().strftime(
                "%Y%m%d_%H%M"
            )
            + ".pdf"
        )

        doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=30,
            leftMargin=30,
            topMargin=30,
            bottomMargin=30
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "Title",
            parent=styles["Heading1"],
            fontName=font_name,
            fontSize=20,
            alignment=TA_CENTER,
            textColor=colors.HexColor(
                "#176b2c"
            )
        )

        normal_style = ParagraphStyle(
            "NormalArabic",
            parent=styles["Normal"],
            fontName=font_name,
            fontSize=10,
            alignment=TA_RIGHT
        )

        center_style = ParagraphStyle(
            "Center",
            parent=styles["Normal"],
            fontName=font_name,
            fontSize=10,
            alignment=TA_CENTER
        )

        story = []

        # Header
        story.append(
            Paragraph(
                "کۆمپانییا ئۆرگانیک جویس",
                title_style
            )
        )

        story.append(
            Spacer(1, 5)
        )

        story.append(
            Paragraph(
                "لیستا قایمە",
                center_style
            )
        )

        story.append(Spacer(1, 3))
        story.append(Paragraph(
            "شوێن: " + str(location) + " | مۆبایل: " + str(phone),
            center_style
        ))

        story.append(
            Spacer(1, 5)
        )

        story.append(
            Paragraph(
                "بەروار: "
                + datetime.now().strftime(
                    "%Y-%m-%d"
                )
                + " | کات: "
                + datetime.now().strftime(
                    "%H:%M"
                ),
                center_style
            )
        )

        story.append(
            Spacer(1, 15)
        )

        # Note
        if note:

            story.append(
                Paragraph(
                    "<b>تێبینی:</b> "
                    + note,
                    normal_style
                )
            )

            story.append(
                Spacer(1, 10)
            )

        # Table
        table_data = [

            [
                Paragraph(
                    "بەش",
                    center_style
                ),

                Paragraph(
                    "بابەت",
                    center_style
                ),

                Paragraph(
                    "بڕ",
                    center_style
                ),

                Paragraph(
                    "یەکە",
                    center_style
                )
            ]

        ]

        for order in orders:

            table_data.append([

                Paragraph(
                    str(order["category"]),
                    center_style
                ),

                Paragraph(
                    "<b>"
                    + str(order["item_name"])
                    + "</b>",
                    center_style
                ),

                Paragraph(
                    str(order["quantity"]),
                    center_style
                ),

                Paragraph(
                    str(order["unit"]),
                    center_style
                )

            ])

        if not orders:

            table_data.append([

                Paragraph(
                    "قایمە بەتاڵە",
                    center_style
                ),
                "",
                "",
                ""

            ])

        table = Table(
            table_data,
            colWidths=[
                90,
                230,
                70,
                70
            ],
            repeatRows=1
        )

        table.setStyle(
            TableStyle([

                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor(
                        "#e8f5e9"
                    )
                ),

                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor(
                        "#176b2c"
                    )
                ),

                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor(
                        "#cfd8cf"
                    )
                ),

                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                ),

                (
                    "ALIGN",
                    (0, 0),
                    (-1, -1),
                    "CENTER"
                ),

                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    8
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    8
                )

            ])
        )

        story.append(table)

        story.append(
            Spacer(1, 15)
        )

        story.append(
            Paragraph(
                "کۆی بابەتەکان: "
                + str(len(orders)),
                center_style
            )
        )

        def draw_watermark(canvas, doc):
            canvas.saveState()
            try:
                from reportlab.lib.utils import ImageReader
                logo_path = os.path.join(os.getcwd(), "logo.png")
                if os.path.exists(logo_path):
                    img = ImageReader(logo_path)
                    iw, ih = img.getSize()
                    target_w = 300
                    target_h = target_w * ih / float(iw) if iw else 300
                    x = (A4[0] - target_w) / 2
                    y = (A4[1] - target_h) / 2
                    if hasattr(canvas, "setFillAlpha"):
                        canvas.setFillAlpha(0.08)
                    canvas.drawImage(img, x, y, width=target_w, height=target_h, mask="auto", preserveAspectRatio=True)
                    if hasattr(canvas, "setFillAlpha"):
                        canvas.setFillAlpha(1)
            except Exception:
                pass
            canvas.restoreState()

        doc.build(story, onFirstPage=draw_watermark, onLaterPages=draw_watermark)

        return send_file(
            filename,
            as_attachment=True
        )

    except Exception as e:

        return (
            "PDF Error: "
            + str(e),
            500
        )


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    init_db()

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )