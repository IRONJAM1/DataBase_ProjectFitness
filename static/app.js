// ============================================================
//  app.js  —  ตรรกะหน้าเว็บ (ทำให้เสร็จแล้ว ★ นิสิตไม่ต้องแก้)
//  ปรับช่องค้นหา/ฟอร์มได้ที่ตัวแปร ENTITIES ด้านล่าง
// ============================================================
// ★ ตัวอย่าง dropdown ที่อ่านข้อมูลจากฐานข้อมูล: ฟอร์ม "การจอง" ช่อง class_id
//   แสดง name แต่ส่งค่าเป็น class_id (อ่านรายการจาก /api/classes)
//   ช่อง FK อื่น ๆ ทำแบบเดียวกันได้ — เปลี่ยน "type": "number" เป็น select + optionsFrom
const ENTITIES = {
  "members": {
    "label": "สมาชิก",
    "api": "/api/members",
    "idKey": "member_id",
    "search": [
      {
        "key": "name",
        "label": "ชื่อ",
        "type": "text"
      },
      {
        "key": "gender",
        "label": "เพศ",
        "type": "select",
        "options": [
          "",
          "M",
          "F"
        ]
      },
      {
        "key": "package_id",
        "label": "แพ็กเกจ",
        "type": "select",
        "optionsFrom": {
          "api": "/api/packages",
          "value": "package_id",
          "label": "package_name"
        }
      }
    ],
    "form": [
      {
        "key": "name",
        "label": "ชื่อ",
        "type": "text"
      },
      {
        "key": "gender",
        "label": "เพศ",
        "type": "select",
        "options": [
          "M",
          "F"
        ]
      },
      {
        "key": "join_date",
        "label": "วันที่สมัคร",
        "type": "date"
      },
      {
        "key": "package_id",
        "label": "แพ็กเกจ",
        "type": "select",
        "optionsFrom": {
          "api": "/api/packages",
          "value": "package_id",
          "label": "package_name"
        }
      },
      {
        "key": "credit",
        "label": "เครดิต",
        "type": "number"
      },
      {
        "key": "start_datepackage",
        "label": "วันเริ่มแพ็กเกจ",
        "type": "date"
      },
      {
        "key": "end_datepackage",
        "label": "วันหมดอายุแพ็กเกจ",
        "type": "date"
      },
      {
        "key": "referred_by",
        "label": "รหัสผู้แนะนำ",
        "type": "number"
      }
    ]
  },
  "classes": {
    "label": "คลาสเรียน",
    "api": "/api/classes",
    "idKey": "class_id",
    "search": [
      {
        "key": "name",
        "label": "ชื่อคลาส",
        "type": "text"
      },
      {
        "key": "room",
        "label": "ห้อง",
        "type": "text"
      }
    ],
    "form": [
      {
        "key": "name",
        "label": "ชื่อคลาส",
        "type": "text"
      },
      {
        "key": "trainer_id",
        "label": "รหัสเทรนเนอร์",
        "type": "number"
      },
      {
        "key": "package_id",
        "label": "แพ็กเกจ",
        "type": "select",
        "optionsFrom": {
          "api": "/api/packages",
          "value": "package_id",
          "label": "package_name"
        }
      },
      {
        "key": "room",
        "label": "ห้อง",
        "type": "text"
      },
      {
        "key": "detail_class",
        "label": "รายละเอียดคลาส",
        "type": "text"
      },
      {
        "key": "capacity",
        "label": "จำนวนรับ",
        "type": "number"
      },
      {
        "key": "schedule_time",
        "label": "เวลาเริ่ม",
        "type": "text"
      },
      {
        "key": "end_time",
        "label": "เวลาสิ้นสุด",
        "type": "text"
      }
    ]
  },
  "trainers": {
    "label": "เทรนเนอร์",
    "api": "/api/trainers",
    "idKey": "trainer_id",
    "search": [
      {
        "key": "name",
        "label": "ชื่อเทรนเนอร์",
        "type": "text"
      },
      {
        "key": "specialty",
        "label": "ความเชี่ยวชาญ",
        "type": "text"
      }
    ],
    "form": [
      {
        "key": "name",
        "label": "ชื่อเทรนเนอร์",
        "type": "text"
      },
      {
        "key": "specialty",
        "label": "ความเชี่ยวชาญ",
        "type": "text"
      },
      {
        "key": "phone",
        "label": "เบอร์โทรศัพท์",
        "type": "text"
      }
    ]
  },
  "equipment": {
    "label": "อุปกรณ์",
    "api": "/api/equipment",
    "idKey": "equip_id",
    "search": [
      {
        "key": "name",
        "label": "ชื่ออุปกรณ์",
        "type": "text"
      },
      {
        "key": "zone",
        "label": "โซน",
        "type": "text"
      },
      {
        "key": "status",
        "label": "สถานะ",
        "type": "select",
        "options": [
          "",
          "ready",
          "broken",
          "repair"
        ]
      }
    ],
    "form": [
      {
        "key": "name",
        "label": "ชื่ออุปกรณ์",
        "type": "text"
      },
      {
        "key": "zone",
        "label": "โซน",
        "type": "text"
      },
      {
        "key": "status",
        "label": "สถานะ",
        "type": "select",
        "options": [
          "ready",
          "broken",
          "repair"
        ]
      },
      {
        "key": "total_quantity",
        "label": "จำนวนทั้งหมด",
        "type": "number"
      }
    ]
  },
  "bookings": {
    "label": "การจอง",
    "api": "/api/bookings",
    "idKey": "booking_id",
    "search": [
      {
        "key": "member_id",
        "label": "รหัสสมาชิก",
        "type": "number"
      },
      {
        "key": "class_id",
        "label": "รหัสคลาส",
        "type": "number"
      },
      {
        "key": "status",
        "label": "สถานะ",
        "type": "select",
        "options": [
          "",
          "booked",
          "cancelled"
        ]
      }
    ],
    "form": [
      {
        "key": "member_id",
        "label": "รหัสสมาชิก",
        "type": "number"
      },
      {
        "key": "class_id",
        "label": "คลาส",
        "type": "select",
        "optionsFrom": {
          "api": "/api/classes",
          "value": "class_id",
          "label": "name"
        }
      },
      {
        "key": "book_date",
        "label": "วันที่จอง",
        "type": "date"
      },
      {
        "key": "status",
        "label": "สถานะ",
        "type": "select",
        "options": [
          "booked",
          "cancelled"
        ]
      }
    ]
  }
};

