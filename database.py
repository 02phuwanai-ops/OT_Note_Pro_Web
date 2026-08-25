"""
=========================================
OT Note Pro v1.0 - Falcon
Database (MySQL / Aiven)
=========================================
"""
import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()


# ==========================================
# Connect
# ==========================================

def connect():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 10981)),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        ssl_disabled=False,
        ssl_verify_identity=False
    )


# ==========================================
# Initialize Database
# ==========================================

def init_db():
    print("กำลังอัปเดตโครงสร้างตาราง...")
    conn = connect()
    cur = conn.cursor()

    # 1. ตาราง users
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        employee_id VARCHAR(100) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        role VARCHAR(50) DEFAULT 'technician',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    # 2. ตาราง ot_records
    cur.execute("""
    CREATE TABLE IF NOT EXISTS ot_records (
        id INT AUTO_INCREMENT PRIMARY KEY,
        employee_id INT,
        ticket VARCHAR(255),
        circuit VARCHAR(255),
        fault_date VARCHAR(100),
        start_time VARCHAR(20),
        finish_time VARCHAR(20),
        hours DECIMAL(5,2),
        description TEXT,
        owner VARCHAR(100),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("อัปเดตโครงสร้างตารางเรียบร้อยแล้ว!")


def create_user_table():
    init_db()


# ==========================================
# Users
# ==========================================

def register_user(employee_id, password):
    import bcrypt

    conn = connect()
    cur = conn.cursor()

    hashed_password = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    try:
        cur.execute("""
        INSERT INTO users(
            employee_id,
            password,
            role
        )
        VALUES(%s,%s,%s)
        """, (
            employee_id,
            hashed_password,
            "technician"
        ))
        conn.commit()
        return True
    except Exception as e:
        print("Register Error:", e)
        return False
    finally:
        cur.close()
        conn.close()


def login_user(employee_id, password):
    import bcrypt

    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    SELECT password, role
    FROM users
    WHERE employee_id=%s
    """, (employee_id,))

    user = cur.fetchone()
    cur.close()
    conn.close()

    if not user:
        return None

    stored_password = user[0]

    # bcrypt password check
    if stored_password.startswith("$2"):
        try:
            if bcrypt.checkpw(password.encode("utf-8"), stored_password.encode("utf-8")):
                return (user[1],)
        except Exception:
            return None
    else:
        # plain text check
        if password == stored_password:
            return (user[1],)

    return None


# ==========================================
# Save OT
# ==========================================

def save_ot(ticket, circuit, fault_date, start_time, finish_time, hours, description, owner):
    conn = connect()
    cur = conn.cursor()

    try:
        cur.execute("""
        INSERT INTO ot_records(
            ticket,
            circuit,
            fault_date,
            start_time,
            finish_time,
            hours,
            description,
            owner
        )
        VALUES(%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            ticket,
            circuit,
            fault_date,
            start_time,
            finish_time,
            hours,
            description,
            owner
        ))
        conn.commit()
        return True
    except mysql.connector.Error as e:
        print("MYSQL ERROR:", e)
        return False
    finally:
        cur.close()
        conn.close()


# ==========================================
# Update OT
# ==========================================

def update_ot(ticket, start_time, finish_time, hours, description, owner):
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    UPDATE ot_records
    SET
        start_time=%s,
        finish_time=%s,
        hours=%s,
        description=%s
    WHERE ticket=%s
    AND owner=%s
    """, (
        start_time,
        finish_time,
        hours,
        description,
        ticket,
        owner
    ))

    conn.commit()
    updated = cur.rowcount
    cur.close()
    conn.close()
    return updated > 0


# ==========================================
# Delete OT
# ==========================================

