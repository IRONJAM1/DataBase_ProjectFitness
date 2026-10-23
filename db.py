# ============================================================
#  db.py — ชั้นติดต่อฐานข้อมูล  ★★★ นิสิตเขียน SQL ในไฟล์นี้ ★★★
#  มองหาคำว่า  # TODO  ทุกฟังก์ชัน — ใช้ %s เป็น placeholder เสมอ (กัน SQL injection)
# ============================================================
import math
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


def get_package(package_id):
    """ดึงข้อมูลแพ็กเกจเดี่ยวตาม package_id"""
    sql = "SELECT package_id, package_name, price, duration_months FROM package WHERE package_id = %s"
    rows = run_query(sql, (package_id,))
    return rows[0] if rows else None


def calculate_package_end_date(start_date, duration_months):
    """คำนวณวันหมดอายุตามระยะเวลาเดือนจริงของแพ็กเกจ (start_date + duration_months - 1 วัน)"""
    sql = "SELECT DATE_SUB(DATE_ADD(%s, INTERVAL %s MONTH), INTERVAL 1 DAY) AS end_date"
    rows = run_query(sql, (start_date, duration_months))
    return rows[0]["end_date"] if rows else None


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


def add_point(member_id, points=10):
    """เพิ่มคะแนนสะสม (total_point) ให้กับสมาชิกตาม member_id"""
    sql = """UPDATE member
             SET total_point = total_point + %s
             WHERE member_id = %s"""
    return run_command(sql, (points, member_id))


def create_member(data):
    ref_raw = blank_to_none(data.get("referred_by"))
    ref_id = int(ref_raw) if ref_raw is not None else None

    pkg_raw = blank_to_none(data.get("package_id"))
    pkg_id = int(pkg_raw) if pkg_raw is not None else None

    credit_input = float(data.get("credit") or 0)
    join_date = data["join_date"]
    start_date = blank_to_none(data.get("start_datepackage"))
    end_date = None

    # หากมีการเลือกแพ็กเกจ ให้ตรวจสอบเครดิต คำนวณหักเงิน และคำนวณวันหมดอายุตามเดือนจริง
    if pkg_id:
        pkg = get_package(pkg_id)
        if not pkg:
            raise ValueError("ไม่พบแพ็กเกจที่เลือก")
        price = float(pkg["price"])
        if credit_input < price:
            raise ValueError(f"เครดิตไม่เพียงพอสำหรับสมัครแพ็กเกจ '{pkg['package_name']}' (ราคา {price:,.2f} บาท แต่มีเครดิตเพียง {credit_input:,.2f} บาท)")
        
        # หักค่าแพ็กเกจออกจากเครดิต
        credit_input -= price

        # หากไม่ได้ใส่วันเริ่มแพ็กเกจ ให้ใช้วันที่สมัคร (join_date) เป็นวันเริ่ม
        if not start_date:
            start_date = join_date

        # คำนวณวันหมดอายุตามระยะเวลาเดือนจริงของแพ็กเกจ (เช่น 1 เดือน, 12 เดือน)
        end_date = calculate_package_end_date(start_date, pkg["duration_months"])
    else:
        # ไม่ได้เลือกแพ็กเกจ
        start_date = None
        end_date = None

    sql = '''INSERT INTO member (name, gender, credit, join_date, package_id, start_datepackage, end_datepackage, referred_by)
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'''
    params = (data["name"], data["gender"], credit_input,
              join_date, pkg_id,
              start_date, end_date,
              ref_id)
    out = run_command(sql, params)
    
    # ถ้ามีผู้แนะนำ (ref_id ไม่ใช่ None และไม่ใช่ "") ให้เพิ่มคะแนนให้ผู้แนะนำ
    if ref_id:
        add_point(ref_id, 10)
        
    return out

