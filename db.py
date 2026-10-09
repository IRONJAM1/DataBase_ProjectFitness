# ============================================================
#  db.py — ชั้นติดต่อฐานข้อมูล  ★★★ นิสิตเขียน SQL ในไฟล์นี้ ★★★
#  มองหาคำว่า  # TODO  ทุกฟังก์ชัน — ใช้ %s เป็น placeholder เสมอ (กัน SQL injection)
# ============================================================
import mysql.connector
import config


def get_connection():
    return mysql.connector.connect(
        host=config.DB_HOST, user=config.DB_USER, password=config.DB_PASSWORD,
        database=config.DB_NAME, port=config.DB_PORT)


def run_query(sql, params=None):
    """รัน SELECT คืนผลเป็น list ของ dict"""
    conn = get_connection(); cur = conn.cursor(dictionary=True)
    cur.execute(sql, params or ()); rows = cur.fetchall()
    cur.close(); conn.close(); return rows


def run_command(sql, params=None):
    """รัน INSERT / UPDATE / DELETE แล้ว commit"""
    conn = get_connection(); cur = conn.cursor()
    cur.execute(sql, params or ()); conn.commit()
    out = {"new_id": cur.lastrowid, "affected": cur.rowcount}
    cur.close(); conn.close(); return out


def blank_to_none(value):
    """ช่องที่ไม่ได้กรอกในฟอร์มจะส่งมาเป็น "" — แปลงเป็น None (= NULL ใน SQL)
    ใช้กับคอลัมน์ที่ว่างได้ เช่น return_date, paid_date  เพราะ MySQL ไม่รับ '' เป็น DATE"""
    return None if value in ("", None) else value


def _todo(name):
    raise NotImplementedError(f"TODO: ยังไม่ได้เขียนฟังก์ชัน {name} ใน db.py")


# ---------- แพ็กเกจ (package) ----------
def list_packages():
    """ดึงรายการแพ็กเกจทั้งหมด สำหรับใช้ใน dropdown บนหน้าเว็บ (GET /api/packages)
    หลักการ:
      - ใช้ run_query(sql) เพื่อคืนผลลัพธ์เป็น list ของ dict
      - ต้องมีคอลัมน์ package_id และ package_name เพื่อให้ optionsFrom บนหน้าเว็บนำไปแสดงผลได้
    """
    sql = "SELECT package_id, package_name, price, duration_months FROM package ORDER BY package_id"
    return run_query(sql)


# ---------- สมาชิก (member) ----------
def search_members(filters):
    sql = '''SELECT m.member_id, m.name , m.gender, m.credit, m.join_date,
                         m.package_id, p.package_name, m.start_datepackage,
                         m.end_datepackage, m.total_point, m.referred_by
                  FROM member m
                  LEFT JOIN package p ON m.package_id = p.package_id
                  WHERE 1=1'''
    params = []
    if filters.get("name"):
            sql += " AND m.name like %s"
            params.append("%"+filters['name']+"%")
    if filters.get("gender"):
            sql += " AND m.gender = %s"
            params.append(filters["gender"])
    if filters.get("package_id"):
            sql += " AND p.package_id = %s"
            params.append(filters["package_id"])
    sql += " ORDER BY m.member_id"
    return run_query(sql, params)


def get_member(member_id):
    # TODO: SELECT * FROM member WHERE member_id = %s แล้วคืนแถวเดียว
    sql = "select * from member where member_id = %s"
    rows = run_query(sql, (member_id,))
    return rows[0] if rows else None


def create_member(data):
    sql = '''INSERT INTO member (name, gender, credit, join_date, package_id, start_datepackage, end_datepackage, referred_by)
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'''
    params = (data["name"], data["gender"], float(data.get("credit") or 0),
                  data["join_date"], blank_to_none(data.get("package_id")),
                  blank_to_none(data.get("start_datepackage")),
                  blank_to_none(data.get("end_datepackage")),
                  blank_to_none(data.get("referred_by")))
    return run_command(sql, params)


def update_member(member_id, data):
    sql = """update member
            set name = %s,gender = %s,credit = %s,join_date = %s,package_id = %s,start_datepackage = %s,end_datepackage = %s,referred_by = %s
            where member_id = %s"""
    return run_command(sql,(data["name"],data["gender"],data["credit"],data["join_date"],data["package_id"],data["start_datepackage"],data["end_datepackage"],blank_to_none(data["referred_by"]), member_id))


