
-- 1. ตารางแพ็กเกจ (package) 
create table package (
    package_id int auto_increment primary key,
    package_name varchar(50) not null unique,
    price decimal(10,2) not null check (price >= 0),
    duration_months int not null check (duration_months > 0)
);

-- 2. ตารางสมาชิก (member)
-- มี Self-reference: referred_by ชี้กลับมาที่ member_id
create table member (
    member_id int auto_increment primary key,
    name varchar(100) not null,
    gender varchar(10) not null,
    credit decimal(10,2) not null default 0.00 check (credit >= 0),
    join_date date not null,
    package_id int null,
    start_datepackage date null,
    end_datepackage date null,
    total_point int not null default 0 check (total_point >= 0),
    referred_by int null, 
    constraint fk_member_referred_by foreign key (referred_by) 
        references member(member_id) 
        on delete set null on update cascade,
    constraint fk_member_package foreign key (package_id) 
        references package(package_id) 
        on delete set null on update cascade
);

-- 3. ตารางเทรนเนอร์ (trainer)
create table trainer (
    trainer_id int auto_increment primary key,
    name varchar(100) not null,
    specialty varchar(100) not null,
    phone varchar(20) not null
);


-- 4. ตารางคลาสเรียน (gym_class)
-- ความสัมพันธ์ 1:M จาก trainer และเชื่อม package_id จากตาราง package
create table gym_class (
    class_id int auto_increment primary key,
    trainer_id int not null,
    package_id int null, 
    name varchar(100) not null,
    room varchar(50) not null,
    detail_class varchar(255) not null,
    capacity int not null check (capacity > 0),
    schedule_time datetime not null,
    end_time datetime not null,
    constraint fk_class_trainer foreign key (trainer_id) 
        references trainer(trainer_id) 
        on delete restrict on update cascade,
    constraint fk_class_package foreign key (package_id) 
        references package(package_id) 
        on delete set null on update cascade,
    constraint chk_class_time check (end_time > schedule_time)
);


-- 5. ตารางอุปกรณ์ (equipment)
create table equipment (
    equip_id int auto_increment primary key,
    name varchar(100) not null,
    zone varchar(50) not null,
    status enum('ready', 'broken', 'repair') not null default 'ready',
    total_quantity int not null default 0 check (total_quantity >= 0)
);


-- 6. ตารางการจอง (booking) -> M:N ระหว่าง member และ gym_class
create table booking (
    booking_id int auto_increment primary key,
    member_id int not null,
    class_id int not null,
    book_date datetime not null default current_timestamp,
    status enum('booked', 'cancelled') not null default 'booked',
    constraint fk_booking_member foreign key (member_id) 
        references member(member_id) 
        on delete cascade on update cascade,
    constraint fk_booking_class foreign key (class_id) 
        references gym_class(class_id) 
        on delete restrict on update cascade
);


-- 7. ตารางอุปกรณ์ที่ใช้ในแต่ละคลาส (class_equipment) -> M:N: gym_class x equipment
create table class_equipment (
    class_id int not null,
    equip_id int not null,
    quantity int not null check (quantity > 0),
    primary key (class_id, equip_id),
    constraint fk_ce_class foreign key (class_id) 
        references gym_class(class_id) 
        on delete cascade on update cascade,
    constraint fk_ce_equipment foreign key (equip_id) 
        references equipment(equip_id) 
        on delete restrict on update cascade
);

-- ============================================================
-- 1. ข้อมูลตัวอย่าง: ตารางแพ็กเกจ (package) - 3 แพ็กเกจ
-- ============================================================
insert into package (package_id, package_name, price, duration_months) values
(1, 'Basic Monthly', 1200.00, 1),
(2, 'Premium Monthly', 2200.00, 1),
(3, 'VIP Annual', 21900.00, 12);

insert into member (member_id, name, gender, credit, join_date, package_id, start_datepackage, end_datepackage, total_point, referred_by) values
(1, 'สมชาย สายลุย', 'm', 500.00, '2026-01-10', 2, '2026-04-01', '2026-04-30', 120, null),
(2, 'วิภาดา รักสุขภาพ', 'f', 1200.00, '2026-01-15', 3, '2026-01-15', '2027-01-14', 270, null),
(3, 'กิตติศักดิ์ พลังกล้าม', 'm', 0.00, '2026-02-01', 1, '2026-04-01', '2026-04-30', 70, null),
(4, 'ชลธิชา หน้าใส', 'f', 200.00, '2026-02-10', 1, '2026-04-01', '2026-04-30', 60, 1),
(5, 'ธนกฤต ฟิตเปรี๊ยะ', 'm', 450.00, '2026-02-18', 2, '2026-04-01', '2026-04-30', 60, 1),
(6, 'ปรียาภรณ์ อ่อนช้อย', 'f', 0.00, '2026-03-01', 1, '2026-04-05', '2026-05-04', 20, 2),
(7, 'ณัฐพล คนขยัน', 'm', 800.00, '2026-03-05', 2, '2026-04-01', '2026-04-30', 10, 3),
(8, 'วรรณพร หุ่นดี', 'f', 150.00, '2026-03-12', 1, '2026-04-01', '2026-04-30', 20, 4),
(9, 'ศิริพร ยิ้มหวาน', 'f', 600.00, '2026-03-20', 2, '2026-04-01', '2026-04-30', 10, 2),
(10, 'อนันต์ ทรงพลัง', 'm', 0.00, '2026-04-01', 1, '2026-04-01', '2026-04-30', 20, 5);

