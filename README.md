# ระบบจัดการร้านซ่อมอุปกรณ์อิเล็กทรอนิกส์และเครื่องใช้ไฟฟ้า

Local Web Application สำหรับงานฐานข้อมูล โดยใช้ **Python + Flask + SQLite**

## วิธีใช้งาน

1. ติดตั้ง Python 3.10 ขึ้นไป
2. เปิด Terminal ในโฟลเดอร์โปรเจกต์
3. สร้าง virtual environment

```bash
python -m venv .venv
```

Windows:
```bash
.venv\Scripts\activate
```

4. ติดตั้ง Flask

```bash
pip install -r requirements.txt
```

5. เริ่มระบบ

```bash
python app.py
```

6. เปิดเบราว์เซอร์ไปที่ `http://127.0.0.1:5000`

## ไฟล์สำคัญ

- `app.py` โปรแกรม Flask
- `database.db` ฐานข้อมูล SQLite ที่ใช้งานจริง
- `schema.sql` โครงสร้าง 11 ตาราง
- `seed.sql` ข้อมูลตัวอย่าง
- `templates/` หน้าเว็บ
- `static/style.css` CSS แบบง่าย

ข้อมูลจะถูกเก็บใน `database.db` และยังคงอยู่หลังปิด/เปิดโปรแกรมใหม่