def update_member(member_id, data):
    old_member = get_member(member_id)
    if not old_member:
        raise ValueError("ไม่พบข้อมูลสมาชิกที่ต้องการแก้ไข")

    ref_old_raw = blank_to_none(old_member.get("referred_by"))
    old_ref_id = int(ref_old_raw) if ref_old_raw is not None else None

    ref_new_raw = blank_to_none(data.get("referred_by"))
    new_ref_id = int(ref_new_raw) if ref_new_raw is not None else None

    old_pkg_raw = blank_to_none(old_member.get("package_id"))
    old_pkg_id = int(old_pkg_raw) if old_pkg_raw is not None else None

    new_pkg_raw = blank_to_none(data.get("package_id"))
    new_pkg_id = int(new_pkg_raw) if new_pkg_raw is not None else None

    credit_input = float(data.get("credit") or 0)
    current_points = int(old_member.get("total_point") or 0)
    join_date = data["join_date"]
    start_date = blank_to_none(data.get("start_datepackage"))
    end_date = None

    if new_pkg_id:
        pkg = get_package(new_pkg_id)
        if not pkg:
            raise ValueError("ไม่พบแพ็กเกจที่เลือก")
        
        # กรณีเปลี่ยนแพ็กเกจใหม่ (เดิมไม่มีแพ็กเกจ หรือเปลี่ยนเป็นแพ็กเกจอื่น)
        if new_pkg_id != old_pkg_id:
            raw_price = float(pkg["price"])
            
            # แต้มสะสมช่วยลดราคาแพ็กเกจ: แต้ม 1 แต้ม = 10 บาท (point * 10)
            discount = current_points * 10
            final_price = max(0.0, raw_price - discount)

            # คำนวณแต้มที่ใช้ไป และแต้มคงเหลือ
            if discount >= raw_price:
                # ส่วนลดจากแต้มครอบคลุมราคาแพ็กเกจทั้งหมด
                used_points = math.ceil(raw_price / 10)
                current_points -= used_points
            else:
                # ใช้แต้มทั้งหมดที่มีเพื่อลดราคา
                current_points = 0

            # ตรวจสอบว่าเครดิตเพียงพอกับราคาหลังหักส่วนลดหรือไม่
            if credit_input < final_price:
                raise ValueError(
                    f"เครดิตไม่เพียงพอสำหรับสมัครแพ็กเกจ '{pkg['package_name']}' "
                    f"(ราคาปกติ {raw_price:,.2f} บาท ใช้ {old_member.get('total_point', 0)} แต้มลดเหลือ {final_price:,.2f} บาท แต่มีเครดิตเพียง {credit_input:,.2f} บาท)"
                )
            credit_input -= final_price

            if not start_date:
                start_date = old_member.get("start_datepackage") or join_date

        # กรณีแพ็กเกจเดิม แต่ไม่ได้กรอกวันเริ่มมา ให้ใช้วันเริ่มเดิม
        if not start_date:
            start_date = old_member.get("start_datepackage") or join_date

        # คำนวณวันหมดอายุใหม่ตามวันเริ่มแพ็กเกจและระยะเวลาเดือนจริงเสมอ
        end_date = calculate_package_end_date(start_date, pkg["duration_months"])
    else:
        # ยกเลิกแพ็กเกจ
        start_date = None
        end_date = None

    sql = """UPDATE member
             SET name = %s, gender = %s, credit = %s, join_date = %s,
                 package_id = %s, start_datepackage = %s, end_datepackage = %s, referred_by = %s,
                 total_point = %s
             WHERE member_id = %s"""
    params = (data["name"], data["gender"], credit_input,
              join_date, new_pkg_id,
              start_date, end_date,
              new_ref_id, current_points, member_id)
    out = run_command(sql, params)

    # ตรวจสอบ: ถ้ามีคนแนะนำใหม่ และไม่ใช่คนเดิม จึงค่อยบวกแต้มเพิ่ม
    if new_ref_id and new_ref_id != old_ref_id:
        add_point(new_ref_id, 10)

    return out


def delete_member(member_id):
    return run_command("DELETE FROM member WHERE member_id = %s", (member_id,))

