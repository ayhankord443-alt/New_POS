import os
import sqlite3
from flask import Flask, render_template_string, request, send_file, redirect, url_for
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from bidi.algorithm import get_display
import arabic_reshaper

app = Flask(__name__)

# --- 1. Database Setup (دروستکردنی داتابەیس و خشتە بە شێوەیەکی خۆکار بۆ ئەوەی هەڵەی no such table نەدات) ---
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT,
            quantity TEXT,
            price TEXT,
            total TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- 2. Font Registration (تۆمارکردنی فۆنتی Amiri بە شێوازێکی پارێزراو بۆ لینوکس و ویندۆز) ---
try:
    font_paths = [
        os.path.join("Amiri", "Amiri-Regular.ttf"),
        "Amiri-Regular.ttf",
        "/app/Amiri/Amiri-Regular.ttf"
    ]
    font_registered = False
    for path in font_paths:
        if os.path.exists(path):
            pdfmetrics.registerFont(TTFont('Amiri', path))
            font_registered = True
            break
    if not font_registered:
        print("Warning: Amiri font file not found in standard paths!")
except Exception as e:
    print(f"Font registration error: {e}")

# --- 3. Text Shaping Helper ---
def reshape_text(text):
    if not text:
        return ""
    reshaped = arabic_reshaper.reshape(str(text))
    return get_display(reshaped)

# --- 4. HTML Template & Routes ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ku" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>کۆمپانیا یا لورگانیک جوریی</title>
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
        .container {
            max-width: 600px;
            margin: auto;
            background: #f9f9f9;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #419245;
        }
        a.btn {
            display: inline-block;
            background-color: #419245;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 5px;
            margin-top: 15px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>بەخێر هاتن بۆ سیستەمێ پۆس</h1>
        <p>داتابەیس و فۆنت بە سەرکەوتوویی ئامادە کران.</p>
        <a href="/download_pdf" class="btn">داگرتنی PDF</a>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM orders")
    orders = c.fetchall()
    conn.close()
    return render_template_string(HTML_TEMPLATE, orders=orders)

@app.route('/download_pdf')
def download_pdf():
    file_path = "output.pdf"
    doc = SimpleDocTemplate(file_path, pagesize=letter)
    story = []
    
    styles = getSampleStyleSheet()
    kurdish_style = ParagraphStyle(
        'KurdishStyle',
        parent=styles['Normal'],
        fontName='Amiri',
        fontSize=14,
        leading=18,
        alignment=2
    )
    
    title_text = reshape_text("ڕاپۆرتی فرۆشتن و داواکارییەکان - لورگانیک")
    story.append(Paragraph(title_text, kurdish_style))
    story.append(Spacer(1, 15))
    
    doc.build(story)
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)