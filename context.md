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
- [x] ฟอร์มคลาสเรียนใน `app.js` ปรับ `trainer_id` เป็น dropdown ดึงจาก `/api/trainers`
- [x] ฟอร์มคลาสเรียนใน `app.js` ปรับช่องเวลาเริ่มและเวลาสิ้นสุดเป็น `datetime-local` มีปุ่มเลือกวัน-เวลา

---

## 6. การปรับปรุง UI ฟอร์มคลาสเรียนล่าสุด (Classes Form Improvements)
- **ช่องเทรนเนอร์ (`trainer_id`):** ปรับจากช่องพิมพ์ตัวเลข (`number`) เป็น Dropdown (`select`) ดึงรายชื่อเทรนเนอร์ผ่าน API `/api/trainers` (แสดงชื่อ `name` แต่ส่งค่าเป็น `trainer_id`)
- **ช่องเวลาเริ่มและสิ้นสุด (`schedule_time`, `end_time`):** ปรับจาก `text` เป็น `datetime-local` ทำให้มีตัวเลือกปฏิทินและเวลา (Date-Time Picker) ให้กดเลือกได้ทันที สะดวกและลดข้อผิดพลาดในการพิมพ์รูปแบบวันเวลา

---

## 7. การแก้ไข Dropdown โซนของอุปกรณ์ (Equipment Zone Dropdown Fix)
- **ปัญหาเดิม:** ดึงจาก `/api/equipment` โดยใช้ `"value": "equip_id"` ทำให้:
  1. ชื่อโซนซ้ำตามจำนวนอุปกรณ์ในแต่ละโซน
  2. เมื่อเลือกโซน ระบบส่งค่า `equip_id` (เช่น `1`, `2`) ไปค้นหาแทนที่จะเป็นชื่อโซน (`Studio A`) ทำให้ `WHERE zone = %s` หาไม่เจอ
- **การแก้ไข:**
  1. เพิ่มฟังก์ชัน `list_zones()` ใน `db.py`: ใช้ `SELECT DISTINCT zone FROM equipment ORDER BY zone` เพื่อตัดค่าซ้ำ
  2. เพิ่ม Endpoint `GET /api/zones` ใน `app.py`
  3. ปรับใน `static/app.js`: ดึงจาก `/api/zones` โดยกำหนด `"value": "zone"` และ `"label": "zone"`

---

## 8. การเพิ่มแท็บ การยืมอุปกรณ์ (class_equipment)
- **ตำแหน่ง:** เรียงต่อจากแท็บ **อุปกรณ์** (สมาชิก -> คลาสเรียน -> เทรนเนอร์ -> อุปกรณ์ -> **การยืมอุปกรณ์** -> การจอง)
- **ฐานข้อมูล:** เชื่อมโยงกับตาราง `class_equipment` (ความสัมพันธ์ M:N ระหว่าง `gym_class` และ `equipment`)
- **การจัดการ Composite Primary Key:**
  - `class_equipment` มี PK ร่วมกัน 2 ตัวคือ `(class_id, equip_id)`
  - ในฟังก์ชัน `search_class_equipment` ทำการสร้าง id เสมือน: `(ce.class_id * 100000 + ce.equip_id) AS id` เพื่อให้เข้ากันได้กับระบบ UI หน้าบ้าน 100% โดยไม่ต้องแก้ฟังก์ชัน JavaScript หลัก
  - ในฟังก์ชัน `get_class_equipment`, `update_class_equipment`, และ `delete_class_equipment` สามารถถอดรหัส:
    * `class_id = id // 100000`
    * `equip_id = id % 100000`
- **ฟอร์มและ Dropdown:**
  - ช่อง "คลาสเรียน": Dropdown ดึงรายชื่อคลาสจาก `/api/classes`
  - ช่อง "อุปกรณ์": Dropdown ดึงรายชื่ออุปกรณ์จาก `/api/equipment`
  - ช่อง "จำนวน": กรอกจำนวนที่ใช้/ยืม

---

## 9. การแก้ไขปัญหาการแก้ไขข้อมูลการจอง (Booking Edit Fix)
- **ปัญหา:** เมื่อกดปุ่ม "แก้ไข" ในแท็บการจองแล้วไม่มีหน้าต่างขึ้นมา เกิดจากใน `search_bookings` มีการตั้ง alias `b.booking_id as 'Booking ID'` ทำให้ชื่อฟิลด์ไม่ตรงกับ `"idKey": "booking_id"` ใน `static/app.js` ค่า ID จึงกลายเป็น `undefined` และส่งไปที่ `/api/bookings/undefined` (404 Not Found)
- **การแก้ไข:**
  1. ใน `search_bookings`: เปลี่ยนจาก `b.booking_id as 'Booking ID'` เป็น `b.booking_id`
  2. ใน `create_booking`: แก้ไขการอ่านค่า `data["status "]` (มี space) ให้เป็น `data["status"]` เพื่อป้องกัน KeyError