# ---------- คลาสเรียน (gym_class) ----------
def list_ClassName():
    """ดึงรายชื่อคลาสเรียนทั้งหมดที่ไม่ซ้ำกันสำหรับตัวเลือกใน Dropdown บนหน้าเว็บ"""
    sql = "SELECT DISTINCT name FROM gym_class ORDER BY name"
    return run_query(sql)


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
    if filters.get("classname"):
        sql += " and c.name like %s"
        params.append("%"+filters['classname']+"%")
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
    sql = '''insert into gym_class (name, trainer_id, package_id, room, detail_class, capacity, schedule_time, end_time)
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'''
    params = (data["name"], data["trainer_id"], blank_to_none(data.get("package_id")),
              data["room"], data["detail_class"], data["capacity"],
              data["schedule_time"], data["end_time"])
    return run_command(sql, params)


def update_class(class_id, data):
    sql = """update gym_class
             set name = %s, trainer_id = %s, package_id = %s, room = %s, detail_class = %s, capacity = %s, schedule_time = %s, end_time = %s
             where class_id = %s"""
    params = (data["name"], data["trainer_id"], blank_to_none(data.get("package_id")),
              data["room"], data["detail_class"], data["capacity"],
              data["schedule_time"], data["end_time"], class_id)
    return run_command(sql, params)


def delete_class(class_id):
   sql = "delete from gym_class where class_id = %s"
   return run_command(sql,(class_id,))

# ---------- เทรนเนอร์ (trainer) ----------
def search_trainers(filters):
    sql = """select trainer_id,
             name,
             specialty,
             phone
             from trainer
             where 1=1"""
    params = []
    if filters.get("name"):
        sql += " and name like %s"
        params.append("%"+filters['name']+"%")
    if filters.get("specialty"):
        sql += " and specialty like %s"
        params.append("%"+filters['specialty']+"%")
    sql += " order by trainer_id"
    return run_query(sql, params)


def get_trainer(trainer_id):
    sql = "select * from trainer where trainer_id = %s"
    rows = run_query(sql, (trainer_id,))
    return rows[0] if rows else None


def create_trainer(data):
    sql = ''' insert into trainer (name,specialty,phone)
                 VALUES (%s, %s, %s)'''
    params = (data["name"],data["specialty"],data["phone"])
    return run_command(sql, params)

def update_trainer(trainer_id, data):
    sql = """update trainer
                set name = %s,specialty = %s,phone = %s
                where trainer_id = %s"""
    return run_command(sql,(data["name"],data["specialty"],data["phone"],trainer_id))
   


def delete_trainer(trainer_id):
    sql = "delete from trainer where trainer_id = %s"
    return run_command(sql, (trainer_id,))


# ---------- อุปกรณ์ (equipment) ----------
def list_zones():
    """ดึงรายชื่อโซนทั้งหมดที่ไม่ซ้ำกัน (DISTINCT) สำหรับตัวเลือกใน Dropdown"""
    sql = "SELECT DISTINCT zone FROM equipment WHERE zone IS NOT NULL AND zone <> '' ORDER BY zone"
    return run_query(sql)


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
    sql = "select * from equipment where 1=1"
    params = []
    if filters.get("name"):
        sql += " and name like %s"
        params.append("%"+filters['name']+"%")
    if filters.get("zone"):
        sql += " and zone = %s"
        params.append(filters['zone'])
    if filters.get("status"):
        sql += " and status = %s"
        params.append(filters["status"])
    sql += " order by equip_id"
    return run_query(sql, params)


def get_equipment(equip_id):
    sql = "SELECT * FROM equipment WHERE equip_id = %s"
    rows = run_query(sql, (equip_id,))
    return rows[0] if rows else None
    # TODO: SELECT * FROM equipment WHERE equip_id = %s แล้วคืนแถวเดียว
    _todo("get_equipment")


def create_equipment(data):
    sql = "INSERT INTO equipment (name, zone, status, total_quantity) VALUES (%s, %s, %s, %s)"
    params = (data["name"], data["zone"], data.get("status", "ready"), data.get("total_quantity"))
    return run_command(sql, params)


def update_equipment(equip_id, data):
    sql = """update equipment
            set name = %s,zone = %s,status = %s,total_quantity = %s
            where equip_id = %s"""
    params = (data["name"], data["zone"], data["status"], data.get("total_quantity"), equip_id)
    return run_command(sql, params)
    
def delete_equipment(equip_id):
    sql = "delete from equipment where equip_id = %s"
    return run_command(sql, (equip_id,))