-- ============================================================
-- 3. ข้อมูลตัวอย่าง: ตารางเทรนเนอร์ (trainer) - 5 คน
-- ============================================================
insert into trainer (trainer_id, name, specialty, phone) values
(1, 'โค้ชโต้ง (สมศักดิ์)', 'Weight Training & Bodybuilding', '081-111-2222'),
(2, 'ครูแอน (สิริพร)', 'Yoga & Pilates', '082-333-4444'),
(3, 'โค้ชเบิร์ด (อนุชา)', 'CrossFit & Cardio', '083-555-6666'),
(4, 'ครูนุ่น (ขนิษฐา)', 'Zumba & Dance', '084-777-8888'),
(5, 'โค้ชเอก (เอกลักษณ์)', 'Boxing & Martial Arts', '085-999-0000');

-- ============================================================
-- 4. ข้อมูลตัวอย่าง: ตารางคลาสเรียน (gym_class) - 7 คลาส
-- มี package_id ระบุสิทธิ์, detail_class อธิบายคลาส
-- และ end_time สอดคล้องกับ check (end_time > schedule_time)
-- ============================================================
insert into gym_class (class_id, trainer_id, package_id, name, room, detail_class, capacity, schedule_time, end_time) values
(1, 2, 1, 'Morning Yoga Flow', 'Studio A', 'ฝึกการหายใจและยืดเหยียดกล้ามเนื้อพื้นฐาน เหมาะสำหรับทุกระดับ', 15, '2026-04-10 08:00:00', '2026-04-10 09:00:00'),
(2, 5, 2, 'Muay Thai Cardio', 'Combat Zone', 'คาร์ดิโอผสมผสานศิลปะการต่อสู้มวยไทย เน้นเบิร์นไขมัน', 10, '2026-04-10 10:00:00', '2026-04-10 11:30:00'),
(3, 1, 1, 'Hypertrophy Upper Body', 'Weight Zone', 'เวทเทรนนิ่งเน้นเสริมสร้างกล้ามเนื้อส่วนบน อก หลัง แขน', 12, '2026-04-10 14:00:00', '2026-04-10 15:30:00'),
(4, 4, 1, 'Zumba Party Night', 'Studio B', 'เต้นออกกำลังกายสไตล์ละติน จังหวะสนุกสนาน เผาผลาญพลังงาน', 20, '2026-04-10 18:00:00', '2026-04-10 19:00:00'),
(5, 3, 2, 'HIIT Extreme Fat Burn', 'Func Turf', 'ออกกำลังกายความเข้มข้นสูง เร่งอัตราการเผาผลาญไขมันต่อเนื่อง', 12, '2026-04-11 09:00:00', '2026-04-11 10:00:00'),
(6, 2, 2, 'Pilates Reform & Mat', 'Studio A', 'พัฒนาแกนกลางลำตัว เพิ่มความยืดหยุ่นและปรับบุคลิกภาพ', 10, '2026-04-11 11:00:00', '2026-04-11 12:00:00'),
(7, 1, 1, 'Core & Six-Pack Blast', 'Weight Zone', 'เน้นบริหารกล้ามเนื้อหน้าท้องและแกนกลางลำตัวโดยเฉพาะ', 15, '2026-04-11 16:00:00', '2026-04-11 17:00:00');

-- ============================================================
-- 5. ข้อมูลตัวอย่าง: ตารางอุปกรณ์ (equipment) - 8 ชนิด
-- ใช้สถานะ enum('ready', 'broken', 'repair')
-- ============================================================
insert into equipment (equip_id, name, zone, status, total_quantity) values
(1, 'Yoga Mat (เสื่อโยคะ)', 'Studio A', 'ready', 30),
(2, 'Yoga Block (บล็อกโยคะ)', 'Studio A', 'ready', 40),
(3, 'Boxing Gloves (นวมชกมวย)', 'Combat Zone', 'ready', 20),
(4, 'Punching Pad (เป้าล่อเตะ/ต่อย)', 'Combat Zone', 'ready', 15),
(5, 'Adjustable Dumbbell (ดัมเบลปรับน้ำหนัก)', 'Weight Zone', 'ready', 24),
(6, 'Weight Bench (ม้าดัมเบล)', 'Weight Zone', 'repair', 8),
(7, 'Kettlebell 12kg (เคตเทิลเบล)', 'Func Turf', 'ready', 15),
(8, 'Battle Rope (เชือกสะบัด)', 'Func Turf', 'broken', 4);