---

## 10. การจัดการ Duplicate Entry ในตาราง class_equipment
- **ปัญหา:** เมื่อผู้ใช้กด "เพิ่มข้อมูลใหม่" โดยเลือกคลาสและอุปกรณ์ที่เคยมีอยู่ในระบบแล้ว MySQL จะฟ้อง `IntegrityError: 1062: Duplicate entry for key 'class_equipment.PRIMARY'` เนื่องจากละเมิดกฎ Primary Key `(class_id, equip_id)`
- **การแก้ไข:**
  1. ใน `create_class_equipment`: เพิ่มการตรวจสอบว่าคู่นี้มีอยู่ในฐานข้อมูลหรือยัง หากมีอยู่แล้ว ให้ `raise ValueError("คลาสนี้มีการยืมอุปกรณ์ชนิดนี้อยู่แล้ว...")` เพื่อแสดงข้อความแจ้งเตือนภาษาไทยที่เข้าใจง่ายบนหน้าเว็บ
  2. ใน `update_class_equipment`: เพิ่มการตรวจสอบกรณีเปลี่ยนคู่คลาสและอุปกรณ์ไปซ้ำกับแถวอื่นที่มีอยู่แล้ว

---

## 11. การคำนวณคะแนนสะสม (Referral Points) เมื่อเพิ่มสมาชิกใหม่
- **ปัญหาเดิม:** มีการเขียนไวยากรณ์ `data.get["referred_by"]` (ใช้วงเล็บเหลี่ยมแทนวงเล็บกลม) ทำให้เกิด `TypeError: 'builtin_function_or_method' object is not subscriptable`
- **การปรับปรุง:**
  1. แยกฟังก์ชัน `add_point(member_id, points=10)` สำหรับ UPDATE คะแนน `total_point = total_point + %s`
  2. ใน `create_member`: บันทึกข้อมูลสมาชิกใหม่ให้สำเร็จก่อน (`run_command`) จากนั้นตรวจเช็คว่า `referred_by` มีค่าหรือไม่ หากมีจึงทำการเรียก `add_point(ref_id, 10)` เพื่อความถูกต้องของ Business Logic

---

## 12. การป้องกันการบวกแต้มซ้ำตอนแก้ไขสมาชิก (Prevent Duplicate Referral Points on Update)
- **ปัญหา:** ตอนกดแก้ไขสมาชิก แม้รหัสผู้แนะนำ (`referred_by`) จะเป็นคนเดิม แต่แต้มยังถูกบวกเพิ่ม 10 คะแนนทุกครั้ง เกิดจาก **Type Mismatch** ใน Python โดยค่าเดิมจากฐานข้อมูลเป็น `int` (เช่น `1`) แต่ค่าใหม่จากฟอร์มหน้าเว็บเป็น `str` (เช่น `"1"`) ซึ่ง `"1" != 1` ใน Python มีค่าเป็น `True` เสมอ
- **การแก้ไข:**
  - แปลงค่าทั้งสองฝั่งเป็น `int` (หรือ `None`) ให้เป็น Type เดียวกันก่อนเปรียบเทียบ:
    `old_ref_id = int(...) if ... else None`
    `new_ref_id = int(...) if ... else None`
  - ตรวจเช็คเงื่อนไข `if new_ref_id and new_ref_id != old_ref_id:` ทำให้แต้มจะถูกเพิ่มก็ต่อเมื่อมีการระบุผู้แนะนำใหม่ที่ไม่ใช่คนเดิมเท่านั้น

---

## 13. การคำนวณวันหมดอายุแพ็กเกจอัตโนมัติ และการตัดเครดิตตามจริง (Package Calculation & Credit Deduction)
- **ความต้องการ:**
  1. การสมัครแพ็กเกจ ให้ผู้ใช้กรอกเฉพาะ **วันเริ่มแพ็กเกจ (`start_datepackage`)** เท่านั้น และให้ระบบคำนวณ **วันหมดอายุแพ็กเกจ (`end_datepackage`)** ตามจำนวนเดือนจริง (`duration_months`) ของแพ็กเกจนั้นๆ โดยอัตโนมัติ
  2. การคำนวณเครดิต (`credit`): ต้องตรวจสอบว่าเครดิตที่กรอกมาเพียงพอต่อราคาแพ็กเกจ (`price`) หรือไม่ หากเพียงพอให้หักค่าแพ็กเกจออกจากเครดิตและบันทึกยอดคงเหลือลงฐานข้อมูลจริง หากไม่พอให้แจ้งเตือนข้อผิดพลาด
