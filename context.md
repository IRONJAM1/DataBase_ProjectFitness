# บันทึกรายละเอียดการปรับปรุงระบบ (context.md)
**โครงงานวิชา Database: ระบบฟิตเนส (Fitness Management System)**

---

## 1. ภาพรวมการเปลี่ยนแปลง (Overview)
การปรับปรุงโค้ดเทมเพลตในครั้งนี้มีวัตถุประสงค์เพื่อ:
1. เชื่อมโยงและปรับปรุงระบบให้สอดคล้องกับ `schema.sql` ฉบับปรับปรุงใหม่
2. ขยายความสามารถให้ครอบคลุมทุก Entity หลักในฐานข้อมูล โดยการเพิ่มแท็บ **เทรนเนอร์ (`trainers`)** และ **อุปกรณ์ (`equipment`)** เข้าสู่ระบบ
3. รักษาโครงสร้างสถาปัตยกรรมเดิม 100% (Vanilla JS Frontend + Flask REST API + MySQL Connector) ไม่รื้อโครงสร้าง UI หรือตัวแปรอ็อบเจกต์เดิมของอาจารย์

### กฎเหล็กด้านความปลอดภัย (Database Safety)
- **Parameterized Query (%s) 100%:** คำสั่ง SQL ทุกคำสั่งที่มีการรับค่าพารามิเตอร์จากผู้ใช้ **ต้องใช้ `%s` เป็น Placeholder เท่านั้น** และส่งค่าผ่าน Tuple/List
- **ห้ามต่อสตริง (No String Concatenation):** ห้ามใช้ f-string (`f"SELECT ... WHERE id = {id}"`), format string หรือเครื่องหมาย `+` ในการต่อสตริงคำสั่ง SQL โดยเด็ดขาด เพื่อป้องกันช่องโหว่ **SQL Injection**

---

## 2. การวิเคราะห์เปรียบเทียบกับ `schema.sql` ฉบับปรับปรุงใหม่

| ตาราง | โครงสร้างและฟิลด์ใน Schema | บทบาทในระบบและการเชื่อมโยง |
| :--- | :--- | :--- |
| **`package`** | `package_id`, `package_name`, `price`, `duration_months` | ตารางแพ็กเกจสมาชิก สำหรับทำ Dropdown ตัวเลือกบนหน้าเว็บ |
| **`member`** | `member_id`, `name`, `gender`, `credit`, `join_date`, `package_id`, `start_datepackage`, `end_datepackage`, `total_point`, `referred_by` | - ยกเลิก `package_type` เดิม<br>- เชื่อมโยง FK `package_id` กับตาราง `package`<br>- เพิ่ม `credit`, `start_datepackage`, `end_datepackage`<br>- มี Self-reference FK `referred_by` ชี้กลับไปที่ `member_id` |
| **`gym_class`** | `class_id`, `trainer_id`, `package_id`, `name`, `room`, `detail_class`, `capacity`, `schedule_time`, `end_time` | - เชื่อมโยง FK `trainer_id` (เทรนเนอร์ผู้สอน)<br>- เชื่อมโยง FK `package_id` (แพ็กเกจขั้นต่ำ)<br>- เพิ่ม `detail_class` และ `end_time` (มีเงื่อนไข `end_time > schedule_time`) |
| **`trainer`** *(แท็บใหม่)* | `trainer_id`, `name`, `specialty`, `phone` | จัดการข้อมูลครูฝึก/เทรนเนอร์ |
| **`equipment`** *(แท็บใหม่)* | `equip_id`, `name`, `zone`, `status`, `total_quantity` | จัดการอุปกรณ์ฟิตเนส โซนใช้งาน สถานะ (`ready`, `broken`, `repair`) และจำนวนทั้งหมด |
| **`booking`** | `booking_id`, `member_id`, `class_id`, `book_date`, `status` | บันทึกการจองคลาสเรียนของสมาชิก |

---

## 3. สรุปรายละเอียดการแก้ไขในแต่ละไฟล์