-- ============================================================
-- 6. ข้อมูลตัวอย่าง: ตารางอุปกรณ์ที่ใช้ในแต่ละคลาส (class_equipment)
-- M:N: gym_class x equipment (ใช้ทดสอบ Report 3)
-- ============================================================
insert into class_equipment (class_id, equip_id, quantity) values
-- คลาส 1: Morning Yoga Flow ใช้เสื่อ 15 ผืน และ บล็อก 30 ชิ้น
(1, 1, 15),
(1, 2, 30),
-- คลาส 2: Muay Thai Cardio ใช้นวม 10 คู่ และ เป้าล่อ 10 ชิ้น
(2, 3, 10),
(2, 4, 10),
-- คลาส 3: Hypertrophy Upper Body ใช้ดัมเบล 12 คู่ และ ม้าซ้อม 6 ตัว
(3, 5, 12),
(3, 6, 6),
-- คลาส 5: HIIT Extreme Fat Burn ใช้เคตเทิลเบล 12 ลูก และ เชือก 2 เส้น
(5, 7, 12),
(5, 8, 2),
-- คลาส 6: Pilates Reform & Mat ใช้เสื่อโยคะ 10 ผืน
(6, 1, 10),
-- คลาส 7: Core & Six-Pack Blast ใช้เสื่อ 15 ผืน และ ดัมเบล 10 คู่
(7, 1, 15),
(7, 5, 10);

-- ============================================================
-- 7. ข้อมูลตัวอย่าง: ตารางการจอง (booking) - 18 รายการ
-- มีทั้งสถานะ 'booked' (16 รายการ) และ 'cancelled' (2 รายการ)
-- ออกแบบมาเพื่อทดสอบ Report 1 และ Report 2 โดยเฉพาะ:
-- ยอดจองสำเร็จ (booked) ต่อคลาส:
--   Class 1: 5 จอง | Class 2: 4 จอง | Class 4: 3 จอง | Class 3: 2 จอง | Class 7: 2 จอง
-- ยอดจองสำเร็จ (booked) ต่อเทรนเนอร์:
--   ครูแอน (trainer_id = 2): 5 จอง (Class 1)
--   โค้ชโต้ง (trainer_id = 1): 4 จอง (Class 3 มี 2 + Class 7 มี 2)
--   โค้ชเอก (trainer_id = 5): 4 จอง (Class 2)
--   ครูนุ่น (trainer_id = 4): 3 จอง (Class 4)
--   โค้ชเบิร์ด (trainer_id = 3): 0 จอง (Class 5 มี 2 แต่ถูก cancelled ทั้งหมด)
-- ค่าเฉลี่ยการจองสำเร็จต่อเทรนเนอร์ = (5 + 4 + 4 + 3 + 0) / 5 = 3.2
-- เทรนเนอร์ที่ได้ > ค่าเฉลี่ย (Above Avg): ครูแอน (5), โค้ชโต้ง (4), โค้ชเอก (4)
-- ============================================================
insert into booking (booking_id, member_id, class_id, book_date, status) values
-- คลาส 1 (Morning Yoga Flow): 5 จอง (booked ทั้งหมด)
(1, 1, 1, '2026-04-05 09:12:00', 'booked'),
(2, 2, 1, '2026-04-05 10:00:00', 'booked'),
(3, 4, 1, '2026-04-05 11:30:00', 'booked'),
(4, 6, 1, '2026-04-06 08:20:00', 'booked'),
(5, 8, 1, '2026-04-06 14:15:00', 'booked'),

-- คลาส 2 (Muay Thai Cardio): 4 จอง (booked ทั้งหมด)
(6, 1, 2, '2026-04-06 15:00:00', 'booked'),
(7, 3, 2, '2026-04-07 09:40:00', 'booked'),
(8, 5, 2, '2026-04-07 10:15:00', 'booked'),
(9, 7, 2, '2026-04-07 11:00:00', 'booked'),

-- คลาส 3 (Hypertrophy Upper Body): 2 จอง (booked ทั้งหมด)
(10, 3, 3, '2026-04-07 13:20:00', 'booked'),
(11, 10, 3, '2026-04-07 14:00:00', 'booked'),

-- คลาส 4 (Zumba Party Night): 3 จอง (booked ทั้งหมด)
(12, 2, 4, '2026-04-08 08:30:00', 'booked'),
(13, 6, 4, '2026-04-08 09:10:00', 'booked'),
(14, 9, 4, '2026-04-08 10:45:00', 'booked'),

-- คลาส 5 (HIIT Extreme Fat Burn): 2 รายการ (cancelled เพื่อทดสอบการตัดยอดคำนวณ)
(15, 5, 5, '2026-04-08 16:00:00', 'cancelled'),
(16, 7, 5, '2026-04-08 17:30:00', 'cancelled'),

-- คลาส 7 (Core & Six-Pack Blast): 2 จอง (booked ทั้งหมด)
(17, 8, 7, '2026-04-09 11:00:00', 'booked'),
(18, 10, 7, '2026-04-09 13:50:00', 'booked');