def delete_member(member_id):
    return run_command("DELETE FROM member WHERE member_id = %s", (member_id,))

# ---------- คลาสเรียน (gym_class) ----------
def search_classes(filters):

    sql = """select 
                c.class_id, 
                c.name, 
                c.detail_class, 
                c.room,
                c.capacity,
                p.package_name,
                c.schedule_time 
            from gym_class c
            left join package p on c.package_id = p.package_id
            where 1=1"""
    params = []
    if filters.get("name"):
        sql += " and c.name like %s"
        params.append("%"+filters['name']+"%")
    if filters.get("room"):
        sql += " and c.room like %s"
        params.append("%"+filters['room']+"%")
    sql += " order by c.class_id"
    return run_query(sql, params)


def get_class(class_id):
    sql = "select * from gym_class where class_id = %s"
    rows = run_query(sql, (class_id,))    
    return rows[0] if rows else None


def create_class(data):
    sql = ''' insert into gym_class (name,trainer_id,room,detail_class,capacity,schedule_time,end_time)
                 VALUES (%s, %s, %s, %s, %s,%s,%s)'''
    params = (data["name"],data["trainer_id"],data["detail_class"],data["room"],data["capacity"],data["schedule_time"],data["end_time"])
    return run_command(sql, params)


def update_class(class_id, data):
    sql = """update gym_class
            set name = %s,trainer_id = %s,room = %s,detail_class = %s,capacity = %s,schedule_time = %s,end_time = %s
            where class_id = %s"""
    return run_command(sql,(data["name"],data["trainer_id"],data["room"],data["detail_class"],data["capacity"],data["schedule_time"],data["end_time"],class_id))


def delete_class(class_id):
   sql = "delete from gym_class where class_id = %s"
   return run_command(sql,(class_id,))

# ---------- เทรนเนอร์ (trainer) ----------
def search_trainers(filters):
    """ค้นหา เทรนเนอร์ ตามเงื่อนไข (name, specialty)
    หลักการและคำใบ้:
      1) เริ่มต้นคำสั่ง SQL:
         sql = "SELECT * FROM trainer WHERE 1=1"
         params = []
      2) ตรวจสอบเงื่อนไขใน filters และต่อเงื่อนไขแบบ Parameterized Query (%s เสมอ):
         - ถ้ามี filters.get("name"):
             sql += " AND name LIKE %s"
             params.append(f"%{filters['name']}%")
         - ถ้ามี filters.get("specialty"):
             sql += " AND specialty LIKE %s"
             params.append(f"%{filters['specialty']}%")
      3) ห้ามต่อสตริงเด็ดขาด (ป้องกัน SQL Injection)
      4) คืนผลลัพธ์ด้วย run_query(sql, tuple(params))"""
    # TODO: เขียน SQL ค้นหาแบบยืดหยุ่นตาม filters (ใช้ %s เสมอ)
    _todo("search_trainers")


def get_trainer(trainer_id):
    """ดึงข้อมูล เทรนเนอร์ 1 รายการตาม trainer_id (ใช้ตอนเปิดฟอร์มแก้ไข)
    หลักการ:
      - sql = "SELECT * FROM trainer WHERE trainer_id = %s"
      - rows = run_query(sql, (trainer_id,))
      - return rows[0] if rows else None"""
    # TODO: SELECT * FROM trainer WHERE trainer_id = %s แล้วคืนแถวเดียว
    _todo("get_trainer")


def create_trainer(data):
    """เพิ่ม เทรนเนอร์ ใหม่ — data มีคีย์: name, specialty, phone
    หลักการและคำใบ้:
      - ใช้ INSERT แบบ Parameterized (%s):
        sql = "INSERT INTO trainer (name, specialty, phone) VALUES (%s, %s, %s)"
        params = (data["name"], data["specialty"], data["phone"])
        return run_command(sql, params)"""
    # TODO: INSERT INTO trainer (...) VALUES (%s, ...)
    _todo("create_trainer")