# ---------- การยืมอุปกรณ์ในคลาส (class_equipment) ----------
def check_equipment_available(equip_id, new_quantity, old_quantity=0):
    """ตรวจสอบว่าอุปกรณ์มีพอให้ยืมหรือไม่"""
    # 1. เช็คว่ามีอุปกรณ์นี้จริง และสถานะพร้อมใช้งานหรือไม่
    eq = run_query("SELECT name, status, total_quantity FROM equipment WHERE equip_id = %s", (equip_id,))
    if not eq:
        raise ValueError("ไม่พบอุปกรณ์นี้ในระบบ")
    
    if eq[0]["status"] != "ready":
        raise ValueError(f"อุปกรณ์ '{eq[0]['name']}' อยู่ในสถานะ {eq[0]['status']} (ไม่พร้อมใช้งาน)")
    
    total = eq[0]["total_quantity"]
    
    # 2. คำนวณจำนวนที่ถูกคลาสอื่นยืมไปแล้วทั้งหมด
    used_rows = run_query("SELECT IFNULL(SUM(quantity), 0) AS used FROM class_equipment WHERE equip_id = %s", (equip_id,))
    total_used = used_rows[0]["used"]
    
    # หักลบจำนวนเดิมของคลาสนี้ออกก่อน (กรณีแก้ไข)
    used_by_others = total_used - old_quantity
    available = total - used_by_others
    
    # 3. ถ้าขอยืมมากกว่าที่มีอยู่ ให้แจ้งเตือนทันที
    if new_quantity > available:
        raise ValueError(f"อุปกรณ์ '{eq[0]['name']}' มีไม่พอ! ยืมได้อีกสูงสุด {available} ชิ้น (มีทั้งหมด {total} ชิ้น, ถูกคลาสอื่นยืมอยู่ {used_by_others} ชิ้น)")


def search_class_equipment(filters):
    """ค้นหา อุปกรณ์ที่ใช้ในแต่ละคลาส (class_equipment)
    JOIN gym_class และ equipment เพื่อแสดงชื่อคลาสและชื่ออุปกรณ์
    สร้าง id เสมือนจาก (ce.class_id * 100000 + ce.equip_id) เพื่อใช้เป็น primary key สำหรับหน้าเว็บ
    """
    sql = """SELECT (ce.class_id * 100000 + ce.equip_id) AS id,
                    c.name AS 'คลาสเรียน',
                    e.name AS 'อุปกรณ์',
                    e.zone AS 'โซน',
                    ce.quantity AS 'จำนวนที่ใช้'
             FROM class_equipment ce
             INNER JOIN gym_class c ON ce.class_id = c.class_id
             INNER JOIN equipment e ON ce.equip_id = e.equip_id
             WHERE 1=1"""
    params = []
    if filters.get("class_id"):
        sql += " AND ce.class_id = %s"
        params.append(filters["class_id"])
    if filters.get("equip_id"):
        sql += " AND ce.equip_id = %s"
        params.append(filters["equip_id"])
    sql += " ORDER BY c.name, e.name"
    return run_query(sql, tuple(params))


def get_class_equipment(_id):
    """ดึงข้อมูลการใช้อุปกรณ์ 1 รายการตาม composite id (class_id * 100000 + equip_id)"""
    class_id = _id // 100000
    equip_id = _id % 100000
    sql = "SELECT class_id, equip_id, quantity FROM class_equipment WHERE class_id = %s AND equip_id = %s"
    rows = run_query(sql, (class_id, equip_id))
    return rows[0] if rows else None