- **การแก้ไข:**
  1. **หน้าเว็บ (`static/app.js`):**
     - นำฟิลด์ `end_datepackage` ออกจากฟอร์มกรอกข้อมูลสมาชิก (`ENTITIES.members.form`) เพื่อให้ผู้ใช้กรอกเฉพาะวันเริ่ม ส่วนในตารางค้นหายังคงแสดงวันหมดอายุตามปกติ
  2. **ฐานข้อมูล (`db.py`):**
     - เพิ่มฟังก์ชัน `get_package(package_id)`: ดึงข้อมูลแพ็กเกจ (ราคา `price` และระยะเวลา `duration_months`)
     - เพิ่มฟังก์ชัน `calculate_package_end_date(start_date, duration_months)`: ใช้คำสั่ง SQL ฟังก์ชัน `DATE_SUB(DATE_ADD(%s, INTERVAL %s MONTH), INTERVAL 1 DAY)` ซึ่งคำนวณวันสิ้นสุดตามเดือนจริงและจัดการเรื่องวันสิ้นเดือน/ปีอธิกสุรทินได้อย่างแม่นยำ (ตรงตามข้อมูลตัวอย่างใน `schema.sql`)
     - ปรับปรุง `create_member(data)`:
       - หากมีการเลือกแพ็กเกจ: ตรวจสอบว่า `credit >= price` หรือไม่ หากไม่พอให้ `raise ValueError` แจ้งเตือนภาษาไทย หากพอให้หักลบ `credit = credit - price`
       - หากไม่ได้ใส่วันเริ่มแพ็กเกจ ให้ใช้วันที่สมัคร (`join_date`) อัตโนมัติ แล้วคำนวณ `end_datepackage` บันทึกลงตาราง
     - ปรับปรุง `update_member(member_id, data)`:
       - หากมีการเปลี่ยนแพ็กเกจใหม่: ตรวจสอบเครดิตและหักราคาแพ็กเกจใหม่ พร้อมคำนวณวันหมดอายุใหม่
       - หากเป็นแพ็กเกจเดิมแต่มีการปรับเปลี่ยนวันเริ่มแพ็กเกจ: คำนวณวันหมดอายุใหม่ให้อัตโนมัติโดยไม่หักเครดิตซ้ำ

---

## 14. การนำแต้มสะสม (total_point) มาช่วยลดราคาแพ็กเกจเมื่อเปลี่ยนแพ็กเกจ (Point Discount: point * 10)
- **ความต้องการ:**
  - เมื่อสมาชิกกดแก้ไขข้อมูลและทำการเปลี่ยนแพ็กเกจ (`new_pkg_id != old_pkg_id`) ต้องการให้นำแต้มสะสมปัจจุบันของสมาชิกมาช่วยลดราคาแพ็กเกจ โดยคิดอัตรา `ส่วนลด = point * 10` บาท
