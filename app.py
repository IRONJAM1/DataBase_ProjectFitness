# ============================================================
#  app.py — เว็บแอป Flask (ทำให้เสร็จแล้ว ★ ปกติไม่ต้องแก้)
#  รัน:  python app.py  แล้วเปิด http://127.0.0.1:5000
#  ★ เพิ่มรายงานใหม่ไม่ต้องแก้ไฟล์นี้ — ไปเพิ่มที่ REPORTS ท้าย db.py
# ============================================================
from datetime import date, datetime
from flask import Flask, request, jsonify, render_template
from flask.json.provider import DefaultJSONProvider
import db


class JSONProvider(DefaultJSONProvider):
    """- ส่งวันที่เป็นรูปแบบ YYYY-MM-DD ให้ช่อง <input type="date"> ในฟอร์มอ่านได้
       - ไม่เรียงชื่อคอลัมน์ใหม่ → หัวตารางเรียงตามลำดับใน SELECT"""
    sort_keys = False

    @staticmethod
    def default(o):
        if isinstance(o, (date, datetime)):
            return o.isoformat()
        return DefaultJSONProvider.default(o)


app = Flask(__name__)
app.json = JSONProvider(app)


def safe(fn, *args, **kwargs):
    try:
        return jsonify({"ok": True, "data": fn(*args, **kwargs)})
    except NotImplementedError as e:
        return jsonify({"ok": False, "todo": True, "error": str(e)}), 501
    except ValueError as e:
        # ข้อผิดพลาดที่ db.py ตั้งใจแจ้งผู้ใช้ เช่น raise ValueError("คลาสนี้เต็มแล้ว")
        return jsonify({"ok": False, "error": str(e)}), 400
    except Exception as e:
        return jsonify({"ok": False, "error": f"{type(e).__name__}: {e}"}), 500


@app.route("/")
def page_home():
    return render_template("index.html")

@app.route("/report")
def page_report():
    return render_template("report.html")


# ---- แพ็กเกจ ----
@app.route("/api/packages", methods=["GET"])
def packages_list():
    return safe(db.list_packages)


# ---- สมาชิก ----
@app.route("/api/members", methods=["GET"])
def members_list():
    filters = {k: v for k, v in request.args.items() if v}
    return safe(db.search_members, filters)

@app.route("/api/members/<int:_id>", methods=["GET"])
def member_get(_id):
    return safe(db.get_member, _id)

@app.route("/api/members", methods=["POST"])
def member_create():
    return safe(db.create_member, request.json)

@app.route("/api/members/<int:_id>", methods=["PUT"])
def member_update(_id):
    return safe(db.update_member, _id, request.json)

@app.route("/api/members/<int:_id>", methods=["DELETE"])
def member_delete(_id):
    return safe(db.delete_member, _id)

# ---- คลาสเรียน ----
@app.route("/api/classes", methods=["GET"])
def classes_list():
    filters = {k: v for k, v in request.args.items() if v}
    return safe(db.search_classes, filters)

@app.route("/api/classes/<int:_id>", methods=["GET"])
def class_get(_id):
    return safe(db.get_class, _id)

@app.route("/api/classes", methods=["POST"])
def class_create():
    return safe(db.create_class, request.json)

@app.route("/api/classes/<int:_id>", methods=["PUT"])
def class_update(_id):
    return safe(db.update_class, _id, request.json)

@app.route("/api/classes/<int:_id>", methods=["DELETE"])
def class_delete(_id):
    return safe(db.delete_class, _id)

# ---- เทรนเนอร์ ----
@app.route("/api/trainers", methods=["GET"])
def trainers_list():
    filters = {k: v for k, v in request.args.items() if v}
    return safe(db.search_trainers, filters)

@app.route("/api/trainers/<int:_id>", methods=["GET"])
def trainer_get(_id):
    return safe(db.get_trainer, _id)