def create_class_equipment(data):
    class_id = int(data["class_id"])
    equip_id = int(data["equip_id"])
    quantity = int(data.get("quantity") or 1)
    
    # ตรวจสอบว่าคลาสนี้มีอุปกรณ์นี้บันทึกอยู่แล้วหรือไม่ (ป้องกัน Duplicate Primary Key)
    existing = run_query(
        "SELECT quantity FROM class_equipment WHERE class_id = %s AND equip_id = %s",
        (class_id, equip_id)
    )
    if existing:
        raise ValueError(
            f"คลาสนี้มีการยืมอุปกรณ์ชนิดนี้อยู่แล้ว (บันทึกไว้แล้ว {existing[0]['quantity']} ชิ้น) "
            f"หากต้องการเปลี่ยนจำนวน กรุณากดปุ่ม 'แก้ไข' ที่รายการเดิมในตารางแทนครับ"
        )
    
    # ตรวจสอบสต็อกก่อนบันทึก
    check_equipment_available(equip_id, quantity)
    
    sql = "INSERT INTO class_equipment (class_id, equip_id, quantity) VALUES (%s, %s, %s)"
    params = (class_id, equip_id, quantity)
    return run_command(sql, params)


def update_class_equipment(_id, data):
    old_class_id = _id // 100000
    old_equip_id = _id % 100000
    new_class_id = int(data["class_id"])
    new_equip_id = int(data["equip_id"])
    new_quantity = int(data.get("quantity") or 1)
    
    # ถ้าเปลี่ยนคลาสหรืออุปกรณ์ไปเป็นคู่ที่มีอยู่แล้วในระบบ (ที่ไม่ใช่แถวเดิมของตัวเอง)
    if (new_class_id != old_class_id or new_equip_id != old_equip_id):
        existing = run_query(
            "SELECT quantity FROM class_equipment WHERE class_id = %s AND equip_id = %s",
            (new_class_id, new_equip_id)
        )
        if existing:
            raise ValueError("คลาสนี้มีอุปกรณ์ชนิดนี้บันทึกอยู่แล้วในระบบ ไม่สามารถเปลี่ยนไปซ้ำได้")
    
    # ดึงจำนวนเดิมที่คลาสนี้เคยยืมไว้
    old_row = get_class_equipment(_id)
    old_quantity = old_row["quantity"] if (old_row and old_equip_id == new_equip_id) else 0
    
    # ตรวจสอบสต็อกก่อนอัปเดต
    check_equipment_available(new_equip_id, new_quantity, old_quantity)
    
    sql = """UPDATE class_equipment
             SET class_id = %s, equip_id = %s, quantity = %s
             WHERE class_id = %s AND equip_id = %s"""
    params = (new_class_id, new_equip_id, new_quantity, old_class_id, old_equip_id)
    return run_command(sql, params)



def delete_class_equipment(_id):
    """ลบ การใช้อุปกรณ์ในคลาส"""
    class_id = _id // 100000
    equip_id = _id % 100000
    sql = "DELETE FROM class_equipment WHERE class_id = %s AND equip_id = %s"
    return run_command(sql, (class_id, equip_id))


# ---------- การจอง (booking) ----------
def list_ClassName():
    sql = "SELECT DISTINCT name FROM gym_class WHERE name IS NOT NULL AND name != '' ORDER BY name"
    return run_query(sql)
def search_bookings(filters):
    sql = """select 
                    b.booking_id,
                    m.name as 'Member',
                    c.name as 'Class',
                    b.book_date as 'Booking Date',
                    b.status as 'Status'
            from booking b
            join member m on b.member_id = m.member_id
            join gym_class c on b.class_id = c.class_id
            where 1=1"""
    params = []
    if filters.get("Membername"):
        sql += " and m.name like %s"
        params.append("%"+filters['Membername']+"%")
    if filters.get("classname"):
        sql += " and c.name like %s"
        params.append("%"+filters['classname']+"%")
    if filters.get("status"):
        sql += " and b.status = %s"
        params.append(filters["status"])
    sql += " order by b.booking_id"
    return run_query(sql, params)


def get_booking(booking_id):
    sql = "SELECT * FROM booking WHERE booking_id = %s"
    rows = run_query(sql, (booking_id,))
    return rows[0] if rows else None


