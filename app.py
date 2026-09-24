
from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3, os

app = Flask(__name__)
app.secret_key = "myassignment-local-key"
DB = "database.db"

TABLES = {
    "CUSTOMER": ("ลูกค้า", ["CUSTOMER_ID","CUS_NAME","CUS_HOUSE_NO","CUS_STREET","CUS_SUBDISTRICT","CUS_DISTRICT","CUS_PROVINCE","CUS_POSTCODE","CUS_PHONE"]),
    "DEVICE": ("อุปกรณ์", ["DEVICE_ID","CUSTOMER_ID","DEVICE_TYPE","BRAND","MODEL"]),
    "TECHNICIAN": ("ช่าง", ["TECH_ID","TECH_NAME","TECH_SPECIALTY"]),
    "SYMPTOM": ("อาการเสีย", ["SYMPTOM_ID","SYMPTOM_NAME"]),
    "SPARE_PART": ("อะไหล่", ["PART_ID","PART_NAME","PART_PRICE","STOCK_QTY"]),
    "SUPPLIER": ("ผู้จำหน่าย", ["SUPPLIER_ID","SUPPLIER_NAME","SUPPLIER_PHONE"]),
    "REPAIR_ORDER": ("รายการซ่อม", ["ORDER_ID","DEVICE_ID","TECH_ID","DATE_RECEIVED","DATE_COMPLETED","LABOR_COST"]),
    "REPAIR_SYMPTOM": ("อาการของงานซ่อม", ["ORDER_ID","SYMPTOM_ID"]),
    "REPAIR_PART_USED": ("อะไหล่ที่ใช้", ["ORDER_ID","PART_ID","QTY_USED"]),
    "PAYMENT": ("การชำระเงิน", ["PAYMENT_ID","ORDER_ID","PAYMENT_METHOD","PAYMENT_AMOUNT","PAYMENT_STATUS","PAYMENT_DATE"]),
    "STOCK_MOVEMENT": ("การเคลื่อนไหวสต็อก", ["MOVEMENT_ID","PART_ID","SUPPLIER_ID","MOVEMENT_TYPE","MOVEMENT_QTY","MOVEMENT_DATE"])
}