### ก. ไฟล์ `templates/index.html`
เพิ่มปุ่มแท็บสำหรับเปิดหน้าจัดการ **เทรนเนอร์** และ **อุปกรณ์**:
```html
<div class="tabs">
  <button class="tab active" data-entity="members">สมาชิก</button>
  <button class="tab" data-entity="classes">คลาสเรียน</button>
  <button class="tab" data-entity="trainers">เทรนเนอร์</button>
  <button class="tab" data-entity="equipment">อุปกรณ์</button>
  <button class="tab" data-entity="bookings">การจอง</button>
</div>
```

---

### ข. ไฟล์ `static/app.js` (แก้ไขเฉพาะตัวแปร `ENTITIES`)
1. **แท็บ `members`:**
   - **`search`:** ปรับช่องค้นหา `package_type` เป็น `package_id` แบบ dropdown ดึงผ่าน `/api/packages` ด้วย `optionsFrom`
   - **`form`:** ปรับ `package_type` เป็น `package_id` ด้วย `optionsFrom` พร้อมเพิ่มฟิลด์:
     * `credit` (number)
     * `start_datepackage` (date)
     * `end_datepackage` (date)
     * `referred_by` (number, เว้นว่างได้)

2. **แท็บ `classes`:**
   - **`form`:** เพิ่มฟิลด์ `package_id` (dropdown จาก `/api/packages`), `detail_class` (text), `end_time` (text)

3. **แท็บ `trainers` (เพิ่มใหม่):**
   - **`idKey`:** `trainer_id`
   - **`search`:** ค้นหาด้วย `name` (ชื่อเทรนเนอร์), `specialty` (ความเชี่ยวชาญ)
   - **`form`:** ฟอร์มบันทึก `name`, `specialty`, `phone` (เบอร์โทรศัพท์)

4. **แท็บ `equipment` (เพิ่มใหม่):**
   - **`idKey`:** `equip_id`
   - **`search`:** ค้นหาด้วย `name` (ชื่ออุปกรณ์), `zone` (โซน), `status` (สถานะ: ทั้งหมด/ready/broken/repair)
   - **`form`:** ฟอร์มบันทึก `name`, `zone`, `status` (ready/broken/repair), `total_quantity` (จำนวนทั้งหมด)

---

### ค. ไฟล์ `app.py`
เพิ่ม API Endpoints สำหรับรองรับ Entity ใหม่ตามมาตรฐาน REST API เดิม:
1. **แพ็กเกจ (`package`):**
   - `GET /api/packages` -> `safe(db.list_packages)`
2. **เทรนเนอร์ (`trainer`):**
   - `GET /api/trainers` -> ค้นหาเทรนเนอร์ตามฟิลเตอร์
   - `GET /api/trainers/<int:_id>` -> ดึงข้อมูลเทรนเนอร์ 1 คน
   - `POST /api/trainers` -> เพิ่มเทรนเนอร์ใหม่
   - `PUT /api/trainers/<int:_id>` -> แก้ไขข้อมูลเทรนเนอร์
   - `DELETE /api/trainers/<int:_id>` -> ลบข้อมูลเทรนเนอร์
3. **อุปกรณ์ (`equipment`):**
   - `GET /api/equipment` -> ค้นหาอุปกรณ์ตามฟิลเตอร์
   - `GET /api/equipment/<int:_id>` -> ดึงข้อมูลอุปกรณ์ 1 ชิ้น
   - `POST /api/equipment` -> เพิ่มอุปกรณ์ใหม่
   - `PUT /api/equipment/<int:_id>` -> แก้ไขข้อมูลอุปกรณ์
   - `DELETE /api/equipment/<int:_id>` -> ลบข้อมูลอุปกรณ์

---

### ง. ไฟล์ `db.py`
คงโครงสร้างเดิมและเพิ่มฟังก์ชันฐานข้อมูลสำหรับ **เทรนเนอร์** และ **อุปกรณ์** พร้อมคอมเมนต์อธิบายหลักการและแนวทางการเขียนคำสั่ง SQL เพื่อให้นิสิตฝึกเขียนเอง:

1. **ฟังก์ชันที่เขียนคำสั่ง SQL พร้อมใช้งาน:**
   - `list_packages()`: คืนค่ารายการแพ็กเกจทั้งหมดสำหรับ Dropdown บนหน้าเว็บ