def update_trainer(trainer_id, data):
    """แก้ไข เทรนเนอร์ ตาม trainer_id
    หลักการและคำใบ้:
      - ใช้ UPDATE แบบ Parameterized (%s):
        sql = "UPDATE trainer SET name=%s, specialty=%s, phone=%s WHERE trainer_id=%s"
        params = (data["name"], data["specialty"], data["phone"], trainer_id)
        return run_command(sql, params)"""
    # TODO: UPDATE trainer SET ... WHERE trainer_id=%s
    _todo("update_trainer")


def delete_trainer(trainer_id):
    """ลบ เทรนเนอร์ ตาม trainer_id
    หลักการ:
      - sql = "DELETE FROM trainer WHERE trainer_id = %s"
      - return run_command(sql, (trainer_id,))
    หมายเหตุ: หากเทรนเนอร์มีคลาสผูกอยู่ (FK restrict) ฐานข้อมูลจะไม่อนุญาตให้ลบ"""
    # TODO: DELETE FROM trainer WHERE trainer_id=%s
    _todo("delete_trainer")


# ---------- อุปกรณ์ (equipment) ----------
def search_equipment(filters):
    """ค้นหา อุปกรณ์ ตามเงื่อนไข (name, zone, status)
    หลักการและคำใบ้:
      1) sql = "SELECT * FROM equipment WHERE 1=1"
         params = []
      2) ตรวจสอบเงื่อนไขใน filters (%s เสมอ):
         - ถ้ามี filters.get("name"):
             sql += " AND name LIKE %s"
             params.append(f"%{filters['name']}%")
         - ถ้ามี filters.get("zone"):
             sql += " AND zone LIKE %s"
             params.append(f"%{filters['zone']}%")
         - ถ้ามี filters.get("status"):
             sql += " AND status = %s"
             params.append(filters["status"])
      3) คืนผลลัพธ์ด้วย run_query(sql, tuple(params))"""
    # TODO: เขียน SQL ค้นหาแบบยืดหยุ่นตาม filters (ใช้ %s เสมอ)
    _todo("search_equipment")


def get_equipment(equip_id):
    """ดึงข้อมูล อุปกรณ์ 1 รายการตาม equip_id (ใช้ตอนเปิดฟอร์มแก้ไข)
    หลักการ:
      - sql = "SELECT * FROM equipment WHERE equip_id = %s"
      - rows = run_query(sql, (equip_id,))
      - return rows[0] if rows else None"""
    # TODO: SELECT * FROM equipment WHERE equip_id = %s แล้วคืนแถวเดียว
    _todo("get_equipment")


def create_equipment(data):
    """เพิ่ม อุปกรณ์ ใหม่ — data มีคีย์: name, zone, status, total_quantity
    หลักการและคำใบ้:
      - ตรวจสอบ status ว่าต้องเป็น 'ready', 'broken', หรือ 'repair' (enum)
      - total_quantity ต้อง >= 0 (check constraint)
      - ใช้ INSERT แบบ Parameterized (%s):
        sql = "INSERT INTO equipment (name, zone, status, total_quantity) VALUES (%s, %s, %s, %s)"
        params = (data["name"], data["zone"], data.get("status", "ready"), int(data.get("total_quantity") or 0))
        return run_command(sql, params)"""
    # TODO: INSERT INTO equipment (...) VALUES (%s, ...)
    _todo("create_equipment")


def update_equipment(equip_id, data):
    """แก้ไข อุปกรณ์ ตาม equip_id
    หลักการและคำใบ้:
      - sql = "UPDATE equipment SET name=%s, zone=%s, status=%s, total_quantity=%s WHERE equip_id=%s"
      - params = (data["name"], data["zone"], data["status"], int(data.get("total_quantity") or 0), equip_id)
      - return run_command(sql, params)"""
    # TODO: UPDATE equipment SET ... WHERE equip_id=%s
    _todo("update_equipment")


def delete_equipment(equip_id):
    """ลบ อุปกรณ์ ตาม equip_id
    หลักการ:
      - sql = "DELETE FROM equipment WHERE equip_id = %s"
      - return run_command(sql, (equip_id,))"""
    # TODO: DELETE FROM equipment WHERE equip_id=%s
    _todo("delete_equipment")