# Fields: (column_name, label, required, field_type, options)
# field_type: 'text' | 'date' | 'number' | 'decimal' | 'select'
# options: list of values for select, or None
FORMS = {
    "CUSTOMER": [
        ("CUSTOMER_ID", "รหัสลูกค้า", True, "text", None),
        ("CUS_NAME", "ชื่อลูกค้า", True, "text", None),
        ("CUS_HOUSE_NO", "บ้านเลขที่", True, "text", None),
        ("CUS_STREET", "ถนน", False, "text", None),
        ("CUS_SUBDISTRICT", "ตำบล/แขวง", False, "text", None),
        ("CUS_DISTRICT", "อำเภอ/เขต", False, "text", None),
        ("CUS_PROVINCE", "จังหวัด", False, "text", None),
        ("CUS_POSTCODE", "รหัสไปรษณีย์", False, "text", None),
        ("CUS_PHONE", "เบอร์โทร", False, "text", None),
    ],
    "DEVICE": [
        ("DEVICE_ID", "รหัสอุปกรณ์", True, "text", None),
        ("CUSTOMER_ID", "รหัสลูกค้า", True, "text", None),
        ("DEVICE_TYPE", "ประเภทอุปกรณ์", True, "text", None),
        ("BRAND", "ยี่ห้อ", True, "text", None),
        ("MODEL", "รุ่น", False, "text", None),
    ],
    "TECHNICIAN": [
        ("TECH_ID", "รหัสช่าง", True, "text", None),
        ("TECH_NAME", "ชื่อช่าง", True, "text", None),
        ("TECH_SPECIALTY", "ความถนัด", False, "text", None),
    ],
    "SYMPTOM": [
        ("SYMPTOM_ID", "รหัสอาการ", True, "text", None),
        ("SYMPTOM_NAME", "ชื่ออาการเสีย", True, "text", None),
    ],
    "SPARE_PART": [
        ("PART_ID", "รหัสอะไหล่", True, "text", None),
        ("PART_NAME", "ชื่ออะไหล่", True, "text", None),
        ("PART_PRICE", "ราคา", True, "decimal", None),
        ("STOCK_QTY", "จำนวนคงเหลือ", True, "number", None),
    ],
    "SUPPLIER": [
        ("SUPPLIER_ID", "รหัสผู้จำหน่าย", True, "text", None),
        ("SUPPLIER_NAME", "ชื่อผู้จำหน่าย", True, "text", None),
        ("SUPPLIER_PHONE", "เบอร์โทร", False, "text", None),
    ],
    "REPAIR_ORDER": [
        ("ORDER_ID", "เลขที่งานซ่อม", True, "text", None),
        ("DEVICE_ID", "รหัสอุปกรณ์", True, "text", None),
        ("TECH_ID", "รหัสช่าง", True, "text", None),
        ("DATE_RECEIVED", "วันที่รับ", True, "date", None),
        ("DATE_COMPLETED", "วันที่เสร็จ", False, "date", None),
        ("LABOR_COST", "ค่าแรง", True, "decimal", None),
    ],
    "REPAIR_SYMPTOM": [
        ("ORDER_ID", "เลขที่งานซ่อม", True, "text", None),
        ("SYMPTOM_ID", "รหัสอาการ", True, "text", None),
    ],
    "REPAIR_PART_USED": [
        ("ORDER_ID", "เลขที่งานซ่อม", True, "text", None),
        ("PART_ID", "รหัสอะไหล่", True, "text", None),
        ("QTY_USED", "จำนวนที่ใช้", True, "number", None),
    ],
    "PAYMENT": [
        ("PAYMENT_ID", "รหัสการชำระ", True, "text", None),
        ("ORDER_ID", "เลขที่งานซ่อม", True, "text", None),
        ("PAYMENT_METHOD", "วิธีชำระ", True, "select", ["เงินสด", "โอนเงิน", "พร้อมเพย์", "บัตรเครดิต"]),
        ("PAYMENT_AMOUNT", "จำนวนเงิน", True, "decimal", None),
        ("PAYMENT_STATUS", "สถานะ", True, "select", ["รอชำระ", "ชำระแล้ว", "ยกเลิก"]),
        ("PAYMENT_DATE", "วันที่ชำระ", False, "date", None),
    ],
    "STOCK_MOVEMENT": [
        ("MOVEMENT_ID", "รหัสรายการ", True, "text", None),
        ("PART_ID", "รหัสอะไหล่", True, "text", None),
        ("SUPPLIER_ID", "รหัสผู้จำหน่าย (เว้นว่างเมื่อเบิกใช้)", False, "text", None),
        ("MOVEMENT_TYPE", "ประเภท", True, "select", ["รับเข้า", "เบิกใช้"]),
        ("MOVEMENT_QTY", "จำนวน", True, "number", None),
        ("MOVEMENT_DATE", "วันที่", True, "date", None),
    ],
}

# Primary keys for each table (used for edit/delete)
PRIMARY_KEYS = {
    "CUSTOMER": ["CUSTOMER_ID"],
    "DEVICE": ["DEVICE_ID"],
    "TECHNICIAN": ["TECH_ID"],
    "SYMPTOM": ["SYMPTOM_ID"],
    "SPARE_PART": ["PART_ID"],
    "SUPPLIER": ["SUPPLIER_ID"],
    "REPAIR_ORDER": ["ORDER_ID"],
    "REPAIR_SYMPTOM": ["ORDER_ID", "SYMPTOM_ID"],
    "REPAIR_PART_USED": ["ORDER_ID", "PART_ID"],
    "PAYMENT": ["PAYMENT_ID"],
    "STOCK_MOVEMENT": ["MOVEMENT_ID"],
}

def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con

def init_db():
    if os.path.exists(DB): return
    con = sqlite3.connect(DB)
    con.executescript(open("schema.sql", encoding="utf-8").read())
    con.executescript(open("seed.sql", encoding="utf-8").read())
    con.commit(); con.close()

@app.route("/")
def index():
    con = db()
    counts = {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in TABLES}
    con.close()
    return render_template("index.html", tables=TABLES, counts=counts)

@app.route("/table/<table>")
def table_view(table):
    if table not in TABLES: return "ไม่พบตาราง", 404
    con = db()
    rows = con.execute(f"SELECT * FROM {table}").fetchall()
    con.close()
    pks = PRIMARY_KEYS.get(table, [])
    return render_template("table.html", table=table, title=TABLES[table][0],
                           columns=TABLES[table][1], rows=rows, pks=pks)