def delete_ot(record_id):
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM ot_records
        WHERE id=%s
    """, (record_id,))

    conn.commit()
    cur.close()
    conn.close()


# ==========================================
# Recent Records
# ==========================================

def get_recent(owner, limit=20):
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    SELECT
        ticket,
        circuit,
        fault_date,
        start_time,
        finish_time,
        hours,
        description,
        id
    FROM ot_records
    WHERE owner=%s
    ORDER BY id DESC
    LIMIT %s
    """, (owner, limit))

    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def get_total_hours(owner):
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        SELECT IFNULL(SUM(hours),0)
        FROM ot_records
        WHERE owner=%s
    """, (owner,))

    total = cur.fetchone()[0]
    cur.close()
    conn.close()
    return float(total)


# ==========================================
# All Records
# ==========================================

def get_all_records():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    SELECT
        ticket,
        circuit,
        fault_date,
        start_time,
        finish_time,
        hours,
        description,
        id
    FROM ot_records
    ORDER BY id DESC
    """)

    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


# ==========================================
# Search Ticket
# ==========================================

def search_ticket(keyword):
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
    SELECT
        ticket,
        circuit,
        fault_date,
        start_time,
        finish_time,
        hours,
        description,
        id
    FROM ot_records
    WHERE ticket LIKE %s
    ORDER BY id DESC
    """, (f"%{keyword}%",))

    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


# ==========================================
# Clear Database
# ==========================================

def clear_database():
    conn = connect()
    cur = conn.cursor()

    cur.execute("DELETE FROM ot_records")
    conn.commit()
    cur.close()
    conn.close()


# ==========================================
# Get Users
# ==========================================

def get_users():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            employee_id,
            role
        FROM users
        ORDER BY employee_id
    """)

    rows = cur.fetchall()
    cur.close()
    conn.close()

    result = []
    for row in rows:
        result.append({
            "employee_id": row[0],
            "role": row[1]
        })
    return result


# ==========================================
# Delete User
# ==========================================

def delete_user(employee_id):
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM users
        WHERE employee_id=%s
    """, (employee_id,))

    conn.commit()
    deleted = cur.rowcount
    cur.close()
    conn.close()
    return deleted > 0


# ==========================================
# Reset Password
# ==========================================

def reset_password(employee_id, new_password):
    import bcrypt

    conn = connect()
    cur = conn.cursor()

    hashed_password = bcrypt.hashpw(
        new_password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    cur.execute("""
        UPDATE users
        SET password = %s
        WHERE employee_id = %s
    """, (hashed_password, employee_id))

    conn.commit()
    updated = cur.rowcount
    cur.close()
    conn.close()
    return updated > 0


# ==========================================
# Admin Helper Functions
# ==========================================

def ensure_admin():
    conn = connect()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE users
            SET role = 'admin'
            WHERE employee_id = 'admin'
        """)
        conn.commit()
        print(" [SYSTEM] Admin role updated successfully.")
    except Exception as e:
        print(" [SYSTEM] Admin update error:", e)
    finally:
        cur.close()
        conn.close()


def fix_admin_account():
    import bcrypt
    conn = connect()
    cur = conn.cursor()
    try:
        # เข้ารหัส 123456
        hashed = bcrypt.hashpw("123456".encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        
        # เช็คก่อนว่ามี user ชื่อ admin หรือยัง
        cur.execute("SELECT id FROM users WHERE employee_id = 'admin'")
        exists = cur.fetchone()
        
        if exists:
            # ถ้ามีแล้ว ให้ อัปเดตรหัส และ สิทธิ์
            cur.execute("""
                UPDATE users 
                SET password = %s, role = 'admin' 
                WHERE employee_id = 'admin'
            """, (hashed,))
            print(" [SYSTEM] Admin password reset to '123456' & Role updated to 'admin'")
        else:
            # ถ้ายังไม่มี ให้ สร้างบัญชี admin ใหม่เลย
            cur.execute("""
                INSERT INTO users (employee_id, password, role)
                VALUES (%s, %s, %s)
            """, ('admin', hashed, 'admin'))
            print(" [SYSTEM] Admin account CREATED with password '123456'")
            
        conn.commit()
    except Exception as e:
        print(" [SYSTEM] Error fixing admin:", e)
    finally:
        cur.close()
        conn.close()