def check_can_book(member_id, class_id, booking_id=None, book_date=None):
    """ตรวจเงื่อนไขก่อนบันทึกการจองตามวันเวลาจริงของคลาส — ถ้าไม่ผ่านให้ raise ValueError"""
    
    # -------------------------------------------------------------
    # 1. ดึงข้อมูลคลาสเรียนและสมาชิก
    # -------------------------------------------------------------
    class_rows = run_query(
        """SELECT class_id, name, capacity, schedule_time, end_time, package_id 
           FROM gym_class WHERE class_id = %s""", (class_id,)
    )
    if not class_rows:
        raise ValueError("ไม่พบคลาสเรียนนี้ในระบบ")
    c_info = class_rows[0]

    member_rows = run_query(
        """SELECT member_id, name, package_id, start_datepackage, end_datepackage 
           FROM member WHERE member_id = %s""", (member_id,)
    )
    if not member_rows:
        raise ValueError("ไม่พบข้อมูลสมาชิกในระบบ")
    m_info = member_rows[0]

    # -------------------------------------------------------------
    # 2. ตรวจสอบวันเวลา: การจองต้องไม่เลยเวลาที่คลาสเริ่มเรียน
    # -------------------------------------------------------------
    if book_date:
        book_dt_str = str(book_date).strip()
        sched_dt_str = str(c_info["schedule_time"]).strip()
        if book_dt_str > sched_dt_str:
            raise ValueError(
                f"ไม่สามารถจองได้ เนื่องจากเวลาที่จอง ({book_dt_str}) "
                f"เลยเวลาเริ่มคลาสเรียนแล้ว ({sched_dt_str})"
            )

    # -------------------------------------------------------------
    # 3. ตรวจสอบวันเวลา: แพ็กเกจของสมาชิกต้องครอบคลุมวันที่มีคลาสเรียน
    # -------------------------------------------------------------
    if not m_info.get("package_id"):
        raise ValueError("สมาชิกยังไม่มีแพ็กเกจ ไม่สามารถจองคลาสเรียนได้")

    class_date = str(c_info["schedule_time"])[:10]  # วันที่จัดคลาส (YYYY-MM-DD)
    start_pkg = str(m_info.get("start_datepackage") or "")[:10]
    end_pkg = str(m_info.get("end_datepackage") or "")[:10]

    if not start_pkg or not end_pkg:
        raise ValueError("ข้อมูลแพ็กเกจของสมาชิกไม่สมบูรณ์ (ไม่พบวันเริ่มหรือวันหมดอายุ)")

    if class_date < start_pkg:
        raise ValueError(
            f"ไม่สามารถจองได้ เนื่องจากคลาสนี้จัดวันที่ {class_date} "
            f"แต่แพ็กเกจของท่านจะเริ่มใช้งานวันที่ {start_pkg}"
        )
    if class_date > end_pkg:
        raise ValueError(
            f"ไม่สามารถจองได้ เนื่องจากแพ็กเกจของท่านหมดอายุวันที่ {end_pkg} "
            f"ก่อนวันที่มีคลาสเรียน ({class_date})"
        )

    # -------------------------------------------------------------
    # 4. ตรวจสอบวันเวลา: เวลาเรียนต้องไม่ชนกับคลาสอื่นที่สมาชิกจองไว้แล้ว
    # -------------------------------------------------------------
    sql_conflict = """
        SELECT c.name, c.schedule_time, c.end_time 
        FROM booking b
        JOIN gym_class c ON b.class_id = c.class_id
        WHERE b.member_id = %s 
          AND b.status = 'booked' 
          AND b.booking_id <> %s
          AND c.schedule_time < %s 
          AND c.end_time > %s
        LIMIT 1
    """
    conflict_rows = run_query(
        sql_conflict, 
        (member_id, booking_id or 0, c_info["end_time"], c_info["schedule_time"])
    )
    if conflict_rows:
        conflict = conflict_rows[0]
        raise ValueError(
            f"ไม่สามารถจองได้ เนื่องจากเวลาเรียนชนกับคลาส '{conflict['name']}' "
            f"({conflict['schedule_time']} - {conflict['end_time']}) ที่ท่านได้จองไว้แล้ว"
        )

    # -------------------------------------------------------------
    # 5. ตรวจสอบการจองซ้ำ (สมาชิกคนเดิม ห้ามจองคลาสเดิมซ้ำ)
    # -------------------------------------------------------------
    sql_dup = """
        SELECT COUNT(*) AS dup_count 
        FROM booking 
        WHERE member_id = %s 
          AND class_id = %s 
          AND status = 'booked' 
          AND booking_id <> %s
    """
    dup_rows = run_query(sql_dup, (member_id, class_id, booking_id or 0))
    if dup_rows[0]["dup_count"] > 0:
        raise ValueError("สมาชิกท่านนี้ได้จองคลาสนี้ไว้แล้ว (ห้ามจองซ้ำ)")

    # -------------------------------------------------------------
    # 6. ตรวจสอบความจุคลาส (capacity) และคำนวณที่นั่งว่าง
    # -------------------------------------------------------------
    sql_booked = """
        SELECT COUNT(*) AS booked_count 
        FROM booking 
        WHERE class_id = %s 
          AND status = 'booked' 
          AND booking_id <> %s
    """
    booked_rows = run_query(sql_booked, (class_id, booking_id or 0))
    booked_count = booked_rows[0]["booked_count"]

    seats_left = c_info["capacity"] - booked_count
    if seats_left <= 0:
        raise ValueError(f"คลาส '{c_info['name']}' เต็มแล้ว (รับได้ {c_info['capacity']} คน จองแล้ว {booked_count} คน)")