2. **ฟังก์ชันสำหรับเทรนเนอร์ (`trainer`):**
   - `search_trainers(filters)`: แนวทางการค้นหาแบบ Dynamic WHERE กรอง `name` และ `specialty` ด้วย `LIKE %s`
   - `get_trainer(trainer_id)`: ดึงข้อมูลเทรนเนอร์ด้วย `WHERE trainer_id = %s`
   - `create_trainer(data)`: ตัวอย่าง `INSERT INTO trainer (name, specialty, phone) VALUES (%s, %s, %s)`
   - `update_trainer(trainer_id, data)`: ตัวอย่าง `UPDATE trainer SET ... WHERE trainer_id = %s`
   - `delete_trainer(trainer_id)`: คำสั่ง `DELETE FROM trainer WHERE trainer_id = %s`
3. **ฟังก์ชันสำหรับอุปกรณ์ (`equipment`):**
   - `search_equipment(filters)`: ค้นหาตาม `name LIKE %s`, `zone LIKE %s`, `status = %s`
   - `get_equipment(equip_id)`: ดึงข้อมูลอุปกรณ์ด้วย `WHERE equip_id = %s`
   - `create_equipment(data)`: ตัวอย่าง `INSERT INTO equipment (name, zone, status, total_quantity) VALUES (%s, %s, %s, %s)`
   - `update_equipment(equip_id, data)`: ตัวอย่าง `UPDATE equipment SET ... WHERE equip_id = %s`
   - `delete_equipment(equip_id)`: คำสั่ง `DELETE FROM equipment WHERE equip_id = %s`

---

## 4. แนวทางการฝึกเขียนคำสั่ง SQL ใน `db.py` สำหรับนิสิต

### ตัวอย่างที่ 1: การเขียน Dynamic Search ใน `search_trainers`
```python
def search_trainers(filters):
    sql = "SELECT * FROM trainer WHERE 1=1"
    params = []
    
    if filters.get("name"):
        sql += " AND name LIKE %s"
        params.append(f"%{filters['name']}%")
        
    if filters.get("specialty"):
        sql += " AND specialty LIKE %s"
        params.append(f"%{filters['specialty']}%")
        
    return run_query(sql, tuple(params))
```

### ตัวอย่างที่ 2: การเขียน Dynamic Search ใน `search_equipment`
```python
def search_equipment(filters):
    sql = "SELECT * FROM equipment WHERE 1=1"
    params = []
    
    if filters.get("name"):
        sql += " AND name LIKE %s"
        params.append(f"%{filters['name']}%")
        
    if filters.get("zone"):
        sql += " AND zone LIKE %s"
        params.append(f"%{filters['zone']}%")
        
    if filters.get("status"):
        sql += " AND status = %s"
        params.append(filters["status"])
        
    return run_query(sql, tuple(params))
```

### ตัวอย่างที่ 3: การเพิ่มข้อมูลอุปกรณ์พร้อมตรวจสอบค่าเริ่มต้น
```python
def create_equipment(data):
    sql = """
        INSERT INTO equipment (name, zone, status, total_quantity)
        VALUES (%s, %s, %s, %s)
    """
    params = (
        data["name"],
        data["zone"],
        data.get("status", "ready"),
        int(data.get("total_quantity") or 0)
    )
    return run_command(sql, params)
```

---

## 5. การตรวจสอบความถูกต้อง (Verification Checklist)
- [x] หน้าเว็บ `index.html` มีปุ่มแท็บครบถ้วนทั้ง 5 แท็บ: สมาชิก, คลาสเรียน, เทรนเนอร์, อุปกรณ์, การจอง
- [x] ตัวแปร `ENTITIES` ใน `static/app.js` รองรับโครงสร้างข้อมูลของ `trainers` และ `equipment`
- [x] ไฟล์ `app.py` มี API routes ครบถ้วนตามมาตรฐาน REST API
- [x] ไฟล์ `db.py` มีฟังก์ชันครบถ้วนพร้อมคำอธิบายหลักการ Parameterized Query (`%s`) สำหรับฝึกเขียน
- [x] ไวยากรณ์ภาษา Python ในทุกไฟล์ผ่านการตรวจสอบด้วย `py_compile` ไม่มีข้อผิดพลาด