# ---------- การจอง (booking) ----------
def search_bookings(filters):
    """ค้นหา การจอง ตามเงื่อนไข (member_id, class_id, status)
    คำใบ้: เริ่มจาก sql = "SELECT * FROM booking WHERE 1=1"
    แล้วต่อเงื่อนไขเฉพาะ filter ที่มีค่า (ข้อความใช้ LIKE %s, อื่น ๆ ใช้ = %s)"""
    # TODO: เขียน SQL ค้นหาแบบยืดหยุ่นตาม filters (ใช้ %s เสมอ)
    _todo("search_bookings")


def get_booking(booking_id):
    """ดึง การจอง 1 รายการตาม booking_id (ใช้ตอนเปิดฟอร์มแก้ไข)"""
    # TODO: SELECT * FROM booking WHERE booking_id = %s แล้วคืนแถวเดียว
    _todo("get_booking")


def check_can_book(member_id, class_id, booking_id=None):
    """ตรวจก่อนบันทึกการจอง — ถ้าไม่ผ่านให้ raise ValueError("ข้อความ")
    (หน้าเว็บจะแสดงข้อความนั้นเป็น alert ให้ผู้ใช้เห็น และไม่บันทึกข้อมูล)
    1) คลาสต้องมีอยู่จริง และยังมีที่นั่งว่าง (seats_left > 0)
       seats_left = capacity − (SELECT COUNT(*) FROM booking
                                WHERE class_id = %s AND status = 'booked' AND booking_id <> %s)
    2) ห้ามจองซ้ำ: สมาชิกคนนี้มีการจอง 'booked' ในคลาสนี้อยู่แล้ว (ไม่นับแถวตัวเอง)
    ★ ตอนเพิ่มใหม่ booking_id เป็น None → ส่ง 0 แทน (booking_id or 0) จะได้ไม่ตรงกับแถวไหนเลย
    ตัวอย่าง: raise ValueError("คลาสนี้เต็มแล้ว")"""
    # TODO: เขียนการตรวจ 2 ข้อตามคำใบ้
    _todo("check_can_book")


def create_booking(data):
    """เพิ่ม การจอง ใหม่ — data มีคีย์: member_id, class_id, book_date, status
    คำใบ้:
      1) ถ้า status = 'booked' → เรียก check_can_book(data["member_id"], data["class_id"]) ก่อน
      2) INSERT INTO booking (...) VALUES (%s, ...)"""
    # TODO: เขียนตามคำใบ้
    _todo("create_booking")


def update_booking(booking_id, data):
    """แก้ไข การจอง ตาม booking_id
    คำใบ้:
      1) ถ้า status ใหม่ = 'booked' และ (เดิมเคย cancelled หรือเปลี่ยนคลาส/สมาชิก)
         → check_can_book(data["member_id"], data["class_id"], booking_id)
         (ดูค่าเดิมด้วย get_booking — การยกเลิกจองไม่ต้องตรวจ)
      2) UPDATE booking SET ... WHERE booking_id=%s"""
    # TODO: เขียนตามคำใบ้
    _todo("update_booking")


def delete_booking(booking_id):
    """ลบ การจอง ตาม booking_id"""
    # TODO: DELETE FROM booking WHERE booking_id=%s
    _todo("delete_booking")