def create_booking(data):
    # ถ้าสถานะเป็น 'booked' ให้ตรวจก่อนว่าจองได้ไหม
    if data.get("status") == "booked":
        check_can_book(data["member_id"], data["class_id"], booking_id=None, book_date=data.get("book_date"))

    sql = "INSERT INTO booking (member_id, class_id, book_date, status) VALUES (%s, %s, %s, %s)"
    params = (data["member_id"], data["class_id"], data["book_date"], data["status"])
    return run_command(sql, params)



def update_booking(booking_id, data):
    # ถ้าสถานะใหม่เป็น 'booked' ให้ตรวจเงื่อนไข (ส่ง booking_id ไปเพื่อไม่นับตัวเอง)
    if data.get("status") == "booked":
        check_can_book(data["member_id"], data["class_id"], booking_id=booking_id, book_date=data.get("book_date"))

    sql = """UPDATE booking 
             SET member_id = %s, class_id = %s, book_date = %s, status = %s 
             WHERE booking_id = %s"""
    params = (data["member_id"], data["class_id"], data["book_date"], data["status"], booking_id)
    return run_command(sql, params)

    

def delete_booking(booking_id):
    sql = "DELETE FROM booking WHERE booking_id = %s"
    return run_command(sql, (booking_id,))



# ============================================================
#  REPORT (รายงาน — ใช้ JOIN + GROUP BY + subquery)
#  ★ ชื่อคอลัมน์ใน SELECT จะกลายเป็นหัวตารางบนเว็บ — ใช้ AS 'ชื่อภาษาไทย' ได้
# ============================================================
def report_summary():
    """ตัวเลขสรุปบนการ์ด dashboard — คืน dict {ชื่อการ์ด: ตัวเลข}  (1 คีย์ = 1 การ์ด)
    ดึงข้อมูลจากการ์ดทั้งหมดผ่าน view_report_summary"""
    sql = "SELECT * FROM view_report_summary"
    rows = run_query(sql)
    return rows[0] if rows else {}

def report_popular_classes():
    """📈 คลาสยอดนิยม (Most Booked)
    ดึงข้อมูลจาก view_popular_classes (JOIN booking→gym_class→trainer, GROUP BY class, COUNT, LIMIT 5)"""
    sql = "SELECT * FROM view_popular_classes"
    return run_query(sql)

def report_trainers_above_avg():
    """🏅 เทรนเนอร์ที่มีผู้จองมากกว่าค่าเฉลี่ย (Above Average)
    ดึงข้อมูลจาก view_trainers_above_avg (JOIN booking→gym_class→trainer, GROUP BY trainer, HAVING > AVG)"""
    sql = "SELECT * FROM view_trainers_above_avg"
    return run_query(sql)

def report_class_equipment():
    """🧰 อุปกรณ์ที่ใช้ในแต่ละคลาส (Join 3 Tables)
    ดึงข้อมูลจาก view_class_equipment (JOIN class_equipment→gym_class, class_equipment→equipment)"""
    sql = "SELECT * FROM view_class_equipment"
    return run_query(sql)

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