@app.route("/api/trainers", methods=["POST"])
def trainer_create():
    return safe(db.create_trainer, request.json)

@app.route("/api/trainers/<int:_id>", methods=["PUT"])
def trainer_update(_id):
    return safe(db.update_trainer, _id, request.json)

@app.route("/api/trainers/<int:_id>", methods=["DELETE"])
def trainer_delete(_id):
    return safe(db.delete_trainer, _id)

# ---- อุปกรณ์ ----
@app.route("/api/equipment", methods=["GET"])
def equipment_list():
    filters = {k: v for k, v in request.args.items() if v}
    return safe(db.search_equipment, filters)

@app.route("/api/equipment/<int:_id>", methods=["GET"])
def equipment_get(_id):
    return safe(db.get_equipment, _id)

@app.route("/api/equipment", methods=["POST"])
def equipment_create():
    return safe(db.create_equipment, request.json)

@app.route("/api/equipment/<int:_id>", methods=["PUT"])
def equipment_update(_id):
    return safe(db.update_equipment, _id, request.json)

@app.route("/api/equipment/<int:_id>", methods=["DELETE"])
def equipment_delete(_id):
    return safe(db.delete_equipment, _id)

@app.route("/api/zones", methods=["GET"])
def zones_list():
    return safe(db.list_zones)

# ---- การยืมอุปกรณ์ (class_equipment) ----
@app.route("/api/class_equipment", methods=["GET"])
def class_equipment_list():
    filters = {k: v for k, v in request.args.items() if v}
    return safe(db.search_class_equipment, filters)

@app.route("/api/class_equipment/<int:_id>", methods=["GET"])
def class_equipment_get(_id):
    return safe(db.get_class_equipment, _id)

@app.route("/api/class_equipment", methods=["POST"])
def class_equipment_create():
    return safe(db.create_class_equipment, request.json)

@app.route("/api/class_equipment/<int:_id>", methods=["PUT"])
def class_equipment_update(_id):
    return safe(db.update_class_equipment, _id, request.json)

@app.route("/api/class_equipment/<int:_id>", methods=["DELETE"])
def class_equipment_delete(_id):
    return safe(db.delete_class_equipment, _id)

# ---- การจอง ----
@app.route("/api/bookings", methods=["GET"])
def bookings_list():
    filters = {k: v for k, v in request.args.items() if v}
    return safe(db.search_bookings, filters)

@app.route("/api/bookings/<int:_id>", methods=["GET"])
def booking_get(_id):
    return safe(db.get_booking, _id)

@app.route("/api/bookings", methods=["POST"])
def booking_create():
    return safe(db.create_booking, request.json)

@app.route("/api/bookings/<int:_id>", methods=["PUT"])
def booking_update(_id):
    return safe(db.update_booking, _id, request.json)

@app.route("/api/bookings/<int:_id>", methods=["DELETE"])
def booking_delete(_id):
    return safe(db.delete_booking, _id)
@app.route("/api/ClassName", methods=["GET"])
def ClassName_list():
    return safe(db.list_ClassName)

# ---- รายงาน ----
@app.route("/api/reports/summary")
def report_summary():
    return safe(db.report_summary)

@app.route("/api/reports")
def report_list():
    """รายชื่อรายงานทั้งหมด (อ่านจาก db.REPORTS) ให้หน้าเว็บสร้างกล่องรายงาน"""
    return jsonify({"ok": True, "data": [{"key": k, "title": t} for k, t, _ in db.REPORTS]})

@app.route("/api/reports/<key>")
def report_run(key):
    """รันรายงานตามชื่อ เช่น /api/reports/overdue"""
    for k, _, fn in db.REPORTS:
        if k == key:
            return safe(fn)
    return jsonify({"ok": False, "error": f"ไม่พบรายงาน '{key}' ใน db.REPORTS"}), 404


if __name__ == "__main__":
    app.run(debug=True, port=5000)