# ============================================================
#  REPORT (รายงาน — ใช้ JOIN + GROUP BY + subquery)
#  ★ ชื่อคอลัมน์ใน SELECT จะกลายเป็นหัวตารางบนเว็บ — ใช้ AS 'ชื่อภาษาไทย' ได้
# ============================================================
def report_summary():
    """ตัวเลขสรุปบนการ์ด dashboard — คืน dict {ชื่อการ์ด: ตัวเลข}  (1 คีย์ = 1 การ์ด)
    ตอนนี้ยังไม่ได้เขียน SQL → คืนค่า None ทุกการ์ด หน้าเว็บจึงแสดง "—" รอไว้
    ★ งานของนิสิต: เขียน SQL ตามตัวอย่างด้านล่าง (1 คอลัมน์ใน SELECT = 1 การ์ด
      ชื่อหลัง AS = ข้อความใต้ตัวเลข) แล้วลบ return {...} ชุดล่างสุดทิ้ง
    ★ การ์ด "คิดเพิ่มเอง" 2 ใบ: ตั้งชื่อการ์ดใหม่ แล้วเขียน SQL เอง
    ★ ผลรวมเงินใช้ IFNULL(SUM(...), 0) — ถ้ายังไม่มีข้อมูล SUM จะได้ NULL"""
    # ---- ตัวอย่างเมื่อเขียน SQL แล้ว (เอา # ข้างหน้าออก แล้วเติมให้ครบทุกการ์ด) ----
    # sql = """SELECT
    #            (SELECT COUNT(*) FROM ...) AS 'สมาชิก',
    #            (SELECT ...)               AS 'คลาส',
    #            ...
    #          """
    # return run_query(sql)[0]      ← [0] = เอาแถวแรก (ผลมีแถวเดียว) ได้เป็น dict

    # TODO: ระหว่างที่ยังไม่ได้เขียน SQL คืนค่า None ให้การ์ดแสดง "—" รอไว้
    return {
        "สมาชิก":         None,   # (SELECT COUNT(*) FROM member)
        "คลาส":           None,   # นับคลาสทั้งหมด
        "เทรนเนอร์":      None,   # นับเทรนเนอร์ทั้งหมด
        "การจอง":         None,   # นับเฉพาะการจองที่ status = 'booked'
        "คิดเพิ่มเอง 1":  None,   # ตั้งชื่อการ์ดใหม่ + เขียน SQL เอง
        "คิดเพิ่มเอง 2":  None,   # ตั้งชื่อการ์ดใหม่ + เขียน SQL เอง
    }

def report_popular_classes():
    """📈 คลาสยอดนิยม (Most Booked)
    คำใบ้: JOIN booking→gym_class, GROUP BY class, COUNT, ORDER BY DESC, LIMIT 5"""
    # TODO: เขียน SQL รายงานนี้ (เขียน JOIN แบบ explicit INNER JOIN ... ON ...)
    _todo("report_popular_classes")

def report_trainers_above_avg():
    """🏅 เทรนเนอร์ที่มีผู้จองมากกว่าค่าเฉลี่ย (Above Average)
    คำใบ้: JOIN booking→gym_class→trainer, GROUP BY trainer, HAVING COUNT(*) > (subquery AVG)"""
    # TODO: เขียน SQL รายงานนี้ (เขียน JOIN แบบ explicit INNER JOIN ... ON ...)
    _todo("report_trainers_above_avg")

def report_class_equipment():
    """🧰 อุปกรณ์ที่ใช้ในแต่ละคลาส (Join 3 Tables)
    คำใบ้: JOIN class_equipment→gym_class, class_equipment→equipment"""
    # TODO: เขียน SQL รายงานนี้ (เขียน JOIN แบบ explicit INNER JOIN ... ON ...)
    _todo("report_class_equipment")

# ============================================================
#  รายการรายงานที่แสดงบนหน้า /report  (เรียงตามลำดับที่แสดง)
#  ★ วิธีเพิ่มรายงานใหม่ (ไม่ต้องแก้ไฟล์อื่น):
#    1) เขียนฟังก์ชัน report_xxx() ด้านบน ให้ return run_query(sql)
#    2) เพิ่ม 1 บรรทัดในรายการนี้:  ("ชื่อใน-url", "หัวข้อที่แสดง", ชื่อฟังก์ชัน)
#  ★ รายการนี้ต้องอยู่ท้ายไฟล์ (หลังฟังก์ชันทั้งหมด) ไม่งั้น Python หาชื่อฟังก์ชันไม่เจอ
#  ★ ห้ามตั้งชื่อ url ว่า "summary" (ใช้แล้วสำหรับการ์ดสรุป)
# ============================================================
REPORTS = [
    ("popular-classes", "📈 คลาสยอดนิยม (Most Booked)",                            report_popular_classes),
    ("top-trainers",    "🏅 เทรนเนอร์ที่มีผู้จองมากกว่าค่าเฉลี่ย (Above Average)", report_trainers_above_avg),
    ("class-equipment", "🧰 อุปกรณ์ที่ใช้ในแต่ละคลาส (Join 3 Tables)",             report_class_equipment),
    # ("my-report", "📋 รายงานของฉัน", report_my_report),   ← ตัวอย่างการเพิ่มรายงานที่ 4
]