- **การแก้ไขใน `update_member` ([`db.py`](file:///c:/Users/ssopp/Documents/freespace/database/DataBase_ProjectFitness/db.py)):**
  1. ดึงแต้มสะสมปัจจุบันของสมาชิก: `current_points = int(old_member.get("total_point") or 0)`
  2. คำนวณส่วนลด: `discount = current_points * 10`
  3. คำนวณราคาที่ต้องจ่ายจริง: `final_price = max(0.0, raw_price - discount)`
  4. หักแต้มที่นำไปใช้:
     - หากส่วนลดครอบคลุมราคาแพ็กเกจทั้งหมด (`discount >= raw_price`): แต้มที่ใช้คือ `math.ceil(raw_price / 10)` และแต้มที่เหลือจะถูกเก็บไว้ `current_points -= used_points`
     - หากใช้แต้มทั้งหมด (`discount < raw_price`): แต้มจะถูกใช้จนหมด `current_points = 0`
  5. ตรวจสอบเครดิต: หากเครดิตไม่พอกับ `final_price` จะแจ้งเตือนราคาปกติและราคาหลังหักส่วนลดด้วยแต้ม
  6. คำสั่ง SQL `UPDATE member`: เพิ่มการบันทึก `total_point = %s` เพื่ออัปเดตแต้มคงเหลือลงฐานข้อมูลจริง

---

## 15. การสร้างและใช้งาน Database Views สำหรับ Dashboard และ Reports
- **แนวคิดและวัตถุประสงค์ (Why Views?):**
  - **Encapsulation & Security:** ซ่อนความซับซ้อนของคำสั่ง SQL (Multi-table JOINs, Subqueries, Aggregations) ไว้ที่ระดับฐานข้อมูล ทำให้ Application Layer (Python/Flask) เรียกใช้งานได้ง่ายด้วยคำสั่งสั้นๆ เพียง `SELECT * FROM view_name`
  - **Maintainability & Reusability:** หากต้องการปรับเปลี่ยนตรรกะหรือฟิลด์ในรายงาน สามารถแก้ไขที่นิยามของ View ได้ทันทีโดยไม่ต้องรื้อโค้ดใน Backend
  - **Performance:** Database Server สามารถ Optimization แผนการ Query ล่วงหน้าได้
- **รายการ Views ที่สร้างขึ้นใน `schema.sql` และนำไปใช้ใน `db.py`:**
  1. **`view_report_summary`:** สรุปภาพรวมบนการ์ด Dashboard 6 ใบ (สมาชิก, คลาส, เทรนเนอร์, การจองที่สำเร็จ, package ยอดฮิต, รายได้รวม)
  2. **`view_popular_classes`:** 5 อันดับคลาสยอดนิยมที่มีการจองสถานะ `booked` มากที่สุด (JOIN 3 ตาราง: `gym_class`, `booking`, `trainer` + `GROUP BY` + `ORDER BY COUNT DESC LIMIT 5`)
  3. **`view_trainers_above_avg`:** เทรนเนอร์ที่มีจำนวนการจองสูงกว่าค่าเฉลี่ยของเทรนเนอร์ทุกคน (JOIN 3 ตาราง + `GROUP BY trainer` + กรองด้วย `HAVING COUNT > (ยอดจองทั้งหมด / จำนวนเทรนเนอร์ทั้งหมด)` ซึ่งอ่านเข้าใจง่ายและไม่ซับซ้อน)
  4. **`view_class_equipment`:** รายละเอียดอุปกรณ์ที่แต่ละคลาสเรียนยืม/ใช้งาน (JOIN 3 ตาราง: `class_equipment`, `gym_class`, `equipment`)
- **การเชื่อมต่อใน Python (`db.py`):**
  - ฟังก์ชัน `report_summary()` คืนค่าแถวแรกของ `view_report_summary`
  - ฟังก์ชัน `report_popular_classes()`, `report_trainers_above_avg()`, และ `report_class_equipment()` รัน `SELECT * FROM view_xxx` และคืนผลลัพธ์เป็นรายการสำหรับแสดงผลบนหน้า `/report` อัตโนมัติ

---

## 16. การตรวจสอบและคำนวณวันเวลาจริงในการจองคลาสเรียน (Booking Date & Time Constraints)
- **ปัญหาเดิม:** ระบบตรวจเช็คเพียงความจุของคลาส (`capacity`) และการจองซ้ำคลาสเดิม แต่ยังไม่ได้คำนวณความถูกต้องของวันและเวลาตามคลาสจริง
- **การปรับปรุงฟังก์ชัน `check_can_book` ([`db.py`](file:///c:/Users/ssopp/Documents/freespace/database/DataBase_ProjectFitness/db.py)):**
  1. **ตรวจสอบเวลาการจอง (Booking Date vs Schedule Time):**
     - วันเวลาที่กดจอง (`book_date`) ต้องไม่เกินเวลาเริ่มเรียนของคลาส (`schedule_time`) เพื่อป้องกันการจองย้อนหลัง
  2. **ตรวจสอบอายุแพ็กเกจของสมาชิก (Package Validity on Class Date):**
     - สมาชิกต้องมีแพ็กเกจที่ยังไม่หมดอายุ
     - วันที่จัดคลาสเรียน (`class_date`) ต้องอยู่ภายในช่วงวันที่สมาชิกได้รับสิทธิ์: `start_datepackage <= class_date <= end_datepackage`
     - หากแพ็กเกจยังไม่เริ่มใช้งานหรือหมดอายุก่อนวันที่มีคลาส จะไม่อนุญาตให้จอง
  3. **ตรวจสอบเวลาเรียนซ้อนทับกัน (No Overlapping Class Time):**
     - สมาชิกคนเดียวกัน ห้ามจองคลาสอื่นที่มีช่วงเวลาเรียนทับซ้อนกันในช่วงวันและเวลาเดียวกัน
     - ตรวจสอบด้วยเงื่อนไข SQL Overlapping Range: `c.schedule_time < new_end_time AND c.end_time > new_start_time`
  4. **การตรวจสอบเดิมที่ยังคงทำงานควบคู่กัน:**
     - ตรวจสอบการจองซ้ำคลาสเดิม (Prevent Duplicate Booking)
     - ตรวจสอบที่นั่งว่าง (`capacity - booked_count > 0`)
  - ส่งผ่านพารามิเตอร์ `booking_id` (เพื่อไม่ให้นับตัวเองตอนกดแก้ไข) และ `book_date` จากทั้ง `create_booking` และ `update_booking`