@app.route("/add/<table>", methods=["GET", "POST"])
def add(table):
    if table not in FORMS: return "ไม่พบแบบฟอร์ม", 404
    fields = FORMS[table]
    if request.method == "POST":
        vals = [request.form.get(k, "").strip() or None for k, *_ in fields]
        try:
            con = db()
            cols = ",".join(k for k, *_ in fields)
            marks = ",".join(["?"] * len(fields))
            con.execute(f"INSERT INTO {table} ({cols}) VALUES ({marks})", vals)
            # Auto-update stock when a STOCK_MOVEMENT is added
            if table == "STOCK_MOVEMENT":
                part = request.form.get("PART_ID")
                qty = int(request.form.get("MOVEMENT_QTY") or 0)
                typ = request.form.get("MOVEMENT_TYPE")
                delta = qty if typ == "รับเข้า" else -qty
                if delta < 0:
                    stock = con.execute("SELECT STOCK_QTY FROM SPARE_PART WHERE PART_ID=?", (part,)).fetchone()
                    if not stock or stock[0] < qty:
                        raise ValueError("สต็อกไม่พอสำหรับการเบิกใช้")
                con.execute("UPDATE SPARE_PART SET STOCK_QTY=STOCK_QTY+? WHERE PART_ID=?", (delta, part))
            con.commit(); con.close()
            flash("เพิ่มข้อมูลเรียบร้อยแล้ว", "ok")
            return redirect(url_for("table_view", table=table))
        except Exception as e:
            if 'con' in locals(): con.rollback(); con.close()
            flash("เพิ่มข้อมูลไม่สำเร็จ: " + str(e), "error")
    return render_template("form.html", table=table, title=TABLES[table][0],
                           fields=fields, mode="add", row=None, pks=PRIMARY_KEYS.get(table, []))

@app.route("/edit/<table>/<path:pk_vals>", methods=["GET", "POST"])
def edit(table, pk_vals):
    if table not in FORMS: return "ไม่พบแบบฟอร์ม", 404
    fields = FORMS[table]
    pks = PRIMARY_KEYS.get(table, [])
    pk_list = pk_vals.split("/")
    if len(pk_list) != len(pks):
        return "รหัสไม่ถูกต้อง", 400

    where_clause = " AND ".join(f"{pk}=?" for pk in pks)

    if request.method == "POST":
        vals = [request.form.get(k, "").strip() or None for k, *_ in fields]
        vals_with_pk = vals + pk_list
        try:
            con = db()
            set_clause = ",".join(f"{k}=?" for k, *_ in fields)
            con.execute(f"UPDATE {table} SET {set_clause} WHERE {where_clause}", vals_with_pk)
            con.commit(); con.close()
            flash("แก้ไขข้อมูลเรียบร้อยแล้ว", "ok")
            return redirect(url_for("table_view", table=table))
        except Exception as e:
            if 'con' in locals(): con.rollback(); con.close()
            flash("แก้ไขข้อมูลไม่สำเร็จ: " + str(e), "error")

    con = db()
    row = con.execute(f"SELECT * FROM {table} WHERE {where_clause}", pk_list).fetchone()
    con.close()
    if not row: return "ไม่พบข้อมูล", 404
    return render_template("form.html", table=table, title=TABLES[table][0],
                           fields=fields, mode="edit", row=row, pks=PRIMARY_KEYS.get(table, []))

@app.route("/delete/<table>/<path:pk_vals>", methods=["POST"])
def delete(table, pk_vals):
    if table not in TABLES: return "ไม่พบตาราง", 404
    pks = PRIMARY_KEYS.get(table, [])
    pk_list = pk_vals.split("/")
    if len(pk_list) != len(pks):
        return "รหัสไม่ถูกต้อง", 400
    where_clause = " AND ".join(f"{pk}=?" for pk in pks)
    try:
        con = db()
        # Reverse stock update if deleting a STOCK_MOVEMENT
        if table == "STOCK_MOVEMENT":
            mov = con.execute(f"SELECT * FROM STOCK_MOVEMENT WHERE {where_clause}", pk_list).fetchone()
            if mov:
                delta = mov["MOVEMENT_QTY"] if mov["MOVEMENT_TYPE"] == "รับเข้า" else -mov["MOVEMENT_QTY"]
                con.execute("UPDATE SPARE_PART SET STOCK_QTY=STOCK_QTY-? WHERE PART_ID=?",
                            (delta, mov["PART_ID"]))
        con.execute(f"DELETE FROM {table} WHERE {where_clause}", pk_list)
        con.commit(); con.close()
        flash("ลบข้อมูลเรียบร้อยแล้ว", "ok")
    except Exception as e:
        if 'con' in locals(): con.rollback(); con.close()
        flash("ลบข้อมูลไม่สำเร็จ: " + str(e), "error")
    return redirect(url_for("table_view", table=table))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