let current = Object.keys(ENTITIES)[0];
let editingId = null;
const $ = (s) => document.querySelector(s);
function setStatus(el, msg, cls = "") { el.className = "status " + cls; el.textContent = msg; }
async function api(url, opts) { const res = await fetch(url, opts); return res.json(); }

function fieldHtml(f, prefix, value = "") {
  if (f.type === "heading") return '<div class="form-section">' + f.label + '</div>';
  let input;
  if (f.type === "select") {
    // options เป็นข้อความ "a" หรือ {value, label} ก็ได้
    input = '<select id="' + prefix + f.key + '">' +
      f.options.map(o => {
        const v = typeof o === "object" ? o.value : o;
        const t = typeof o === "object" ? o.label : (o || "ทั้งหมด");
        return '<option value="' + v + '"' + (String(v) === String(value ?? "") ? " selected" : "") + '>' + t + '</option>';
      }).join("") + '</select>';
  } else { input = '<input id="' + prefix + f.key + '" type="' + f.type + '" value="' + (value ?? "") + '">'; }
  return '<div class="field"><label>' + f.label + '</label>' + input + '</div>';
}
// ช่อง select ที่มี optionsFrom → ดึงตัวเลือกจาก API (เช่น รายชื่อหมวดหมู่จากฐานข้อมูล)
async function loadOptions(fields, forSearch) {
  for (const f of fields.filter(f => f.optionsFrom)) {
    const src = f.optionsFrom, r = await api(src.api);
    f.options = r.ok ? (r.data || []).map(row => ({ value: row[src.value], label: row[src.label] }))
                     : [{ value: "", label: (r.todo ? "🚧 " : "⚠️ ") + r.error }];
    if (forSearch && r.ok) f.options.unshift({ value: "", label: "ทั้งหมด" });
  }
}
// ช่องในฟอร์มที่ใช้อยู่ตอนนี้ (ช่อง editOnly แสดงเฉพาะตอนแก้ไข)
function formFields() { return ENTITIES[current].form.filter(f => !f.editOnly || editingId !== null); }
async function buildSearch() {
  const cfg = ENTITIES[current];
  await loadOptions(cfg.search, true);
  if (cfg !== ENTITIES[current]) return;   // ผู้ใช้เปลี่ยนแท็บระหว่างรอ
  $("#searchTitle").textContent = cfg.label;
  $("#searchFields").innerHTML = cfg.search.map(f => fieldHtml(f, "s_")).join("");
}
async function doSearch() {
  const cfg = ENTITIES[current];
  const params = new URLSearchParams();
  cfg.search.forEach(f => { const v = $("#s_" + f.key).value; if (v) params.append(f.key, v); });
  setStatus($("#status"), "กำลังค้นหา...");
  renderTable(await api(cfg.api + "?" + params.toString()));
}
function renderTable(r) {
  const head = $("#tableHead"), body = $("#tableBody"), st = $("#status");
  head.innerHTML = ""; body.innerHTML = "";
  if (!r.ok) { setStatus(st, (r.todo ? "🚧 " : "⚠️ ") + r.error, r.todo ? "todo" : "err"); return; }
  const rows = r.data || [];
  if (rows.length === 0) { setStatus(st, "ไม่พบข้อมูล"); return; }
  setStatus(st, "พบ " + rows.length + " รายการ");
  const cols = Object.keys(rows[0]);
  head.innerHTML = cols.map(c => "<th>" + c + "</th>").join("") + "<th>จัดการ</th>";
  body.innerHTML = rows.map(row => {
    const id = row[ENTITIES[current].idKey];
    return "<tr>" + cols.map(c => "<td>" + (row[c] ?? "—") + "</td>").join("") +
      '<td><button class="btn sm" onclick="editRow(' + id + ')">แก้ไข</button> ' +
      '<button class="btn sm del" onclick="deleteRow(' + id + ')">ลบ</button></td></tr>';
  }).join("");
}
async function openForm(title, data = {}) {
  await loadOptions(formFields(), false);
  $("#modalTitle").textContent = title;
  $("#formFields").innerHTML = formFields().map(f => fieldHtml(f, "f_", data[f.key])).join("");
  $("#modal").classList.remove("hidden");
}
function collectForm() { const d = {}; formFields().filter(f => f.key).forEach(f => d[f.key] = $("#f_" + f.key).value); return d; }
async function editRow(id) {
  const cfg = ENTITIES[current];
  const r = await api(cfg.api + "/" + id);
  if (!r.ok) { alert((r.todo ? "🚧 " : "⚠️ ") + r.error); return; }
  editingId = id; openForm("แก้ไขข้อมูล", r.data);
}
async function deleteRow(id) {
  if (!confirm("ยืนยันการลบ?")) return;
  const r = await api(ENTITIES[current].api + "/" + id, { method: "DELETE" });
  if (!r.ok) { alert((r.todo ? "🚧 " : "⚠️ ") + r.error); return; }
  doSearch();
}
async function save() {
  const cfg = ENTITIES[current], data = collectForm();
  const opts = { method: editingId ? "PUT" : "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data) };
  const r = await api(editingId ? cfg.api + "/" + editingId : cfg.api, opts);
  if (!r.ok) { alert((r.todo ? "🚧 " : "⚠️ ") + r.error); return; }
  $("#modal").classList.add("hidden"); doSearch();
}
document.querySelectorAll(".tab").forEach(t => t.addEventListener("click", () => {
  document.querySelectorAll(".tab").forEach(x => x.classList.remove("active"));
  t.classList.add("active"); current = t.dataset.entity;
  buildSearch(); $("#tableHead").innerHTML = ""; $("#tableBody").innerHTML = "";
  setStatus($("#status"), 'กด "ค้นหา" เพื่อแสดงข้อมูล');
}));
$("#btnSearch").onclick = doSearch;
$("#btnClear").onclick = () => buildSearch();
$("#btnAdd").onclick = () => { editingId = null; openForm("เพิ่มข้อมูลใหม่"); };
$("#btnSave").onclick = save;
$("#btnCancel").onclick = () => $("#modal").classList.add("hidden");
buildSearch();
setStatus($("#status"), 'กด "ค้นหา" เพื่อแสดงข้อมูล');
